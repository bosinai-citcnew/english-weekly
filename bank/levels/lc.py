"""B2、C1 題庫的精簡寫法。每篇的來源與類型沿用同一週同一位置的 A2-B1 文章。"""


def w(word, pos, ipa, zh, d, ex, g):
    return (word, {"pos": pos, "ipa": ipa, "zh": zh, "def": d, "ex": ex, "g": g})


def gr(pt, zh, ex):
    return {"pt": pt, "zh": zh, "ex": ex}


def q(text, right, *wrong):
    return {"q": text, "opts": [right, *wrong], "a": 0}


def L(title, zh, paras, words, grammar, questions):
    return {"title": title, "zh": zh, "paras": paras, "glossary": dict(words), "grammar": grammar, "questions": questions}
