"""每週英文教室：每週自動換一批新文章（不需要 AI、不需要金鑰）。

在 GitHub Actions 上每週一執行：從 bank.json（12 週的文章題庫）依週次輪流挑一週，
寫入 week.json 與 archive/<週次>.json。只用 Python 標準函式庫。

想加新文章：在 bank/ 資料夾新增 srcN.py（格式照 src1.py），再執行 python bank/build.py。
B2、C1 程度的文章放在 bank_levels.json（每筆是 {"b2": [...], "c1": [...]}）。
"""
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = dt.date(2026, 11, 23)  # 題庫第 1 週對應的星期一


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def word_in(word, s):
    stem = re.escape(word[:-1] if word.endswith("e") or word.endswith("y") else word)
    return re.search(rf"\b{stem}\w*\b", s, re.I)


LEVELS = {"base": ("A2-B1", 3, 18), "b2": ("B2", 4, 24), "c1": ("C1", 4, 28)}  # 程度：(名稱, 最多段落, 重點句最長字數)


def repair(a, idx, kind, source, lvl="base"):
    """檢查一篇文章並補上重點句、目標單字；格式不對就丟出例外。（bank/build.py 也會用到）"""
    name, maxp, maxw = LEVELS[lvl]
    paras = [p.strip() for p in a.get("paras", []) if isinstance(p, str) and p.strip()]
    if len(paras) < 3:
        raise ValueError("段落不足")
    paras = paras[:maxp]
    text = " ".join(paras)
    gl = {}
    for k, v in (a.get("glossary") or {}).items():
        k = str(k).lower().strip()
        if isinstance(v, dict) and v.get("zh") and word_in(k, text):
            gl[k] = {f: str(v.get(f, "")) for f in ("pos", "ipa", "zh", "def", "ex", "g")}
    if len(gl) < 6:
        raise ValueError("單字表太少")
    grammar = [g for g in a.get("grammar", []) if isinstance(g, dict) and g.get("pt") and g.get("ex")][:4]
    qs = []
    for q in a.get("questions", []):
        try:
            if q.get("q") and len(q["opts"]) == 3 and int(q["a"]) in (0, 1, 2):
                qs.append({"q": str(q["q"]), "opts": [str(o) for o in q["opts"]], "a": int(q["a"])})
        except Exception:
            pass
    if len(qs) < 2:
        raise ValueError("題目不足")
    keys = []
    for s in sorted(sentences(text), key=len):
        if len(keys) == 2:
            break
        if len(s.split()) < 5 or len(s.split()) > maxw:
            continue
        for w in gl:
            m = word_in(w, s)
            if m and m.group(0).lower() not in [k["target"].lower() for k in keys]:
                keys.append({"s": s, "target": m.group(0)})
                break
    if len(keys) < 2:
        raise ValueError("找不到重點句")
    note = ("內容主題取自 TED 熱門演講。內文為學習用改寫，不是講者原話，請看原演講了解細節。"
            if kind == "ted" else f"學習用短文，依參考資料改寫成 {name} 程度，延伸閱讀請看來源連結。")
    return {"id": f"a{idx}" if lvl == "base" else f"{lvl}-{idx}", "level": name, "kind": kind, "title": str(a.get("title", "")).strip() or source["name"],
            "zh": str(a.get("zh", "")), "source": source, "note": note, "paras": paras, "glossary": gl,
            "grammar": grammar, "questions": qs[:3], "keySentences": keys, "targetWords": list(gl)[:3]}


def main(today=None):
    today = today or dt.date.today()
    y, w, _ = today.isocalendar()
    week_id = f"{y}-W{w:02d}"
    mon = today - dt.timedelta(days=today.weekday())
    path = os.path.join(ROOT, "week.json")
    try:
        if json.load(open(path, encoding="utf-8")).get("weekId") == week_id and "--force" not in sys.argv:
            print("本週已更新過", week_id)
            return
    except Exception:
        pass
    bank = json.load(open(os.path.join(ROOT, "bank.json"), encoding="utf-8"))
    n = ((mon - START).days // 7) % len(bank)
    data = {"weekId": week_id, "range": f"{mon:%m/%d} - {mon + dt.timedelta(days=6):%m/%d}", "level": "A2-B1",
            "bankWeek": n + 1, "articles": bank[n]}
    # B2、C1 程度：從 bank_levels.json 輪流挑（每週 Claude 更新時會把新文章加進去，題庫越來越多）
    try:
        lv = json.load(open(os.path.join(ROOT, "bank_levels.json"), encoding="utf-8"))
        if lv:
            data["levels"] = lv[((mon - START).days // 7) % len(lv)]
    except Exception:
        pass
    os.makedirs(os.path.join(ROOT, "archive"), exist_ok=True)
    for p in (path, os.path.join(ROOT, "archive", f"{week_id}.json")):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    print("完成", week_id, "題庫第", n + 1, "週：", [a["title"] for a in bank[n]], flush=True)


if __name__ == "__main__":
    main()
