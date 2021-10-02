from typing import List, Text

_CSS = """
@font-face { font-family: 'nbl'; src: url("_NotoSansSC-Black.otf"); }
@font-face { font-family: 'nbo'; src: url("_NotoSansSC-Bold.otf"); }
@font-face { font-family: 'nli'; src: url("_NotoSansSC-Light.otf"); }
@font-face { font-family: 'nme'; src: url("_NotoSansSC-Medium.otf"); }
@font-face { font-family: 'nre'; src: url("_NotoSansSC-Regular.otf"); }
@font-face { font-family: 'nth'; src: url("_NotoSansSC-Thin.otf"); }
@font-face { font-family: 'rbl'; src: url("_NotoSerifSC-Black.otf"); }
@font-face { font-family: 'rbo'; src: url("_NotoSerifSC-Bold.otf"); }
@font-face { font-family: 'rex'; src: url("_NotoSerifSC-ExtraLight.otf"); }
@font-face { font-family: 'rli'; src: url("_NotoSerifSC-Light.otf"); }
@font-face { font-family: 'rme'; src: url("_NotoSerifSC-Medium.otf"); }
@font-face { font-family: 'rre'; src: url("_NotoSerifSC-Regular.otf"); }
@font-face { font-family: 'rse'; src: url("_NotoSerifSC-SemiBold.otf"); }

.card {
 font-family: serif;
 text-align: center;
}

#meaning {
  font-size: 2em;
  display: inline-block;
}
#characters {
  font-size: 5em;
}
#pinyin {
  font-size: 2em;
  font-weight: 900;
}

.night_mode font[color="blue"] {
   color: blue;
}
.night_mode font[color="purple"] {
   color: purple;
}
.night_mode font[color="red"] {
   color: red;
}
.night_mode font[color="green"] {
   color: green;
}
.night_mode font[color="grey"] {
   color: grey;
}
"""


_SCRIPT = """
<script>
var fonts = ['nbl', 'nbo', 'nli', 'nme', 'nre', 'nth', 'rbl', 'rbo', 'rex', 'rli', 'rme', 'rre', 'rse'];
document.getElementById('characters').style.fontFamily = fonts[Math.floor(
    Math.random() * fonts.length)];
</script>
"""


def _to_span_html(fieldname: Text):
    return f"<span id='{fieldname}'>{{{{{fieldname}}}}}</span>"


def gen_template(idx, map_from: List[Text], map_to: List[Text]):
    name = f"Card {idx} {'+'.join(map_from)}=>{'+'.join(map_to)}"
    qfmt = "<br>".join(_to_span_html(f) for f in map_from)
    if "characters" in map_from:
        qfmt += _SCRIPT
    afmt = "{{FrontSide}} <hr>"

    afmt += "<br>".join(_to_span_html(f) for f in map_to)

    return {
        'name': name,
        'qfmt': qfmt,
        'afmt': afmt,
    }
