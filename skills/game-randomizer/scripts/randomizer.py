#!/usr/bin/env python3
"""Injects seeded PRNG + New Seed button. Usage: python3 randomizer.py <slug>"""
import sys, json, re
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

CSS = """<style id="gf-rng-style">
#gf-seed-lbl{position:fixed;bottom:12px;left:14px;z-index:9997;font-family:monospace;
  font-size:12px;color:rgba(255,255,255,.55);background:rgba(0,0,0,.45);
  padding:3px 9px;border-radius:4px;pointer-events:none;letter-spacing:1px;}
#gf-seed-btn{position:fixed;bottom:12px;right:14px;z-index:9997;padding:7px 16px;
  font-family:monospace;font-size:14px;background:rgba(20,20,40,.85);color:#f0c040;
  border:1.5px solid #f0c040;border-radius:6px;cursor:pointer;letter-spacing:1px;}
</style>"""

JS = """<script id="gf-rng-script">
(function(){
  var KEY='gf_seed_{slug}';
  function mulberry32(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
  function getSeed(){var v=localStorage.getItem(KEY);return v!==null?parseInt(v,10):newSeed();}
  function newSeed(){var s=Math.floor(Math.random()*2147483647);localStorage.setItem(KEY,String(s));return s;}
  var cur=getSeed();
  Math.random=mulberry32(cur);
  var lbl,btn;
  function buildUI(){
    lbl=document.createElement('div');lbl.id='gf-seed-lbl';lbl.textContent='Seed: '+cur;document.body.appendChild(lbl);
    btn=document.createElement('button');btn.id='gf-seed-btn';btn.textContent='🎲 New Seed';document.body.appendChild(btn);
    btn.onclick=function(){newSeed();window.location.reload();};
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',buildUI);}else{buildUI();}
})();
</script>"""

def load_meta(d):
    p=d/'gameforge.json'
    try: return json.loads(p.read_text()) if p.exists() else {}
    except: return {}

def save_meta(d,m):
    (d/'gameforge.json').write_text(json.dumps(m,indent=2,ensure_ascii=False))

def main():
    if len(sys.argv)<2: print('Usage: randomizer.py <slug>'); sys.exit(1)
    slug=sys.argv[1]; game_dir=GAMES_DIR/slug; idx=game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    meta=load_meta(game_dir)
    if meta.get('randomized'): print('Already injected'); sys.exit(0)
    html=idx.read_text(encoding='utf-8')
    if 'gf-rng-script' in html: meta['randomized']=True; save_meta(game_dir,meta); sys.exit(0)
    inj=CSS+JS.replace('{slug}',slug)
    # Inject before first <script> so Math.random is patched first
    m=re.search(r'<script[\s>]',html,re.I)
    pos=m.start() if m else len(html)
    html=html[:pos]+inj+'\n'+html[pos:]
    idx.write_text(html,encoding='utf-8')
    meta['randomized']=True; save_meta(game_dir,meta)
    print(f'Randomizer injected: {slug}')

if __name__=='__main__': main()
