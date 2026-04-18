#!/usr/bin/env python3
import sys, os, re

def test_game(slug):
    path = f"/root/.openclaw/workspace/games/{slug}/index.html"
    if not os.path.exists(path):
        print(f"Not found: {path}"); return
    code = open(path, encoding="utf-8").read()
    print(f"\nTesting: {slug}\n" + "=" * 45)
    checks = [
        ("Start screen (Enter/Space)",    r"Enter|Space",                True,  False),
        ("Canvas or DOM element",         r"<canvas|getElementById",     True,  False),
        ("Game loop (interval/RAF)",      r"setInterval|requestAnimationFrame", True, False),
        ("Game over condition",           r"game.?over|running.*false|clearInterval", True, False),
        ("Score/points",                  r"score|Score|points",         False, False),
        ("Arrow key controls",            r"ArrowUp|ArrowLeft",          False, False),
        ("No blocking alert()",           r"alert\(",                    False, True),
    ]
    passed = 0
    for name, pat, required, invert in checks:
        found = bool(re.search(pat, code, re.I))
        ok = (not found) if invert else found
        if ok: passed += 1
        icon = "OK" if ok else ("FAIL" if required else "WARN")
        print(f"  [{icon}] {name}")
    pct = int(passed / len(checks) * 100)
    status = "READY" if pct >= 80 else "ISSUES" if pct >= 60 else "BROKEN"
    print("-" * 45)
    print(f"  Result: {passed}/{len(checks)} ({pct}%) — {status}")
    print("=" * 45)

slug = sys.argv[1] if len(sys.argv) > 1 else None
if slug:
    test_game(slug)
else:
    d = "/root/.openclaw/workspace/games"
    if os.path.exists(d):
        for g in sorted(os.listdir(d)): test_game(g)
