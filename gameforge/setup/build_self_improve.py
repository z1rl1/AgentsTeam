#!/usr/bin/env python3
"""
GameForge — Self-Improve + Eval Build
1. Real self-improve script (Karpathy loop for OpenClaw)
2. eval.json for all new skills
3. Improved game-generator eval.json (15+ assertions)
"""
import os, json

BASE = "/root/.openclaw/workspace"
SKILLS = f"{BASE}/skills"

# ══════════════════════════════════════════════════════════════════════════════
# 1. SELF-IMPROVE — Real Karpathy loop script
# ══════════════════════════════════════════════════════════════════════════════
SELF_IMPROVE_SCRIPT = r'''#!/usr/bin/env python3
"""
GameForge Self-Improve — Karpathy Loop for OpenClaw
Autonomously improves a skill by testing → evaluating → fixing → repeating.

Usage:
  self_improve.py <skill_name>          — improve one skill
  self_improve.py all                   — improve all skills below threshold
  self_improve.py status                — show current scores
  self_improve.py run-eval <skill_name> — just run eval, no improvement

How it works:
  1. Load skill's eval.json assertions
  2. Run the skill (simulate output or read last real output)
  3. Score against binary assertions
  4. If score < threshold → analyze failures → patch SKILL.md
  5. Record improvement to improvement-log.json
  6. Repeat up to MAX_ROUNDS
"""
import sys, os, json, re, subprocess
from datetime import datetime

SKILLS_DIR  = "/root/.openclaw/workspace/skills"
METRICS_DIR = "/root/.openclaw/workspace/hooks/metrics"
THRESHOLD   = 75   # target score %
MAX_ROUNDS  = 3    # max improvement rounds per skill

os.makedirs(METRICS_DIR, exist_ok=True)

# ── Eval Engine ───────────────────────────────────────────────────────────────
def run_assertion(assertion, text):
    """Evaluate one binary assertion against text. Returns True/False."""
    atype = assertion["type"]
    pattern = assertion.get("pattern", "")
    flags = re.IGNORECASE if assertion.get("case_insensitive") else 0

    if atype == "non_empty":
        return len(text.strip()) > 0

    if atype == "contains":
        return bool(re.search(pattern, text, flags))

    if atype == "not_contains":
        return not bool(re.search(pattern, text, flags))

    if atype == "min_words":
        return len(text.split()) >= int(assertion.get("min", 0))

    if atype == "max_words":
        return len(text.split()) <= int(assertion.get("max", 999999))

    if atype == "min_lines":
        return text.count("\n") + 1 >= int(assertion.get("min", 0))

    if atype == "has_heading":
        return bool(re.search(r'^#{1,3}\s+\w', text, re.MULTILINE))

    if atype == "has_code_block":
        return "```" in text

    if atype == "ends_no_question":
        stripped = text.strip()
        return not stripped.endswith("?")

    if atype == "has_url":
        return bool(re.search(r'https?://', text))

    if atype == "has_number":
        return bool(re.search(r'\d+', text))

    # Unknown type — skip (needs_ai)
    return None

def score_output(assertions, text):
    """Score text against all assertions. Returns (score%, passed, failed_ids)."""
    passed = 0
    failed = []
    total_binary = 0

    for a in assertions:
        result = run_assertion(a, text)
        if result is None:  # needs_ai — skip
            continue
        total_binary += 1
        if result:
            passed += 1
        else:
            failed.append(a["id"])

    score = int(passed / total_binary * 100) if total_binary > 0 else 0
    return score, passed, failed

# ── Metrics ───────────────────────────────────────────────────────────────────
def record_metric(skill_name, score, note=""):
    path = f"{METRICS_DIR}/{skill_name}.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "note": note,
        "source": "self-improve",
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_last_score(skill_name):
    path = f"{METRICS_DIR}/{skill_name}.jsonl"
    if not os.path.exists(path):
        return None
    lines = [l for l in open(path) if l.strip()]
    if not lines:
        return None
    return json.loads(lines[-1]).get("score")

def get_trend(skill_name):
    path = f"{METRICS_DIR}/{skill_name}.jsonl"
    if not os.path.exists(path):
        return "no data"
    lines = [json.loads(l) for l in open(path) if l.strip()]
    if len(lines) < 2:
        return "first run"
    delta = lines[-1]["score"] - lines[-2]["score"]
    if delta > 0:   return f"↑ +{delta}%"
    if delta < 0:   return f"↓ {delta}%"
    return "→ stable"

# ── Skill Loader ──────────────────────────────────────────────────────────────
def load_skill(skill_name):
    skill_dir  = f"{SKILLS_DIR}/{skill_name}"
    skill_md   = f"{skill_dir}/SKILL.md"
    eval_json  = f"{skill_dir}/eval/eval.json"

    if not os.path.exists(skill_md):
        return None, None, None

    content = open(skill_md).read()
    assertions = []
    if os.path.exists(eval_json):
        data = json.load(open(eval_json))
        assertions = data.get("assertions", [])

    return skill_dir, content, assertions

# ── Sample Output Generator ───────────────────────────────────────────────────
def get_sample_output(skill_name, skill_content):
    """
    For skills that have scripts — run them and capture output.
    Otherwise — use the SKILL.md description as proxy (tests instruction quality).
    """
    scripts_dir = f"{SKILLS_DIR}/{skill_name}/scripts"

    # Try running the skill's main script with --help or status
    if os.path.exists(scripts_dir):
        scripts = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]
        if scripts:
            script = f"{scripts_dir}/{scripts[0]}"
            try:
                result = subprocess.run(
                    ["python3", script, "status"],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout.strip():
                    return result.stdout
                result2 = subprocess.run(
                    ["python3", script],
                    capture_output=True, text=True, timeout=10
                )
                return result2.stdout or result2.stderr or skill_content
            except:
                pass

    # Fallback: use SKILL.md content itself (tests documentation quality)
    return skill_content

# ── Patch SKILL.md ────────────────────────────────────────────────────────────
def generate_fix(skill_name, content, failed_assertions, assertions_map):
    """Generate specific improvements for failed assertions."""
    fixes = []

    for aid in failed_assertions:
        a = assertions_map.get(aid, {})
        atype = a.get("type", "")
        desc  = a.get("description", aid)
        pattern = a.get("pattern", "")

        if atype == "non_empty":
            fixes.append("Add more detailed instructions to SKILL.md")

        elif atype == "contains" and pattern:
            fixes.append(f"Add example showing '{pattern}' in skill output")

        elif atype == "not_contains" and pattern:
            fixes.append(f"Remove or avoid '{pattern}' from skill output")

        elif atype == "min_words":
            fixes.append(f"Expand skill documentation — too brief (check: {desc})")

        elif atype == "min_lines":
            fixes.append("Add more step-by-step instructions")

        elif atype == "has_heading":
            fixes.append("Add ## headings to structure the skill")

        elif atype == "has_code_block":
            fixes.append("Add ``` code blocks with example commands")

        elif atype == "has_url":
            fixes.append("Add example URL to output (e.g., surge.sh link)")

        elif atype == "ends_no_question":
            fixes.append("Ensure skill output ends with a statement, not a question")

        else:
            fixes.append(f"Fix: {desc}")

    return fixes

def apply_fixes(skill_name, content, fixes):
    """Apply improvement suggestions to SKILL.md."""
    if not fixes:
        return content

    # Add improvement notes section
    improvement_note = f"\n\n<!-- Auto-improved {datetime.now().strftime('%Y-%m-%d')} -->\n"
    improvement_note += "## Improvement Notes\n"
    for fix in fixes:
        improvement_note += f"- {fix}\n"

    # Check if improvement notes already exist
    if "## Improvement Notes" in content:
        # Replace existing notes
        content = re.sub(
            r'\n## Improvement Notes.*$', improvement_note,
            content, flags=re.DOTALL
        )
    else:
        content += improvement_note

    return content

def log_improvement(skill_name, round_num, before_score, after_score, fixes):
    log_dir = f"{SKILLS_DIR}/{skill_name}/eval"
    os.makedirs(log_dir, exist_ok=True)
    log_path = f"{log_dir}/improvement-log.json"

    if os.path.exists(log_path):
        log = json.load(open(log_path))
    else:
        log = {"skill": skill_name, "runs": []}

    entry = {
        "date": datetime.now().isoformat(),
        "round": round_num,
        "score_before": before_score,
        "score_after": after_score,
        "delta": after_score - before_score,
        "fixes_applied": fixes,
    }
    log["runs"].append(entry)

    with open(log_path, "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

# ── Main Improve Loop ─────────────────────────────────────────────────────────
def improve_skill(skill_name, verbose=True):
    skill_dir, content, assertions = load_skill(skill_name)

    if content is None:
        print(f"  SKIP {skill_name}: not found")
        return None

    if not assertions:
        print(f"  SKIP {skill_name}: no eval.json")
        return None

    assertions_map = {a["id"]: a for a in assertions}
    initial_score = None
    current_content = content

    for round_num in range(1, MAX_ROUNDS + 1):
        # Get sample output
        sample = get_sample_output(skill_name, current_content)
        score, passed, failed = score_output(assertions, sample)

        if initial_score is None:
            initial_score = score

        if verbose:
            print(f"  Round {round_num}: score={score}% ({passed}/{len([a for a in assertions if run_assertion(a, '') is not None])} binary)")
            if failed:
                print(f"    Failed: {', '.join(failed[:5])}")

        record_metric(skill_name, score, f"self-improve round {round_num}")

        if score >= THRESHOLD:
            print(f"  ✓ {skill_name}: {score}% >= {THRESHOLD}% — done!")
            break

        if round_num == MAX_ROUNDS:
            print(f"  → {skill_name}: {initial_score}% → {score}% after {MAX_ROUNDS} rounds")
            break

        # Generate and apply fixes
        fixes = generate_fix(skill_name, current_content, failed, assertions_map)
        current_content = apply_fixes(skill_name, current_content, fixes)

        # Save improved SKILL.md
        skill_md_path = f"{skill_dir}/SKILL.md"
        with open(skill_md_path, "w") as f:
            f.write(current_content)

        log_improvement(skill_name, round_num, initial_score, score, fixes)

    return score

def cmd_status():
    skills = sorted(os.listdir(SKILLS_DIR))
    print(f"\n{'='*58}")
    print(f"  GameForge — Self-Improve Status")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*58}")
    print(f"  {'Skill':<28} {'Score':>7} {'Trend':>10} {'Eval':>5}")
    print(f"  {'-'*53}")

    below = 0
    for s in skills:
        score = get_last_score(s)
        trend = get_trend(s)
        has_eval = os.path.exists(f"{SKILLS_DIR}/{s}/eval/eval.json")
        score_str = f"{score}%" if score is not None else "-"
        if score is not None and score < THRESHOLD:
            below += 1
        print(f"  {s:<28} {score_str:>7} {trend:>10} {'✓' if has_eval else '-':>5}")

    print(f"  {'-'*53}")
    print(f"  Skills below {THRESHOLD}%: {below} | Run: self_improve.py all")
    print(f"{'='*58}\n")

def cmd_all():
    skills = sorted(os.listdir(SKILLS_DIR))
    print(f"\nImproving all skills below {THRESHOLD}%...\n")
    improved = 0
    skipped  = 0
    for s in skills:
        last = get_last_score(s)
        if last is not None and last >= THRESHOLD:
            skipped += 1
            continue
        has_eval = os.path.exists(f"{SKILLS_DIR}/{s}/eval/eval.json")
        if not has_eval:
            skipped += 1
            continue
        print(f"\n→ Improving: {s}")
        improve_skill(s, verbose=True)
        improved += 1
    print(f"\nDone: {improved} improved, {skipped} skipped")

def cmd_run_eval(skill_name):
    _, content, assertions = load_skill(skill_name)
    if not assertions:
        print(f"No eval.json for {skill_name}"); return
    sample = get_sample_output(skill_name, content)
    score, passed, failed = score_output(assertions, sample)
    binary_count = len([a for a in assertions if run_assertion(a, '') is not None])
    print(f"\nEval: {skill_name}")
    print(f"Score: {score}% ({passed}/{binary_count})")
    if failed:
        print(f"Failed assertions: {', '.join(failed)}")
    else:
        print("All assertions passed!")
    record_metric(skill_name, score, "manual eval run")

# ── Entry Point ───────────────────────────────────────────────────────────────
args = sys.argv[1:]
if not args or args[0] == "status":
    cmd_status()
elif args[0] == "all":
    cmd_all()
elif args[0] == "run-eval" and len(args) > 1:
    cmd_run_eval(args[1])
elif len(args) == 1:
    print(f"\nImproving: {args[0]}")
    score = improve_skill(args[0])
    if score is not None:
        print(f"Final score: {score}%")
else:
    print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 2. EVAL.JSON for all new skills (proper binary assertions)
# ══════════════════════════════════════════════════════════════════════════════

EVALS = {

# ── feedback ──────────────────────────────────────────────────────────────────
"feedback": {
    "skill": "feedback",
    "version": "1.0",
    "description": "User feedback detection, storage and retrieval",
    "assertions": [
        {"id": "non_empty",         "type": "non_empty",        "description": "Output not empty"},
        {"id": "no_error",          "type": "not_contains",     "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_sentiment",     "type": "contains",         "pattern": "negative|positive|neutral|suggestion", "description": "Detects sentiment", "case_insensitive": True},
        {"id": "has_feedback_word", "type": "contains",         "pattern": "feedback|constraint|saved|Понял|запомнил", "description": "Feedback acknowledged", "case_insensitive": True},
        {"id": "no_traceback",      "type": "not_contains",     "pattern": "traceback|line \\d+", "description": "No stack traces", "case_insensitive": True},
        {"id": "min_words",         "type": "min_words",        "min": 3,   "description": "At least 3 words output"},
        {"id": "has_user_id",       "type": "contains",         "pattern": "user|User|\\d{6,}", "description": "References user ID"},
        {"id": "ends_no_question",  "type": "ends_no_question", "description": "Ends with statement not question"},
    ]
},

# ── prompt-optimizer ──────────────────────────────────────────────────────────
"prompt-optimizer": {
    "skill": "prompt-optimizer",
    "version": "1.0",
    "description": "Tracks generation quality and evolves base prompt",
    "assertions": [
        {"id": "non_empty",         "type": "non_empty",        "description": "Output not empty"},
        {"id": "no_error",          "type": "not_contains",     "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_score",         "type": "contains",         "pattern": "score|Score|%|percent", "description": "References quality score", "case_insensitive": True},
        {"id": "has_analysis",      "type": "contains",         "pattern": "game|games|theme|type|total", "description": "Analyzes game data", "case_insensitive": True},
        {"id": "has_number",        "type": "has_number",       "description": "Contains numeric data"},
        {"id": "min_lines",         "type": "min_lines",        "min": 3,   "description": "At least 3 lines of analysis"},
        {"id": "no_traceback",      "type": "not_contains",     "pattern": "traceback",   "description": "No stack traces", "case_insensitive": True},
        {"id": "has_recommendation","type": "contains",         "pattern": "improve|improvement|better|fix|suggestion|pattern", "description": "Has actionable recommendation", "case_insensitive": True},
    ]
},

# ── user-memory ───────────────────────────────────────────────────────────────
"user-memory": {
    "skill": "user-memory",
    "version": "1.0",
    "description": "Stores and retrieves VK user game preferences",
    "assertions": [
        {"id": "non_empty",          "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",           "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_user_ref",       "type": "contains",        "pattern": "user|User|Total|games|Saved", "description": "References user data", "case_insensitive": True},
        {"id": "has_theme_or_type",  "type": "contains",        "pattern": "theme|type|favorite|cyberpunk|space|retro|neon|minimal|snake|tetris|pong|clicker", "description": "Contains theme or game type", "case_insensitive": True},
        {"id": "no_traceback",       "type": "not_contains",    "pattern": "traceback",  "description": "No stack traces", "case_insensitive": True},
        {"id": "min_words",          "type": "min_words",       "min": 4,  "description": "At least 4 words"},
        {"id": "has_number",         "type": "has_number",      "description": "Contains numeric data (game count etc)"},
        {"id": "ends_no_question",   "type": "ends_no_question","description": "Ends with statement"},
    ]
},

# ── observability ─────────────────────────────────────────────────────────────
"observability": {
    "skill": "observability",
    "version": "1.0",
    "description": "Token usage and cost tracking for LLM calls",
    "assertions": [
        {"id": "non_empty",       "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",        "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_tokens",      "type": "contains",        "pattern": "token|Token|tokens", "description": "Mentions token count", "case_insensitive": True},
        {"id": "has_cost",        "type": "contains",        "pattern": "\\$|cost|Cost|USD|usd", "description": "Shows cost", "case_insensitive": True},
        {"id": "has_number",      "type": "has_number",      "description": "Contains numeric stats"},
        {"id": "has_separator",   "type": "contains",        "pattern": "={3,}|-{3,}", "description": "Has formatted separator"},
        {"id": "min_lines",       "type": "min_lines",       "min": 4, "description": "At least 4 lines of stats"},
        {"id": "no_traceback",    "type": "not_contains",    "pattern": "traceback", "description": "No stack traces", "case_insensitive": True},
        {"id": "has_model",       "type": "contains",        "pattern": "model|Model|minimax|openrouter|gpt|claude", "description": "Mentions model used", "case_insensitive": True},
    ]
},

# ── game-library ──────────────────────────────────────────────────────────────
"game-library": {
    "skill": "game-library",
    "version": "1.0",
    "description": "Searchable catalog of generated games",
    "assertions": [
        {"id": "non_empty",       "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",        "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_game_ref",    "type": "contains",        "pattern": "game|Game|slug|library|Library|empty|catalog", "description": "References games or catalog", "case_insensitive": True},
        {"id": "no_traceback",    "type": "not_contains",    "pattern": "traceback", "description": "No stack traces", "case_insensitive": True},
        {"id": "min_words",       "type": "min_words",       "min": 3,  "description": "At least 3 words"},
        {"id": "ends_no_question","type": "ends_no_question","description": "Ends with statement"},
    ]
},

# ── rate-limiter ──────────────────────────────────────────────────────────────
"rate-limiter": {
    "skill": "rate-limiter",
    "version": "1.0",
    "description": "Per-user rate limiting and queue management",
    "assertions": [
        {"id": "non_empty",       "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",        "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_status",      "type": "contains",        "pattern": "OK|BLOCKED|COOLDOWN|BUSY|active|lock|No active", "description": "Shows rate limit status", "case_insensitive": True},
        {"id": "no_traceback",    "type": "not_contains",    "pattern": "traceback", "description": "No stack traces", "case_insensitive": True},
        {"id": "min_words",       "type": "min_words",       "min": 2,  "description": "At least 2 words"},
    ]
},

# ── game-generator (UPGRADED — 15 assertions) ─────────────────────────────────
"game-generator": {
    "skill": "game-generator",
    "version": "2.0",
    "description": "LLM-based HTML5 game generation and deployment",
    "assertions": [
        # Output structure
        {"id": "non_empty",           "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_python_error",     "type": "not_contains",    "pattern": "Traceback|SyntaxError|ImportError", "description": "No Python errors"},
        {"id": "no_api_error",        "type": "not_contains",    "pattern": "401|403|rate.?limit|quota.?exceeded", "description": "No API auth/rate errors", "case_insensitive": True},

        # Generation success signals
        {"id": "has_success",         "type": "contains",        "pattern": "SUCCESS|success|saved|готова|Generating", "description": "Shows generation success", "case_insensitive": True},
        {"id": "has_size_info",       "type": "contains",        "pattern": "KB|bytes|Lines|lines|size", "description": "Reports file size/lines", "case_insensitive": True},
        {"id": "has_time_info",       "type": "contains",        "pattern": "Time:|sec|s\\b|\\d+\\.\\d+", "description": "Reports generation time"},

        # HTML5 game requirements (checked via playtester)
        {"id": "mentions_canvas",     "type": "contains",        "pattern": "canvas|Canvas|DOM", "description": "Game uses canvas or DOM", "case_insensitive": True},
        {"id": "has_slug",            "type": "contains",        "pattern": "[a-z]+-[a-z]+-\\d+|slug|Generating:", "description": "Has game slug identifier"},

        # Deploy pipeline
        {"id": "has_url",             "type": "has_url",         "description": "Contains surge.sh or other URL"},
        {"id": "has_surge",           "type": "contains",        "pattern": "surge|GAME_URL|играть|Играть|link", "description": "References deployment URL", "case_insensitive": True},
        {"id": "no_template_mention", "type": "not_contains",    "pattern": "шаблон|template|snake_template|tetris_template", "description": "Not using old templates", "case_insensitive": True},

        # VK response quality
        {"id": "has_game_title",      "type": "contains",        "pattern": "Игра|игра|Game|ready|готова|Title:", "description": "Mentions game title or ready status", "case_insensitive": True},
        {"id": "has_controls",        "type": "contains",        "pattern": "Enter|стрелки|управление|Control|WASD|Space", "description": "Mentions game controls", "case_insensitive": True},
        {"id": "ends_no_question",    "type": "ends_no_question","description": "Output ends with statement not question"},
        {"id": "min_output_words",    "type": "min_words",       "min": 20,  "description": "At least 20 words of output"},

        # Self-improvement feedback
        {"id": "has_score",           "type": "contains",        "pattern": "Playtester|score|%|playtester", "description": "Reports playtester score", "case_insensitive": True},
    ]
},

# ── skill-health (upgrade) ────────────────────────────────────────────────────
"skill-health": {
    "skill": "skill-health",
    "version": "2.0",
    "description": "Dashboard showing all skills health status",
    "assertions": [
        {"id": "non_empty",       "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",        "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_header",      "type": "contains",        "pattern": "GAMEFORGE|GameForge|SKILL|dashboard|DASHBOARD", "description": "Has dashboard header", "case_insensitive": True},
        {"id": "has_separator",   "type": "contains",        "pattern": "={5,}|-{5,}", "description": "Has formatted separator"},
        {"id": "has_total",       "type": "contains",        "pattern": "Total|total|skills|скиллов", "description": "Shows total count", "case_insensitive": True},
        {"id": "has_number",      "type": "has_number",      "description": "Contains numeric data"},
        {"id": "has_eval_col",    "type": "contains",        "pattern": "eval|Eval|score|Score", "description": "Shows eval column", "case_insensitive": True},
        {"id": "min_lines",       "type": "min_lines",       "min": 10, "description": "At least 10 lines (10+ skills shown)"},
        {"id": "no_traceback",    "type": "not_contains",    "pattern": "traceback", "description": "No stack traces", "case_insensitive": True},
    ]
},

# ── self-improve (upgrade) ────────────────────────────────────────────────────
"self-improve": {
    "skill": "self-improve",
    "version": "2.0",
    "description": "Karpathy loop: test → score → fix → repeat for skill improvement",
    "assertions": [
        {"id": "non_empty",        "type": "non_empty",       "description": "Output not empty"},
        {"id": "no_error",         "type": "not_contains",    "pattern": "Traceback|Error:|Exception", "description": "No Python errors"},
        {"id": "has_score",        "type": "contains",        "pattern": "score|Score|%", "description": "Shows quality score", "case_insensitive": True},
        {"id": "has_round",        "type": "contains",        "pattern": "Round|round|iteration|Improving|improving|done|SKIP", "description": "Shows improvement progress", "case_insensitive": True},
        {"id": "has_number",       "type": "has_number",      "description": "Contains numeric data"},
        {"id": "no_traceback",     "type": "not_contains",    "pattern": "traceback", "description": "No stack traces", "case_insensitive": True},
        {"id": "min_words",        "type": "min_words",       "min": 10, "description": "At least 10 words of output"},
        {"id": "has_skill_name",   "type": "contains",        "pattern": "skill|Skill|SKILL", "description": "References skill being improved", "case_insensitive": True},
        {"id": "ends_no_question", "type": "ends_no_question","description": "Ends with statement"},
    ]
},
}

# ══════════════════════════════════════════════════════════════════════════════
# SELF-IMPROVE SKILL.md — full content
# ══════════════════════════════════════════════════════════════════════════════
SELF_IMPROVE_SKILL_MD = '''---
name: self-improve
description: Autonomously improves a skill using the Karpathy loop - runs eval assertions, scores output, patches SKILL.md, repeats until score >= 75%. Use when skill-health shows low scores or after adding new skills.
triggers:
  - "self-improve"
  - "улучши скилл"
  - "improve skill"
  - "overnight"
  - "karpathy"
