#!/usr/bin/env python3
import json, re

KEY   = "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"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

# openclaw.json
cfg_path = "/root/.openclaw/openclaw.json"
cfg = json.load(open(cfg_path))
cfg["agents"]["defaults"]["model"]["primary"] = "openrouter/" + MODEL
cfg["plugins"]["installs"]["openrouter"]["apiKey"] = KEY
json.dump(cfg, open(cfg_path,"w"), ensure_ascii=False, indent=2)
print("openclaw.json updated")
print("  model: openrouter/" + MODEL)
print("  apiKey: saved")

# generate_game.py
gp = "/root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py"
code = open(gp).read()
code = re.sub(
    r'MODEL = os\.environ\.get\("GAMEFORGE_MODEL", "[^"]*"\)',
    'MODEL = os.environ.get("GAMEFORGE_MODEL", "' + MODEL + '")',
    code
)
code = re.sub(
    r'OPENROUTER_API_KEY = os\.environ\.get\("OPENROUTER_API_KEY", "[^"]*"\)',
    'OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "' + KEY + '")',
    code
)
open(gp,"w").write(code)
print("generate_game.py updated")

print()
print("Ready! Restart openclaw and test the bot.")
