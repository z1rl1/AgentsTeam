#!/usr/bin/env python3
"""Injects achievement system. Usage: python3 achievements.py <slug>"""
import sys, json, re
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

CSS = """<style id="gf-ach-style">
#gf-ach-banner{display:none;position:fixed;top:24px;right:24px;z-index:99999;
  background:linear-gradient(135deg,#1a1a2e 80%,#2d2d5e);border:2px solid #f0c040;
  border-radius:10px;padding:14px 22px 14px 16px;min-width:260px;color:#fff;
  font-family:monospace,sans-serif;box-shadow:0 4px 24px rgba(0,0,0,.5);
  transform:translateX(120%);transition:transform .4s cubic-bezier(.22,.68,0,1.2);}
#gf-ach-banner.gf-ach-show{display:flex!important;transform:translateX(0);}
#gf-ach-banner.gf-ach-hide{transform:translateX(120%);}
.gf-ach-icon{font-size:28px;margin-right:12px;}
.gf-ach-body{display:flex;flex-direction:column;}
.gf-ach-title{font-size:11px;color:#f0c040;letter-spacing:2px;text-transform:uppercase;margin-bottom:3px;}
.gf-ach-name{font-size:16px;font-weight:bold;}
.gf-ach-desc{font-size:12px;color:rgba(255,255,255,.6);margin-top:2px;}
</style>"""

JS = """<script id="gf-ach-script">
(function(){
  var KEY='gf_ach_{slug}';
  var ACHS=[
    {id:'score1000',icon:'⭐',name:'Score 1000',desc:'Набери 1000 очков',check:function(s){return(s.score||0)>=1000;}},
    {id:'combo5',icon:'🔥',name:'Combo x5',desc:'Комбо из 5',check:function(s){return(s.combo||0)>=5;}},
    {id:'survive60',icon:'⏱️',name:'Survive 60s',desc:'60 секунд',check:function(s){return(s.time||0)>=60;}},
    {id:'first_blood',icon:'🩸',name:'First Blood',desc:'Первое убийство',check:function(s){return(s.kills||0)>=1;}},
    {id:'score5000',icon:'👑',name:'High Roller',desc:'5000 очков',check:function(s){return(s.score||0)>=5000;}},
  ];
  function unlocked(){try{return JSON.parse(localStorage.getItem(KEY)||'[]');}catch(e){return[];}}
  function markDone(id){var u=unlocked();if(u.indexOf(id)===-1){u.push(id);localStorage.setItem(KEY,JSON.stringify(u));}}
  var banner=document.createElement('div');banner.id='gf-ach-banner';
  banner.innerHTML='<span class="gf-ach-icon" id="gf-ai"></span><div class="gf-ach-body"><div class="gf-ach-title">Достижение!</div><div class="gf-ach-name" id="gf-an"></div><div class="gf-ach-desc" id="gf-ad"></div></div>';
  document.body.appendChild(banner);
  var _q=[],_busy=false;
  function show(a){_q.push(a);if(!_busy)next();}
  function next(){if(!_q.length){_busy=false;return;}_busy=true;var a=_q.shift();
    document.getElementById('gf-ai').textContent=a.icon;
    document.getElementById('gf-an').textContent=a.name;
    document.getElementById('gf-ad').textContent=a.desc;
    banner.classList.remove('gf-ach-hide');banner.classList.add('gf-ach-show');
    setTimeout(function(){banner.classList.add('gf-ach-hide');
      setTimeout(function(){banner.classList.remove('gf-ach-show','gf-ach-hide');banner.style.display='none';setTimeout(next,200);},450);},3000);}
  var _state={score:0,kills:0,combo:0,time:0},_t=Date.now();
  function sync(){
    var sv=['score','Score','SCORE','gameScore','points'],v;
    for(var i=0;i<sv.length;i++){v=window[sv[i]];if(typeof v==='number'){_state.score=v;break;}}
    var kv=['kills','killCount','enemiesKilled'];
    for(var i=0;i<kv.length;i++){v=window[kv[i]];if(typeof v==='number'){_state.kills=v;break;}}
    var cv=['combo','comboCount','multiplier'];
    for(var i=0;i<cv.length;i++){v=window[cv[i]];if(typeof v==='number'){_state.combo=v;break;}}
    _state.time=Math.floor((Date.now()-_t)/1000);
  }
  function check(){sync();var u=unlocked();
    ACHS.forEach(function(a){if(u.indexOf(a.id)===-1&&a.check(_state)){markDone(a.id);show(a);}});}
  setInterval(check,800);
})();
</script>"""

def load_meta(d):
    p=d/'gameforge.json'
    try: return json.loads(p.read_text()) if p.exists() else {}
    except: return {}

def save_meta(d,m):
    (d/'gameforge.json').write_text(json.dumps(m,indent=2,ensure_ascii=False))

def main():
    if len(sys.argv)<2: print('Usage: achievements.py <slug>'); sys.exit(1)
    slug=sys.argv[1]; game_dir=GAMES_DIR/slug; idx=game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    meta=load_meta(game_dir)
    if meta.get('achievements'): print('Already injected'); sys.exit(0)
    html=idx.read_text(encoding='utf-8')
    if 'gf-ach-script' in html: meta['achievements']=True; save_meta(game_dir,meta); sys.exit(0)
    inj=CSS+JS.replace('{slug}',slug)
    html=re.sub(r'</body>',inj+'\n</body>',html,1,re.I)
    idx.write_text(html,encoding='utf-8')
    meta['achievements']=True; save_meta(game_dir,meta)
    print(f'Achievements injected: {slug}')

if __name__=='__main__': main()
