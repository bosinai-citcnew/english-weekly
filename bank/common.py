"""Helpers for writing the article bank compactly."""


def w(word, pos, ipa, zh, d, ex, g):
    return (word, {"pos": pos, "ipa": ipa, "zh": zh, "def": d, "ex": ex, "g": g})


def gr(pt, zh, ex):
    return {"pt": pt, "zh": zh, "ex": ex}


def q(text, opts, a):
    return {"q": text, "opts": opts, "a": a}


def wiki(page):
    return {"name": "Wikipedia：" + page.replace("_", " "), "url": "https://en.wikipedia.org/wiki/" + page}


def art(title, zh, source, paras, words, grammar, questions, kind="news"):
    return {"kind": kind, "title": title, "zh": zh, "source": source, "paras": paras,
            "glossary": dict(words), "grammar": grammar, "questions": questions}


def ted(speaker, talk, zh, url, paras, words, grammar, questions):
    a = art(talk, zh, {"name": f"TED：{speaker}, {talk}", "url": url}, paras, words, grammar, questions, kind="ted")
    return a
