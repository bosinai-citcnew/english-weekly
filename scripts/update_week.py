"""每週英文教室：每週自動產生新文章。

在 GitHub Actions 上執行，用免費的 GitHub Models（不需要 API 金鑰，用內建的 GITHUB_TOKEN）。
1. 從 BBC 的公開 RSS 抓本週新聞標題與摘要
2. 請模型挑 3 則適合 A2-B1 的主題，各寫一篇簡單的學習文章
3. 從 TED 清單輪流挑 1 篇演講主題
4. 檢查、修正格式後寫入 week.json 與 archive/<週次>.json
只用 Python 標準函式庫。
"""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://models.github.ai/inference/chat/completions"
MODELS = ["openai/gpt-4o", "openai/gpt-4o-mini"]
FEEDS = [
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/health/rss.xml",
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
]
AVOID = re.compile(r"\b(kill|killed|dead|death|die|died|war|attack|shoot|shooting|murder|bomb|rape|sex|abuse|suicide|terror|stab|gun|election|vote)\w*", re.I)

# TED 演講清單：每週輪流一篇。desc 只寫演講主題，文章不得編造講者原話。
TED = [
    {"speaker": "Matt Cutts", "title": "Try something new for 30 days", "url": "https://www.ted.com/talks/matt_cutts_try_something_new_for_30_days",
     "desc": "A short, light talk: pick something you always wanted to do and try it for 30 days, a simple way to set and reach goals."},
    {"speaker": "Hany Farid", "title": "How to spot fake AI photos", "url": "https://www.ted.com/talks/hany_farid_how_to_spot_fake_ai_photos",
     "desc": "A digital forensics expert explains how AI-made images can fool us and gives everyday people practical tips to check pictures."},
    {"speaker": "Julian Treasure", "title": "How to speak so that people want to listen", "url": "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen",
     "desc": "A sound expert shares habits that make people stop listening and simple voice tools and exercises to speak more powerfully."},
    {"speaker": "Tim Urban", "title": "Inside the mind of a master procrastinator", "url": "https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator",
     "desc": "A funny talk about why we wait until the last minute, and a reminder to think about what we are putting off in life."},
]


