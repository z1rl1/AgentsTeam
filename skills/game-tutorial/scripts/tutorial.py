#!/usr/bin/env python3
"""Injects tutorial overlay. Usage: python3 tutorial.py <slug>"""
import sys, json, re
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

DEFAULT_CONTROLS = "Стрелки / WASD — движение\nПробел — действие / выстрел\nEnter — старт / подтвердить"

CSS = """<style id="gf-tut-style">
#gf-tut-ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.82);
  z-index:99999;align-items:center;justify-content:center;font-family:monospace,sans-serif;}
#gf-tut-ov.gf-tut-vis{display:flex;}
#gf-tut-box{background:#1a1a2e;border:2px solid #f0c040;border-radius:12px;
  padding:36px 44px;max-width:520px;width:92vw;color:#fff;text-align:center;
  box-shadow:0 8px 40px rgba(0,0,0,.7);}
#gf-tut-box h2{color:#f0c040;font-size:24px;margin:0 0 18px;letter-spacing:2px;text-transform:uppercase;}
#gf-tut-ctrl{background:rgba(255,255,255,.05);border-radius:8px;padding:16px 20px;
  margin:0 0 24px;text-align:left;line-height:1.9;font-size:15px;white-space:pre-wrap;}
#gf-tut-btn{padding:11px 36px;background:#f0c040;color:#1a1a2e;border:none;
  border-radius:6px;font-size:16px;font-weight:bold;cursor:pointer;letter-spacing:1px;}
#gf-tut-hint{margin-top:12px;font-size:12px;color:rgba(255,255,255,.35);}
</style>"""

JS = """<script id="gf-tut-script">
(function(){
  var KEY='gf_tut_{slug}';
  if(localStorage.getItem(KEY)==='1')return;
  var CTRL={controls};
  var TITLE={title};
  var ov=document.createElement('div');ov.id='gf-tut-ov';
  ov.innerHTML='<div id="gf-tut-box"><h2>'+TITLE+' — Управление</h2><div id="gf-tut-ctrl">'+CTRL+'</div><button id="gf-tut-btn">Понял! ▶</button><div id="gf-tut-hint">или Пробел / Enter</div></div>';
  function close(){ov.classList.remove('gf-tut-vis');ov.style.display='none';localStorage.setItem(KEY,'1');
    setTimeout(function(){document.dispatchEvent(new KeyboardEvent('keydown',{key:' ',code:'Space',keyCode:32,bubbles:true}));},80);}
  document.addEventListener('DOMContentLoaded',function(){document.body.appendChild(ov);ov.classList.add('gf-tut-vis');document.getElementById('gf-tut-btn').onclick=close;});
  document.addEventListener('keydown',function(e){if(ov.classList.contains('gf-tut-vis')&&(e.code==='Space'||e.code==='Enter')){e.preventDefault();close();}});
})();
</script>"""

def load_meta(d):
    p=d/'gameforge.json'
    try: return json.loads(p.read_text()) if p.exists() else {}
    except: return {}

def save_meta(d,m):
    (d/'gameforge.json').write_text(json.dumps(m,indent=2,ensure_ascii=False))

def main():
    if len(sys.argv)<2: print('Usage: tutorial.py <slug>'); sys.exit(1)
    slug=sys.argv[1]; game_dir=GAMES_DIR/slug; idx=game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    meta=load_meta(game_dir)
    if meta.get('tutorial'): print('Already injected'); sys.exit(0)
    html=idx.read_text(encoding='utf-8')
    if 'gf-tut-script' in html: meta['tutorial']=True; save_meta(game_dir,meta); sys.exit(0)
    controls=meta.get('controls') or DEFAULT_CONTROLS
    if isinstance(controls,list): controls='\n'.join(str(c) for c in controls)
    title=meta.get('title',slug)
    inj=CSS+JS.replace('{slug}',slug).replace('{controls}',json.dumps(controls)).replace('{title}',json.dumps(title))
    html=re.sub(r'</body>',inj+'\n</body>',html,1,re.I)
    idx.write_text(html,encoding='utf-8')
    meta['tutorial']=True; save_meta(game_dir,meta)
    print(f'Tutorial injected: {slug}')

if __name__=='__main__': main()
