"""把 bank/levels/wNN.py 組成 bank_lv.json（12 週，每週 {"b2": [4 篇], "c1": [4 篇]}，主題對應 bank.json 同一週）。"""
import importlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "levels")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
import update_week as u
bank = json.load(open(os.path.join(ROOT, "bank.json"), encoding="utf-8"))
out, problems = [], []
for n in range(1, len(bank) + 1):
    try:
        mod = importlib.import_module(f"w{n:02d}")
    except ModuleNotFoundError:
        problems.append(f"week {n}: missing"); continue
    wk = {}
    for lvl in ("b2", "c1"):
        arts = []
        for i, a in enumerate(getattr(mod, lvl.upper()), 1):
            base = bank[n - 1][i - 1]
            a = dict(a, kind=base["kind"], source=base["source"])
            text = " ".join(a["paras"])
            for g in a["grammar"]:
                if g["ex"] not in text: problems.append(f"w{n} {lvl} {i}: grammar ex: {g['ex']}")
            for k in a["glossary"]:
                if not u.word_in(k, text): problems.append(f"w{n} {lvl} {i}: word: {k}")
            try:
                arts.append(u.repair(a, i, a["kind"], a["source"], lvl))
            except Exception as e:
                problems.append(f"w{n} {lvl} {i}: {e}")
        wk[lvl] = arts
    out.append(wk)
print(len(out), "weeks"); print("\n".join(problems) or "no problems")
if not problems:
    json.dump(out, open(os.path.join(ROOT, "bank_lv.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
