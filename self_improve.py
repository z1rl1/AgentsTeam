#!/usr/bin/env python3
import sys, os, json, re, subprocess
from datetime import datetime

SKILLS_DIR  = '/root/.openclaw/workspace/skills'
METRICS_DIR = '/root/.openclaw/workspace/hooks/metrics'
THRESHOLD   = 75
MAX_ROUNDS  = 3
os.makedirs(METRICS_DIR, exist_ok=True)

def run_assertion(a, text):
    t  = a['type']
    p  = a.get('pattern', '')
    fl = re.IGNORECASE if a.get('case_insensitive') else 0
    if t == 'non_empty':        return len(text.strip()) > 0
    if t == 'contains':         return bool(re.search(p, text, fl))
    if t == 'not_contains':     return not bool(re.search(p, text, fl))
    if t == 'min_words':        return len(text.split()) >= int(a.get('min', 0))
    if t == 'max_words':        return len(text.split()) <= int(a.get('max', 999999))
    if t == 'min_lines':        return text.count('\n') + 1 >= int(a.get('min', 0))
    if t == 'has_heading':      return bool(re.search(r'^#{1,3}\s+\w', text, re.MULTILINE))
    if t == 'has_code_block':   return '```' in text
    if t == 'ends_no_question': return not text.strip().endswith('?')
    if t == 'has_url':          return bool(re.search(r'https?://', text))
    if t == 'has_number':       return bool(re.search(r'\d+', text))
    return None

def score_output(assertions, text):
    passed, failed, total = 0, [], 0
    for a in assertions:
        r = run_assertion(a, text)
        if r is None: continue
        total += 1
        if r: passed += 1
        else: failed.append(a['id'])
    score = int(passed / total * 100) if total > 0 else 0
    return score, passed, failed

def record_metric(skill, score, note=''):
    os.makedirs(METRICS_DIR, exist_ok=True)
    entry = {'timestamp': datetime.now().isoformat(), 'score': score, 'note': note, 'source': 'self-improve'}
    with open(os.path.join(METRICS_DIR, skill + '.jsonl'), 'a') as f:
        f.write(json.dumps(entry) + '\n')

def get_last_score(skill):
    p = os.path.join(METRICS_DIR, skill + '.jsonl')
    if not os.path.exists(p): return None
    lines = [l for l in open(p) if l.strip()]
    return json.loads(lines[-1]).get('score') if lines else None

def get_trend(skill):
    p = os.path.join(METRICS_DIR, skill + '.jsonl')
    if not os.path.exists(p): return 'no data'
    lines = [json.loads(l) for l in open(p) if l.strip()]
    if len(lines) < 2: return 'first run'
    d = lines[-1]['score'] - lines[-2]['score']
    return ('up +' + str(d) + '%') if d > 0 else ('down ' + str(d) + '%') if d < 0 else 'stable'

def load_skill(skill):
    sd = os.path.join(SKILLS_DIR, skill)
    sm = os.path.join(sd, 'SKILL.md')
    ej = os.path.join(sd, 'eval', 'eval.json')
    if not os.path.exists(sm): return None, None, None
    content = open(sm).read()
    assertions = json.load(open(ej)).get('assertions', []) if os.path.exists(ej) else []
    return sd, content, assertions

def get_sample(skill, content):
    sd = os.path.join(SKILLS_DIR, skill, 'scripts')
    if os.path.exists(sd):
        scripts = [f for f in os.listdir(sd) if f.endswith('.py')]
        if scripts:
            try:
                r = subprocess.run(['python3', os.path.join(sd, scripts[0]), 'status'],
                                   capture_output=True, text=True, timeout=10)
                if r.stdout.strip(): return r.stdout
                r2 = subprocess.run(['python3', os.path.join(sd, scripts[0])],
                                    capture_output=True, text=True, timeout=10)
                if r2.stdout.strip(): return r2.stdout
            except: pass
    return content

def generate_fixes(failed, amap):
    fixes = []
    for aid in failed:
        a = amap.get(aid, {})
        t = a.get('type', '')
        p = a.get('pattern', '')
        d = a.get('description', aid)
        if t == 'non_empty':         fixes.append('Add more content to SKILL.md')
        elif t == 'contains':        fixes.append('Add example output containing: ' + p[:40])
        elif t == 'not_contains':    fixes.append('Remove pattern from output: ' + p[:40])
        elif t == 'min_words':       fixes.append('Expand docs - too brief: ' + d)
        elif t == 'min_lines':       fixes.append('Add more step-by-step instructions')
        elif t == 'has_heading':     fixes.append('Add ## headings to structure skill')
        elif t == 'has_code_block':  fixes.append('Add ``` code blocks with examples')
        elif t == 'has_url':         fixes.append('Add example URL to output section')
        elif t == 'ends_no_question':fixes.append('End output with statement not question')
        else:                        fixes.append('Fix: ' + d)
    return fixes

