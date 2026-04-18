#!/usr/bin/env python3
import urllib.request, json, time, re, os

KEY = "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"

MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "google/gemini-2.5-pro-exp-03-25:free",
    "qwen/qwen3-coder-480b-a35b-instruct:free",
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
]

best = None
print("Testing free models...\n")
for model in MODELS:
    try:
        data = json.dumps({
            "model": model,
            "messages": [{"role":"user","content":"Reply with one word: WORKS"}],
            "max_tokens": 10
        }).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={
                "Authorization": "Bearer " + KEY,
                "Content-Type": "application/json",
                "HTTP-Referer": "https://gameforge.vk",
                "X-Title": "GameForge"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            resp = json.loads(r.read())
        text = resp["choices"][0]["message"]["content"].strip()
        print("OK:   " + model)
        print("      -> " + text)
        best = model
        break
    except Exception as e:
        print("FAIL: " + model)
        print("      " + str(e)[:80])

print()
if not best:
    print("No working models right now. Try again in a few minutes.")
    exit(1)

# Save to openclaw.json
cfg_path = "/root/.openclaw/openclaw.json"
cfg = json.load(open(cfg_path))
cfg["agents"]["defaults"]["model"]["primary"] = "openrouter/" + best

# Save API key
if "openrouter" not in cfg.get("plugins",{}).get("installs",{}):
    cfg.setdefault("plugins",{}).setdefault("installs",{}).setdefault("openrouter",{})
cfg["plugins"]["installs"]["openrouter"]["apiKey"] = KEY

json.dump(cfg, open(cfg_path,"w"), ensure_ascii=False, indent=2)
print("openclaw.json: model = openrouter/" + best)
print("openclaw.json: apiKey saved")

# Update generate_game.py
gp = "/root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py"
code = open(gp).read()
code = re.sub(
    r'MODEL = os\.environ\.get\("GAMEFORGE_MODEL", "[^"]*"\)',
    'MODEL = os.environ.get("GAMEFORGE_MODEL", "' + best + '")',
    code
)
code = re.sub(
    r'OPENROUTER_API_KEY = os\.environ\.get\("OPENROUTER_API_KEY", ""\)',
    'OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "' + KEY + '")',
    code
)
open(gp,"w").write(code)
print("generate_game.py: model + key updated")

print()
print("DONE! Restart openclaw gateway and test.")
print("Best model: " + best)
