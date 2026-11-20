import json, os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import update_week as u
weeks, problems = [], []
for name in sorted(f[:-3] for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if f.startswith("src") and f.endswith(".py")):
    for wk in importlib.import_module(name).WEEKS:
        out = []
        for i, a in enumerate(wk, 1):
            text = " ".join(a["paras"])
            for g in a["grammar"]:
                if g["ex"] not in text: problems.append(f"{a['title']}: grammar ex not in text: {g['ex']}")
            for k in a["glossary"]:
                if not u.word_in(k, text): problems.append(f"{a['title']}: word not in text: {k}")
            for p in a["paras"]:
                n = len(p.split())
                if n > 70: problems.append(f"{a['title']}: long paragraph {n}")
            r = u.repair(dict(a), i, a["kind"], a["source"])
            out.append(r)
        weeks.append(out)
print(len(weeks), "weeks")
print("\n".join(problems) or "no problems")
json.dump(weeks, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bank.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
