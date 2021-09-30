from typing import Text


def match_numbers(defn) -> Text:
    els = []
    matching = 1
    while True:
        i = defn.find(f"{matching} ")
        if i == -1:
            break
        a = i + len(str(matching)) + 1
        j = defn.find(f"{matching+1} ")
        if j == -1:
            els.append(defn[a:])
            break
        els.append(defn[a:j])
        matching += 1
    html = "<ol>"
    for e in els:
        html += "<li>" + e + "</li>"
    html += "</ol>"
    return html


def make_defn_html(defn) -> Text:
    # match things like "1 foo 2 bar 3 baz"
    if "1 " in defn and "2 " in defn:
        return match_numbers(defn)
    return defn
