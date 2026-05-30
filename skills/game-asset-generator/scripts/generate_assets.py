#!/usr/bin/env python3
"""Generates visual assets. Usage: python3 generate_assets.py <slug> [background|sprite|all]"""
import sys, os, json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'
IMG_API   = 'https://api.minimaxi.chat/v1/image_generation'

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

def gen_image(prompt, aspect='16:9'):
    key = os.environ.get('MINIMAX_API_KEY', '')
    if not key: raise RuntimeError('MINIMAX_API_KEY not set')
    payload = json.dumps({'model': os.environ.get('MINIMAX_IMAGE_MODEL','image-01'),
        'prompt': prompt, 'aspect_ratio': aspect, 'n': 1}).encode()
    req = urllib.request.Request(IMG_API, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    items = data.get('data') or []
    if not items: raise RuntimeError(f'No data: {data}')
    return items[0].get('url') or items[0].get('image_url') or ''

def download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'GameForge/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        path.write_bytes(r.read())

def build_prompt(asset_type, theme, desc, title):
    base = f'{theme} style, {title} game, 2D game asset'
    if asset_type == 'background':
        return f'2D game background scene, {desc}, {base}, wide landscape, no text, 16:9'
    return f'2D game sprite, {desc}, {base}, white background, centered'

def main():
    if len(sys.argv) < 2: print('Usage: generate_assets.py <slug> [background|sprite|all]'); sys.exit(1)
    slug = sys.argv[1]
    mode = sys.argv[2].lower() if len(sys.argv) > 2 else 'all'
    if mode not in ('background','sprite','all'): print(f'Unknown mode: {mode}'); sys.exit(1)
    game_dir = GAMES_DIR/slug
    if not game_dir.exists(): print(f'ERROR: {game_dir}'); sys.exit(1)
    assets_dir = game_dir/'assets'
    assets_dir.mkdir(exist_ok=True)
    gf_path = game_dir/'gameforge.json'
    meta = {}
    if gf_path.exists():
        try: meta = json.loads(gf_path.read_text())
        except Exception: pass
    title = meta.get('title', slug)
    theme = meta.get('theme', 'arcade')
    desc  = meta.get('description', f'a {theme} game')
    types = ['background','sprite'] if mode == 'all' else [mode]
    generated = {}
    for atype in types:
        print(f'Generating {atype}...')
        prompt = build_prompt(atype, theme, desc, title)
        aspect = '16:9' if atype == 'background' else '1:1'
        try:
            url = gen_image(prompt, aspect)
            if not url: raise RuntimeError('No URL returned')
            ext = 'png'
            for e in ('jpg','jpeg','png','webp'):
                if url.split('?')[0].lower().endswith(e): ext = e; break
            fname = f'{atype}_generated.{ext}'
            dest = assets_dir/fname
            download(url, dest)
            generated[atype] = fname
            print(f'  Saved: {dest}')
        except Exception as e:
            print(f'  ERROR {atype}: {e}')
    if generated:
        assets_meta = meta.get('assets', {})
        assets_meta.update(generated)
        assets_meta['generated_at'] = datetime.now(timezone.utc).isoformat()
        meta['assets'] = assets_meta
        gf_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        print(f'Done: {generated}')
    else:
        print('No assets generated'); sys.exit(1)

if __name__ == '__main__': main()
