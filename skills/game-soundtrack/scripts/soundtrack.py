#!/usr/bin/env python3
"""Generates background music via MiniMax. Usage: python3 soundtrack.py <slug>"""
import sys, os, json, re, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'

def load_env():
    p = WORKSPACE/'.env'
    if not p.exists(): return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ: os.environ[k] = v

load_env()

def api_post(url, body):
    key = os.environ.get('MINIMAX_API_KEY', '')
    if not key: raise RuntimeError('MINIMAX_API_KEY not set')
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def api_get(url):
    key = os.environ.get('MINIMAX_API_KEY', '')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {key}'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def inject_audio(html, mp3_path):
    js = f"""<script>
(function(){{
  var a=document.createElement('audio');
  a.id='__gf_soundtrack__';a.src='{mp3_path}';a.loop=true;a.volume=0.4;
  document.addEventListener('click',function s(){{a.play().catch(function(){{}});document.removeEventListener('click',s);}},{{once:true}});
  document.body.appendChild(a);
}})();
</script>"""
    if '__gf_soundtrack__' in html:
        html = re.sub(r'<script>[^<]*__gf_soundtrack__[^<]*(?:<[^/][^<]*)*</script>', js.strip(), html, flags=re.S)
    elif '</body>' in html:
        html = html.replace('</body>', js + '</body>')
    else:
        html += js
    return html

def main():
    if len(sys.argv) < 2: print('Usage: soundtrack.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    game_dir = GAMES_DIR/slug
    idx = game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    (game_dir/'assets').mkdir(exist_ok=True)
    gf_path = game_dir/'gameforge.json'
    meta = {}
    if gf_path.exists():
        try: meta = json.loads(gf_path.read_text())
        except Exception: pass
    theme = meta.get('theme') or meta.get('description', '') or slug
    prompt = f'Upbeat game background music for a {theme} HTML5 game, loopable, energetic instrumental'
    print(f'[soundtrack] Generating for {slug}...')
    try:
        resp = api_post('https://api.minimaxi.chat/v1/music_generation', {
            'model': 'music-2.6', 'lyrics': '[instrumental]', 'prompt': prompt,
            'refer_voice': False, 'refer_instrumental': False,
            'audio_setting': {'sample_rate': 44100, 'bitrate': 128000, 'format': 'mp3'}
        })
        print(f'  Response keys: {list(resp.keys())}')
        task_id = resp.get('task_id') or (resp.get('data') or {}).get('task_id')
        file_id = resp.get('file_id') or (resp.get('data') or {}).get('file_id')
        if task_id:
            print(f'  Polling task {task_id}...')
            for _ in range(30):
                r2 = api_get(f'https://api.minimaxi.chat/v1/music_generation?task_id={task_id}')
                status = r2.get('status') or (r2.get('data') or {}).get('status', '')
                print(f'  Status: {status}')
                if status.lower() in ('success','completed'):
                    file_id = (r2.get('data') or {}).get('file_id') or r2.get('file_id')
                    break
                if status.lower() in ('failed','error'):
                    raise RuntimeError(f'Music generation failed: {r2}')
                time.sleep(10)
        if not file_id: raise RuntimeError('No file_id obtained')
        r3 = api_get(f'https://api.minimaxi.chat/v1/files/retrieve?file_id={file_id}')
        url = (r3.get('file') or {}).get('download_url') or r3.get('download_url') or r3.get('url')
        if not url: raise RuntimeError(f'No URL: {r3}')
        mp3 = game_dir/'assets'/'music_generated.mp3'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=120) as r4:
            mp3.write_bytes(r4.read())
        print(f'  MP3 saved: {mp3}')
        html = idx.read_text(encoding='utf-8')
        idx.write_text(inject_audio(html, 'assets/music_generated.mp3'), encoding='utf-8')
        meta['has_soundtrack'] = True
        meta['soundtrack_generated_at'] = datetime.now(timezone.utc).isoformat()
        gf_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        print('[soundtrack] Done')
    except Exception as e:
        print(f'ERROR: {e}'); sys.exit(1)

if __name__ == '__main__': main()
