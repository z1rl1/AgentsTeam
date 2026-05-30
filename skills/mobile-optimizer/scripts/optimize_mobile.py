#!/usr/bin/env python3
"""
GameForge Mobile Optimizer — injects touch controls without LLM.
Usage: python3 optimize_mobile.py <slug>
"""
import sys, json, re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'

VIEWPORT_META = '<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">'

TOUCH_CSS = """<style>
/* mobile-optimizer: prevent zoom, hide scrollbars */
* { touch-action: pan-x pan-y; }
canvas, #gameCanvas { touch-action: none; }
body { overflow: hidden; margin: 0; }
.mo-btn {
  position: fixed; z-index: 9999;
  background: rgba(255,255,255,0.18);
  border: 2px solid rgba(255,255,255,0.45);
  border-radius: 50%; color: #fff;
  font-size: 22px; width: 56px; height: 56px;
  display: flex; align-items: center; justify-content: center;
  touch-action: none; user-select: none; cursor: pointer;
}
#mo-action {
  width: 68px; height: 68px; border-radius: 12px;
  background: rgba(255,60,60,0.35); font-size: 14px;
}
</style>"""

TOUCH_JS = """<script>
/* mobile-optimizer touch controls */
(function(){
  var keys = {
    left:  {key:'ArrowLeft',  code:'ArrowLeft',  keyCode:37},
    right: {key:'ArrowRight', code:'ArrowRight', keyCode:39},
    up:    {key:'ArrowUp',    code:'ArrowUp',    keyCode:38},
    down:  {key:'ArrowDown',  code:'ArrowDown',  keyCode:40},
    action:{key:' ',          code:'Space',      keyCode:32}
  };
  function fire(type, info) {
    document.dispatchEvent(new KeyboardEvent(type, {
      key:info.key, code:info.code, keyCode:info.keyCode,
      which:info.keyCode, bubbles:true, cancelable:true
    }));
  }
  function btn(label, dir, id, style) {
    var el = document.createElement('button');
    el.className = 'mo-btn'; el.textContent = label;
    if (id) el.id = id;
    el.style.cssText = style;
    el.addEventListener('touchstart', function(e){ e.preventDefault(); fire('keydown', keys[dir]); }, {passive:false});
    el.addEventListener('touchend',   function(e){ e.preventDefault(); fire('keyup',   keys[dir]); }, {passive:false});
    el.addEventListener('mousedown',  function(){ fire('keydown', keys[dir]); });
    el.addEventListener('mouseup',    function(){ fire('keyup',   keys[dir]); });
    return el;
  }
  function inject() {
    document.body.appendChild(btn('←','left',  '', 'bottom:90px;left:16px'));
    document.body.appendChild(btn('→','right', '', 'bottom:90px;left:128px'));
    document.body.appendChild(btn('↑','up',    '', 'bottom:150px;left:72px'));
    document.body.appendChild(btn('↓','down',  '', 'bottom:30px;left:72px'));
    document.body.appendChild(btn('ACTION','action','mo-action','bottom:80px;right:20px'));
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else { inject(); }
})();
</script>"""


def ensure_viewport(html):
    if re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I):
        print('  viewport: already present')
        return html
    m = re.search(r'(<head[^>]*>)', html, re.I)
    if m:
        return html[:m.end()] + '\n  ' + VIEWPORT_META + html[m.end():]
    return VIEWPORT_META + '\n' + html


def inject_touch(html):
    if 'mobile-optimizer' in html:
        print('  touch: already injected')
        return html
    m = re.search(r'</body>', html, re.I)
    pos = m.start() if m else len(html)
    return html[:pos] + TOUCH_CSS + TOUCH_JS + html[pos:]


def read_meta(slug):
    p = GAMES_DIR / slug / 'gameforge.json'
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def write_meta(slug, meta):
    p = GAMES_DIR / slug / 'gameforge.json'
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False))


def optimize(slug):
    game_dir   = GAMES_DIR / slug
    index_path = game_dir / 'index.html'
    if not index_path.exists():
        print(f'ERROR: {index_path} not found'); return False

    print(f'[mobile-optimizer] {slug}')
    html = index_path.read_text(encoding='utf-8')
    html = ensure_viewport(html)
    html = inject_touch(html)
    index_path.write_text(html, encoding='utf-8')
    print('  Saved.')

    meta = read_meta(slug)
    meta['mobile_optimized']    = True
    meta['mobile_optimized_at'] = datetime.utcnow().isoformat() + 'Z'
    write_meta(slug, meta)
    print('[mobile-optimizer] Done.')
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 optimize_mobile.py <slug>'); sys.exit(1)
    ok = optimize(sys.argv[1])
    sys.exit(0 if ok else 1)