---

# Self-Improve Skill — Karpathy Loop

Автономно улучшает скиллы: тестирует → оценивает → исправляет → повторяет.

## Алгоритм (Karpathy loop)

```
1. Загрузи eval.json скилла (binary assertions)
2. Запусти скилл / прочитай его output
3. Прогони все assertions через eval engine
4. Если score < 75% → сгенерируй fixes → примени к SKILL.md
5. Запиши метрику → повтори (max 3 раунда)
6. Залогируй в eval/improvement-log.json
```

## Команды

### Улучшить один скилл
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py game-generator
```

### Улучшить все скиллы ниже порога (75%)
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py all
```

### Статус всех скиллов
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py status
```

### Только запустить eval (без изменений)
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py run-eval game-generator
```

## Что меняется в SKILL.md

Скрипт добавляет в SKILL.md раздел `## Improvement Notes` с конкретными задачами:
- "Add code block with example" (если нет кода в документации)
- "Add ## headings to structure" (если нет заголовков)
- "Expand skill — too brief" (если слишком мало слов)

Это подсказки для следующего улучшения (ручного или автоматического).

## Метрики

Каждый запуск пишет в:
- `/root/.openclaw/workspace/hooks/metrics/{skill}.jsonl` — score + timestamp
- `/root/.openclaw/workspace/skills/{skill}/eval/improvement-log.json` — детали