def apply_fixes(skill, content, fixes):
    if not fixes: return content
    date_str = datetime.now().strftime('%Y-%m-%d')
    parts = ['', '', '<!-- Auto-improved ' + date_str + ' -->', '## Improvement Notes']
    parts += ['- ' + f for f in fixes]
    note = '\n'.join(parts) + '\n'
    if '## Improvement Notes' in content:
        idx = content.find('\n## Improvement Notes')
        if idx == -1: idx = content.find('## Improvement Notes')
        content = content[:idx]
    return content.rstrip() + note

def log_improvement(skill, rnd, before, after, fixes):
    log_dir = os.path.join(SKILLS_DIR, skill, 'eval')
    os.makedirs(log_dir, exist_ok=True)
    lp = os.path.join(log_dir, 'improvement-log.json')
    log = json.load(open(lp)) if os.path.exists(lp) else {'skill': skill, 'runs': []}
    log['runs'].append({'date': datetime.now().isoformat(), 'round': rnd,
                        'score_before': before, 'score_after': after,
                        'delta': after - before, 'fixes': fixes})
    json.dump(log, open(lp, 'w'), ensure_ascii=False, indent=2)

def improve_skill(skill, verbose=True):
    sd, content, assertions = load_skill(skill)
    if content is None:  print('  SKIP ' + skill + ': not found'); return None
    if not assertions:   print('  SKIP ' + skill + ': no eval.json'); return None
    amap = {a['id']: a for a in assertions}
    initial_score = None
    cur = content
    for rnd in range(1, MAX_ROUNDS + 1):
        sample = get_sample(skill, cur)
        score, passed, failed = score_output(assertions, sample)
        if initial_score is None: initial_score = score
        btotal = len([a for a in assertions if run_assertion(a, '') is not None])
        if verbose:
            print('  Round ' + str(rnd) + ': ' + str(score) + '% (' + str(passed) + '/' + str(btotal) + ')')
            if failed: print('    Failed: ' + ', '.join(failed[:5]))
        record_metric(skill, score, 'round ' + str(rnd))
        if score >= THRESHOLD:
            print('  OK ' + skill + ': ' + str(score) + '%  done!'); break
        if rnd == MAX_ROUNDS:
            print('  -> ' + skill + ': ' + str(initial_score) + '% -> ' + str(score) + '%'); break
        fixes = generate_fixes(failed, amap)
        cur = apply_fixes(skill, cur, fixes)
        open(os.path.join(sd, 'SKILL.md'), 'w').write(cur)
        log_improvement(skill, rnd, initial_score, score, fixes)
    return score

def cmd_status():
    skills = sorted(os.listdir(SKILLS_DIR))
    print('=' * 58)
    print('  GameForge — Skill Quality Dashboard')
    print('  ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print('=' * 58)
    print('  {:<28} {:>6} {:>12} {:>5}'.format('Skill', 'Score', 'Trend', 'Eval'))
    print('  ' + '-' * 53)
    below = 0
    for s in skills:
        score = get_last_score(s)
        trend = get_trend(s)
        has_eval = os.path.exists(os.path.join(SKILLS_DIR, s, 'eval', 'eval.json'))
        ss = (str(score) + '%') if score is not None else '-'
        if score is not None and score < THRESHOLD: below += 1
        print('  {:<28} {:>6} {:>12} {:>5}'.format(s, ss, trend, 'v' if has_eval else '-'))
    print('  ' + '-' * 53)
    print('  Skills below ' + str(THRESHOLD) + '%: ' + str(below))
    print('=' * 58)

def cmd_all():
    skills = sorted(os.listdir(SKILLS_DIR))
    print('\nImproving all skills below ' + str(THRESHOLD) + '%...\n')
    improved = skipped = 0
    for s in skills:
        has_eval = os.path.exists(os.path.join(SKILLS_DIR, s, 'eval', 'eval.json'))
        if not has_eval: skipped += 1; continue
        last = get_last_score(s)
        if last is not None and last >= THRESHOLD: skipped += 1; continue
        print('\n-> ' + s)
        improve_skill(s, verbose=True)
        improved += 1
    print('\nDone: ' + str(improved) + ' improved, ' + str(skipped) + ' skipped')

def cmd_run_eval(skill):
    _, content, assertions = load_skill(skill)
    if not assertions: print('No eval.json for ' + skill); return
    sample = get_sample(skill, content)
    score, passed, failed = score_output(assertions, sample)
    btotal = len([a for a in assertions if run_assertion(a, '') is not None])
    print('Eval: ' + skill + '  Score: ' + str(score) + '% (' + str(passed) + '/' + str(btotal) + ')')
    if failed: print('Failed: ' + ', '.join(failed))
    else: print('All passed!')
    record_metric(skill, score, 'manual eval')

args = sys.argv[1:]
if not args or args[0] == 'status':          cmd_status()
elif args[0] == 'all':                        cmd_all()
elif args[0] == 'run-eval' and len(args) > 1: cmd_run_eval(args[1])
elif len(args) == 1:
    print('Improving: ' + args[0])
    s = improve_skill(args[0])
    if s is not None: print('Final: ' + str(s) + '%')
else:
    print('Usage: self_improve.py <skill>|all|status|run-eval <skill>')
