#!/usr/bin/env python3
"""Injects localStorage leaderboard. Usage: python3 leaderboard.py <slug>"""
import sys, json, re, os
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

CSS = """<style id="gf-lb-style">
#gf-lb-btn{display:none;position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
  padding:10px 28px;font-size:16px;font-weight:bold;border:2px solid #f0c040;
  background:#1a1a2e;color:#f0c040;cursor:pointer;border-radius:6px;z-index:9998;letter-spacing:1px;}
#gf-lb-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);
  z-index:9999;align-items:center;justify-content:center;}
#gf-lb-overlay.gf-lb-vis{display:flex;}
#gf-lb-panel{background:#1a1a2e;border:2px solid #f0c040;border-radius:10px;
  padding:30px 40px;min-width:320px;max-width:480px;width:90vw;
  color:#fff;font-family:monospace,sans-serif;}
#gf-lb-panel h2{margin:0 0 18px;text-align:center;color:#f0c040;font-size:22px;letter-spacing:2px;}
#gf-lb-list{list-style:none;padding:0;margin:0 0 20px;}
#gf-lb-list li{display:flex;justify-content:space-between;padding:6px 0;
  border-bottom:1px solid rgba(255,255,255,0.1);font-size:15px;}
.gf-lb-rank{color:#f0c040;width:28px;}
.gf-lb-date{font-size:11px;color:rgba(255,255,255,0.4);}
#gf-lb-close{display:block;width:100%;padding:9px;background:#f0c040;color:#1a1a2e;
  border:none;border-radius:5px;font-size:15px;font-weight:bold;cursor:pointer;}
</style>"""

JS = """<script id="gf-lb-script">
(function(){
  var KEY='gf_lb_{slug}';
  function getScores(){try{return JSON.parse(localStorage.getItem(KEY)||'[]');}catch(e){return[];}}
  function saveScore(s){var a=getScores();a.push({score:s,date:new Date().toLocaleDateString()});
    a.sort(function(a,b){return b.score-a.score;});localStorage.setItem(KEY,JSON.stringify(a.slice(0,10)));}
  var btn=document.createElement('button');btn.id='gf-lb-btn';btn.textContent='Рекорды';
  document.body.appendChild(btn);
  var ov=document.createElement('div');ov.id='gf-lb-overlay';
  ov.innerHTML='<div id="gf-lb-panel"><h2>РЕКОРДЫ</h2><ul id="gf-lb-list"></ul><button id="gf-lb-close">Закрыть</button></div>';
  document.body.appendChild(ov);
  document.getElementById('gf-lb-close').onclick=function(){ov.classList.remove('gf-lb-vis');};
  ov.onclick=function(e){if(e.target===ov)ov.classList.remove('gf-lb-vis');};
  btn.onclick=function(){
    var s=getScores(),ul=document.getElementById('gf-lb-list');
    ul.innerHTML=s.length?s.map(function(x,i){return'<li><span class="gf-lb-rank">#'+(i+1)+'</span><span>'+x.score+'</span><span class="gf-lb-date">'+x.date+'</span></li>';}).join(''):'<li style="justify-content:center;color:rgba(255,255,255,.5)">Нет записей</li>';
    ov.classList.add('gf-lb-vis');
  };
  var _last=0;
  function tryScore(){
    var cands=['score','Score','SCORE','gameScore','points'],v;
    for(var i=0;i<cands.length;i++){v=window[cands[i]];if(typeof v==='number'&&v>0)return v;}
    return _last;
  }
  new MutationObserver(function(){
    var t=document.body.innerText.toLowerCase();
    if(t.includes('game over')||t.includes('you win')){
      var s=tryScore();if(s>0&&s!==_last){_last=s;saveScore(s);btn.style.display='block';}
    }
  }).observe(document.body,{childList:true,subtree:true,characterData:true});
  setInterval(function(){var s=tryScore();if(s>_last)_last=s;},500);
})();
</script>"""

def load_meta(d):
    p=d/'gameforge.json'
    try: return json.loads(p.read_text()) if p.exists() else {}
    except: return {}

def save_meta(d,m):
    (d/'gameforge.json').write_text(json.dumps(m,indent=2,ensure_ascii=False))

def main():
    if len(sys.argv)<2: print('Usage: leaderboard.py <slug>'); sys.exit(1)
    slug=sys.argv[1]; game_dir=GAMES_DIR/slug; idx=game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx} not found'); sys.exit(1)
    meta=load_meta(game_dir)
    if meta.get('leaderboard'): print('Already injected'); sys.exit(0)
    html=idx.read_text(encoding='utf-8')
    if 'gf-lb-script' in html: meta['leaderboard']=True; save_meta(game_dir,meta); sys.exit(0)
    inj=CSS+JS.replace('{slug}',slug)
    html=re.sub(r'</body>',inj+'\n</body>',html,1,re.I)
    idx.write_text(html,encoding='utf-8')
    meta['leaderboard']=True; save_meta(game_dir,meta)
    print(f'Leaderboard injected: {slug}')

if __name__=='__main__': main()