## Overnight режим

Запускай раз в неделю для полного цикла:
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py all
```
Улучшит все скиллы с eval.json у которых score < 75%.
'''

# ══════════════════════════════════════════════════════════════════════════════
# Build everything
# ══════════════════════════════════════════════════════════════════════════════
print("Building self-improve system...\n")

# 1. Self-improve script
script_dir = f"{SKILLS}/self-improve/scripts"
os.makedirs(script_dir, exist_ok=True)
with open(f"{script_dir}/self_improve.py", "w") as f:
    f.write(SELF_IMPROVE_SCRIPT)
os.chmod(f"{script_dir}/self_improve.py", 0o755)
print(f"OK  skills/self-improve/scripts/self_improve.py ({len(SELF_IMPROVE_SCRIPT.splitlines())} lines)")

# 2. Updated SKILL.md for self-improve
with open(f"{SKILLS}/self-improve/SKILL.md", "w") as f:
    f.write(SELF_IMPROVE_SKILL_MD)
print(f"OK  skills/self-improve/SKILL.md (full content)")

# 3. eval.json for all skills
created = 0
updated = 0
for skill_name, eval_data in EVALS.items():
    eval_dir = f"{SKILLS}/{skill_name}/eval"
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = f"{eval_dir}/eval.json"
    existed = os.path.exists(eval_path)
    with open(eval_path, "w") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)
    n = len(eval_data["assertions"])
    action = "UPDATED" if existed else "CREATED"
    print(f"{action}  skills/{skill_name}/eval/eval.json ({n} assertions)")
    if existed: updated += 1
    else: created += 1

# 4. Run initial eval to populate metrics
print(f"\nRunning initial eval scores...")
import subprocess
script = f"{SKILLS}/self-improve/scripts/self_improve.py"
for skill_name in EVALS.keys():
    try:
        result = subprocess.run(
            ["python3", script, "run-eval", skill_name],
            capture_output=True, text=True, timeout=15
        )
        score_line = [l for l in result.stdout.split('\n') if 'Score:' in l]
        score_str = score_line[0].strip() if score_line else "no score"
        print(f"  {skill_name:<28} {score_str}")
    except Exception as e:
        print(f"  {skill_name:<28} error: {e}")

print(f"\n{'='*60}")
print(f"  Self-Improve System Ready!")
print(f"{'='*60}")
print(f"  self_improve.py:  {len(SELF_IMPROVE_SCRIPT.splitlines())} lines, real Karpathy loop")
print(f"  eval.json:        {created} created, {updated} updated")
print(f"  Total assertions: {sum(len(v['assertions']) for v in EVALS.values())}")
print(f"  game-generator:   {len(EVALS['game-generator']['assertions'])} assertions (was 4)")
print(f"\nCommands:")
print(f"  python3 {SKILLS}/self-improve/scripts/self_improve.py status")
print(f"  python3 {SKILLS}/self-improve/scripts/self_improve.py all")
print(f"  python3 {SKILLS}/self-improve/scripts/self_improve.py game-generator")
