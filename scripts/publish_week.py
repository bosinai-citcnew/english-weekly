"""每週 Claude 更新時事文章用：讀 /home/claude/raw.py（ARTICLES 與 LEVELS），檢查後寫入
week.json、archive/<週次>.json，並把 B2、C1 文章加進 bank_levels.json（讓題庫越來越多）。

用法（在儲存庫根目錄）：python3 scripts/publish_week.py [raw.py 所在資料夾，預設 /home/claude]
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else "/home/claude")
import update_week as u  # noqa: E402
import raw  # noqa: E402


def build(arts, lvl):
    out = []
    for i, a in enumerate(arts, 1):
        text = " ".join(a["paras"])
        for g in a["grammar"]:
            assert g["ex"] in text, f"[{lvl} {i}] grammar ex 不在文章裡：{g['ex']}"
        for k in a["glossary"]:
            assert u.word_in(k, text), f"[{lvl} {i}] 單字不在文章裡：{k}"
        out.append(u.repair(dict(a), i, a["kind"], a["source"], lvl))
    return out


today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
y, w, _ = today.isocalendar()
mon = today - dt.timedelta(days=today.weekday())
d = {"weekId": f"{y}-W{w:02d}", "range": f"{mon:%m/%d} - {mon + dt.timedelta(days=6):%m/%d}",
     "level": "A2-B1", "source": "claude", "articles": build(raw.ARTICLES, "base")}
levels = {k: build(v, k) for k, v in getattr(raw, "LEVELS", {}).items()}
if levels:
    d["levels"] = levels
os.makedirs(os.path.join(ROOT, "archive"), exist_ok=True)
for p in ("week.json", f"archive/{d['weekId']}.json"):
    json.dump(d, open(os.path.join(ROOT, p), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if set(levels) >= {"b2", "c1"}:
    bp = os.path.join(ROOT, "bank_levels.json")
    bank = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else []
    bank = [b for b in bank if b.get("weekId") != d["weekId"]] + [{"weekId": d["weekId"], **levels}]
    json.dump(bank, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(d["weekId"], {k: [a["title"] for a in v] for k, v in {"base": d["articles"], **levels}.items()})