def http(url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "english-weekly-bot"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def fetch_headlines():
    items, seen = [], set()
    for f in FEEDS:
        try:
            root = ET.fromstring(http(f))
        except Exception as e:  # 一個來源失敗不影響其他
            print("feed failed", f, e)
            continue
        n = 0
        for it in root.iter("item"):
            if n >= 8:
                break
            title = strip_html(it.findtext("title"))
            link = (it.findtext("link") or "").strip()
            desc = strip_html(it.findtext("description"))
            if not title or not link or title in seen or AVOID.search(title + " " + desc):
                continue
            seen.add(title)
            items.append({"title": title, "url": link, "desc": desc})
            n += 1
    return items[:30]


def ask(prompt, max_tokens=3000):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("缺少 GITHUB_TOKEN（請在 GitHub Actions 上執行，並開啟 models: read 權限）")
    last = None
    for model in MODELS:
        for attempt in range(3):
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": "You write materials for English learners. Reply with one JSON object only, no other text."},
                             {"role": "user", "content": prompt}],
                "temperature": 0.4, "max_tokens": max_tokens,
            }
            raw = b""
            try:
                req = urllib.request.Request(API, json.dumps(payload).encode(), {
                    "Content-Type": "application/json", "Accept": "application/json",
                    "Authorization": f"Bearer {token}", "User-Agent": "english-weekly-bot"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    raw = r.read()
                data = json.loads(raw.decode("utf-8"))
                txt = data["choices"][0]["message"]["content"] or ""
                txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
                s, e = txt.find("{"), txt.rfind("}")
                if s < 0 or e < s:
                    raise ValueError("回覆裡沒有 JSON：" + txt[:200])
                return json.loads(txt[s:e + 1])
            except urllib.error.HTTPError as e:
                body = e.read()[:400].decode("utf-8", "replace")
                last = f"HTTP {e.code} {body}"
                print(f"{model} attempt {attempt + 1} failed: {last}")
                if e.code in (401, 403, 404):
                    break
            except Exception as e:
                last = f"{e} | raw: {raw[:300]!r}"
                print(f"{model} attempt {attempt + 1} failed: {last}")
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"模型呼叫失敗：{last}")


ARTICLE_SPEC = """Return JSON with exactly these keys:
{"title":"English title","zh":"繁體中文標題","paras":["paragraph 1","paragraph 2","paragraph 3"],
 "glossary":{"word":{"pos":"noun/verb/adjective/adverb","ipa":"/US IPA/","zh":"繁體中文意思","def":"simple English definition in Cambridge Learner's Dictionary style","ex":"short example sentence","g":"用繁體中文 1-2 句說明文法：詞性變化、時態、搭配或句型，盡量連結文章中的用法"}},
 "grammar":[{"pt":"文法點名稱","zh":"繁體中文說明","ex":"an exact phrase copied from the paragraphs"}],
 "questions":[{"q":"English question","opts":["A","B","C"],"a":0}]}
Rules: exactly 3 paragraphs, 40-60 words each, CEFR A2-B1, short simple sentences, written fully in your own words.
glossary: 10-12 useful words from the text; each key is the lowercase base form of a word that appears in the paragraphs (battery for batteries).
grammar: exactly 4 items. questions: exactly 3, each with 3 options and the index (0-2) of the correct one.
All Chinese must be Traditional Chinese (台灣用語)."""


def write_news(item):
    p = f"""Write a short news article for Taiwanese English learners (CEFR A2-B1) about this news item.
Headline: {item['title']}
Summary: {item['desc']}
Use ONLY facts from the headline and summary. Do not add names, numbers or details that are not there. If something is unclear, leave it out.
{ARTICLE_SPEC}"""
    return ask(p)


def write_ted(t):
    p = f"""Write a short learning article for Taiwanese English learners (CEFR A2-B1) about the topic of this TED talk.
Talk: "{t['title']}" by {t['speaker']}. What it is about: {t['desc']}
Introduce the talk's topic and the main idea in simple words. Do NOT invent quotes or say what the speaker said word for word. You may say "The speaker talks about..." and add general, well-known advice on the topic.
{ARTICLE_SPEC}"""
    return ask(p)


def pick_news(items):
    lst = "\n".join(f"{i}. {x['title']} — {x['desc'][:160]}" for i, x in enumerate(items))
    r = ask(f"""Pick 3 news items that are good for adult English learners: interesting, positive or neutral, about science, technology, health, environment, education or daily life. Avoid violence, war, crime, disasters with deaths and political elections. Pick 3 different topics.
{lst}
Return JSON: {{"picks":[index, index, index]}}""", 200)
    out = []
    for i in r.get("picks", []):
        if isinstance(i, int) and 0 <= i < len(items) and items[i] not in out:
            out.append(items[i])
    for x in items:  # 不足 3 篇時補上
        if len(out) >= 3:
            break
        if x not in out:
            out.append(x)
    return out[:3]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def word_in(word, s):
    stem = re.escape(word[:-1] if word.endswith("e") or word.endswith("y") else word)
    return re.search(rf"\b{stem}\w*\b", s, re.I)


def repair(a, idx, kind, source):
    """檢查並修正一篇文章，回傳完整的文章物件；格式不對就丟出例外。"""
    paras = [p.strip() for p in a.get("paras", []) if isinstance(p, str) and p.strip()]
    if len(paras) < 3:
        raise ValueError("段落不足")
    paras = paras[:3]
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
        if len(s.split()) < 5 or len(s.split()) > 18:
            continue
        for w in gl:
            m = word_in(w, s)
            if m and m.group(0).lower() not in [k["target"].lower() for k in keys]:
                keys.append({"s": s, "target": m.group(0)})
                break
    if len(keys) < 2:
        raise ValueError("找不到重點句")
    note = ("內容主題取自 TED 熱門演講。內文為學習用改寫，不是講者原話，請看原演講了解細節。"
            if kind == "ted" else "依本週新聞主題改寫成 A2-B1 學習文章，非原文。")
    return {"id": f"a{idx}", "kind": kind, "title": str(a.get("title", "")).strip() or source["name"],
            "zh": str(a.get("zh", "")), "source": source, "note": note, "paras": paras, "glossary": gl,
            "grammar": grammar, "questions": qs[:3], "keySentences": keys, "targetWords": list(gl)[:3]}


def make(fn, arg, idx, kind, source):
    last = None
    for _ in range(3):
        try:
            return repair(fn(arg), idx, kind, source)
        except Exception as e:
            last = e
            print("retry article", idx, e)
    raise RuntimeError(f"第 {idx} 篇文章失敗：{last}")


def main():
    today = dt.date.today()
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
    items = fetch_headlines()
    if len(items) < 3:
        raise RuntimeError("新聞來源抓不到足夠的標題")
    arts = []
    for i, it in enumerate(pick_news(items), 1):
        arts.append(make(write_news, it, i, "news", {"name": "BBC News：" + it["title"], "url": it["url"]}))
    t = TED[w % len(TED)]
    arts.append(make(write_ted, t, 4, "ted", {"name": f"TED：{t['speaker']}, {t['title']}", "url": t["url"]}))
    data = {"weekId": week_id, "range": f"{mon:%m/%d} - {mon + dt.timedelta(days=6):%m/%d}", "level": "A2-B1", "articles": arts}
    os.makedirs(os.path.join(ROOT, "archive"), exist_ok=True)
    for p in (path, os.path.join(ROOT, "archive", f"{week_id}.json")):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    print("完成", week_id, [a["title"] for a in arts])


if __name__ == "__main__":
    main()
