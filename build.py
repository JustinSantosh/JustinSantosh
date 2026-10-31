"""Builds the animated SVG cards in assets/ for the GitHub profile README.

Edit the CONTENT section, then run:  python build.py
Fonts (SIL Open Font License, from Google Fonts) are subset and embedded in each SVG,
because GitHub renders README images without access to external fonts.
"""
import base64
import io
import re
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).parent
OUT = ROOT / "assets"
FONTS = ROOT / "fonts"

# ─────────────────────────── CONTENT ───────────────────────────
NAME_1, NAME_2 = "JUSTIN", "SANTOSH"
TOUR = "the “Full Stack” tour"
ROLES = "AI ENGINEER · FULL-STACK · DEVOPS · BACKEND"

RECEIPT = [
    ("ROLE", "AI ENG + FULL-STACK"),
    ("ALSO PLAYS", "DEVOPS · BACKEND"),
    ("BASED IN", "INDIA · IST"),
    ("STUDYING", "B.TECH CS · IIIT-NR"),
    ("OPEN TO", "INTERNSHIPS"),
    None,
    ("HEADLINER", "VULGRAPH"),
    ("THE API", "RENEWALHUB"),
    ("DASHBOARD", "SIGNALIST"),
    ("AI TOOL", "RESUME READER"),
    None,
    ("SHIPS WITH", "NEXT.JS · FASTAPI"),
    ("RUNS ON", "DOCKER · CI/CD"),
]

GENRES = [  # title lines, subtitle lines, fill, text colour
    (["AI", "Engineering"], ["LLMs · RAG · agents"], "#7a1f2b", "#f3e9d2"),
    (["Full-", "stack"], ["Next.js · React · TS"], "#e0a63a", "#26231f"),
    (["DevOps"], ["Docker · CI/CD", "Vercel · Linux"], "#9db4ff", "#1c2140"),
    (["Backend"], ["FastAPI · Express", "Postgres · Mongo"], "#f3e9d2", "#26231f"),
]

TOOLS_1 = ["Python", "TypeScript", "JavaScript", "Next.js", "React", "Node.js", "Express",
           "FastAPI", "SQLAlchemy", "Pydantic", "Tailwind", "Vite", "Zustand"]
TOOLS_2 = ["PostgreSQL", "MongoDB", "Supabase", "Docker", "GitHub Actions", "Vercel",
           "OpenAI", "Gemini", "LangSmith", "Inngest", "Upstash", "Clerk", "JWT", "pandas"]

TRACKS = [  # file, number, title, hook, two description lines, chips, genre tag, label colour
    ("vulgraph", "01", "VulGraph", "your codebase, drawn as a map",
     ["Parses JS/TS repos into interactive dependency graphs",
      "with impact analysis and graph-grounded AI answers."],
     ["Next.js", "ts-morph", "Supabase", "LangSmith"], "AI ENGINEERING", "#7a1f2b"),
    ("renewalhub", "02", "RenewalHub API", "never miss a renewal again",
     ["Subscription API: JWT auth, spend summaries, rate",
      "limiting and scheduled email reminder workflows."],
     ["Express", "MongoDB", "Arcjet", "Upstash"], "BACKEND", "#e0a63a"),
    ("signalist", "03", "Signalist", "the market, minus the noise",
     ["Stock dashboard with watchlists, live quotes and",
      "AI-written market digests sent by background jobs."],
     ["Next.js", "Inngest", "Gemini", "MongoDB"], "FULL-STACK", "#9db4ff"),
    ("resume", "04", "Berozgar ki Lathi", "the resume reader that tells the truth",
     ["Upload a PDF, paste a job description, get ATS",
      "scoring and prioritised AI feedback. No backend."],
     ["React 19", "PDF.js", "Puter.js", "Zustand"], "AI TOOL", "#f3e9d2"),
]

DEEP_CUTS = [  # file, title, hook, chips
    ("support-desk", "Smart Support Desk", "tickets, triaged", ["FastAPI", "Postgres", "Alembic"]),
    ("recommender", "Recommendation Engine", "you might also like…", ["SVD", "MovieLens", "Python"]),
    ("forecasting", "Demand Forecasting", "shelves that never run dry", ["Time series", "pandas"]),
]

LINER = [
    ("serif", "Hi, I’m Justin."),
    ("serif", "I study computer science at IIIT Naya Raipur."),
    ("serif", "I like owning the whole pipeline: the model, the API, the container, the deploy."),
    ("hand", "build it, ship it, then make it better."),
    ("serif", "VulGraph turns a codebase into a map. RenewalHub keeps subscriptions honest."),
    ("serif", "Signalist reads the market for you. The resume reader tells you the truth."),
    ("serif", "Right now: shipping side projects and open to internships."),
]

# ─────────────────────────── STYLE ───────────────────────────
BG, CARD, LINE = "#1a1917", "#23211e", "#3a3631"
CREAM, POSTER, MUSTARD, PERI, MUTED = "#f3e9d2", "#7a1f2b", "#e0a63a", "#9db4ff", "#8a8478"
PAPER, PAPER_INK = "#f4efe4", "#26231f"

FONT_FILES = {
    "Disp": ("ArchivoBlack-Regular.ttf", None),
    "Mono": ("SpaceMono-Regular.ttf", None),
    "MonoB": ("SpaceMono-Bold.ttf", None),
    "ISerif": ("InstrumentSerif-Italic.ttf", None),
    "Hand": ("Caveat.ttf", {"wght": 600}),
}
_font_cache = {}


def font_face(family, chars):
    file, inst = FONT_FILES[family]
    if file not in _font_cache:
        f = TTFont(FONTS / file)
        if inst:
            f = instancer.instantiateVariableFont(f, inst)
        buf = io.BytesIO()
        f.save(buf)
        _font_cache[file] = buf.getvalue()
    f = TTFont(io.BytesIO(_font_cache[file]))
    opts = subset.Options()
    opts.flavor = "woff"
    s = subset.Subsetter(opts)
    s.populate(text=chars)
    s.subset(f)
    buf = io.BytesIO()
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/woff;base64,{b64}) format('woff')}}"


def text_of(body, family):
    """Characters used inside elements styled with a given font class."""
    cls = {"Disp": "d", "Mono": "m", "MonoB": "mb", "ISerif": "s", "Hand": "h"}[family]
    found = re.findall(rf'class="[^"]*\b{cls}\b[^"]*"[^>]*>([^<]*)<', body)
    return "".join(found)


GRAIN = """<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/>
<feComponentTransfer><feFuncA type="table" tableValues="0 .09"/></feComponentTransfer></filter>"""

BASE_CSS = """.d{font-family:Disp}.m{font-family:Mono}.mb{font-family:MonoB}.s{font-family:ISerif}.h{font-family:Hand}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes fadeup{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes eq{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}"""


def svg(name, w, h, body, css="", alt=""):
    families = [f for f in FONT_FILES if text_of(body, f)]
    faces = "".join(font_face(f, text_of(body, f) + " ") for f in families)
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'role="img" aria-label="{escape(alt)}"><title>{escape(alt)}</title>'
           f"<defs>{GRAIN}<style>{faces}{BASE_CSS}{css}</style></defs>{body}</svg>")
    (OUT / f"{name}.svg").write_text(doc, encoding="utf-8")
    print(f"  {name}.svg  {len(doc) // 1024} KB")


def frame(w, h, r=18, fill=BG):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
            f'<rect width="{w}" height="{h}" rx="{r}" filter="url(#grain)"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="{LINE}"/>')


def t(x, y, s, cls, size, fill, extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" {extra}>{escape(s)}</text>'


def vinyl(cx, cy, r, label, cls="spin", label_text=""):
    grooves = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{gr}" fill="none" stroke="#2a2826" stroke-width=".8"/>'
        for gr in range(int(r * .38), int(r * .96), max(3, int(r / 28))))
    lt = "".join(t(cx, cy - r * .1 + k * r * .26, s, "mb", r * .085, PAPER_INK, 'text-anchor="middle" letter-spacing="1"')
                 for k, s in enumerate(label_text.split("|"))) if label_text else ""
    return (f'<g class="{cls}" style="transform-origin:{cx}px {cy}px">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#121110"/>{grooves}'
            f'<path d="M{cx - r * .7},{cy - r * .7} A{r},{r} 0 0 1 {cx + r * .2},{cy - r * .97}" '
            f'stroke="#ffffff" stroke-opacity=".08" stroke-width="{r * .18}" fill="none"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .32}" fill="{label}"/>{lt}'
            f'<circle cx="{cx}" cy="{cy}" r="{max(2, r * .03)}" fill="{BG}"/></g>')


def chip_w(s, size=11):
    return len(s) * size * .6 + 18


def chips(x, y, items, size=11, fill=LINE, ink=CREAM):
    out, cx = [], x
    for s in items:
        w = chip_w(s, size)
        out.append(f'<rect x="{cx}" y="{y - size - 6}" width="{w}" height="{size + 12}" rx="{(size + 12) / 2}" fill="{fill}"/>'
                   + t(cx + w / 2, y + 1, s, "m", size, ink, 'text-anchor="middle"'))
        cx += w + 8
    return "".join(out)


# ─────────────────────────── CARDS ───────────────────────────
def hero():
    w, h = 900, 440
    eq = "".join(
        f'<rect x="{770 + i * 14}" y="330" width="9" height="60" rx="3" fill="{[MUSTARD, PERI, CREAM, POSTER][i % 4]}" '
        f'style="transform-origin:{774 + i * 14}px 390px;animation:eq {0.7 + (i % 3) * .25}s ease-in-out {i * .12}s infinite"/>'
        for i in range(7))
    body = (
        frame(w, h, 22)
        + f'<circle cx="575" cy="215" r="182" fill="none" stroke="{MUSTARD}" stroke-width="3"/>'
        + vinyl(575, 215, 176, MUSTARD, label_text="FULL STACK|VOL 01")
        # tonearm
        + f'<g class="arm"><circle cx="790" cy="52" r="26" fill="{CREAM}"/><circle cx="790" cy="52" r="10" fill="{BG}"/>'
          f'<path d="M790 52 L735 190 L715 205" stroke="{CREAM}" stroke-width="7" stroke-linecap="round" fill="none"/>'
          f'<rect x="700" y="198" width="22" height="14" rx="3" fill="{CREAM}" transform="rotate(35 711 205)"/></g>'
        # poster
        + '<g class="poster"><g transform="rotate(-2.5 255 220)">'
          f'<rect x="56" y="42" width="408" height="362" fill="#000" opacity=".35" transform="translate(7 9)"/>'
          f'<rect x="56" y="42" width="408" height="362" fill="{POSTER}"/>'
          f'<rect x="56" y="42" width="408" height="362" filter="url(#grain)"/>'
          f'<rect x="68" y="54" width="384" height="338" fill="none" stroke="{CREAM}" stroke-opacity=".22"/>'
        + t(86, 88, "LIVE · THE 2026 TOUR", "mb", 13, CREAM, 'letter-spacing="2.5"')
        + t(90, 172, NAME_1, "d", 66, "#3d0f16") + t(86, 168, NAME_1, "d", 66, CREAM)
        + t(90, 244, NAME_2, "d", 66, "#3d0f16") + t(86, 240, NAME_2, "d", 66, CREAM)
        + f'<g transform="rotate(-1.5 200 290)"><rect x="86" y="268" width="286" height="44" fill="{MUSTARD}"/>'
        + t(100, 299, TOUR, "s", 27, PAPER_INK) + "</g>"
        + t(86, 350, ROLES, "mb", 12.5, CREAM, 'letter-spacing=".6"')
        + t(86, 372, "IIIT NAYA RAIPUR · INDIA", "m", 12, CREAM, 'opacity=".7" letter-spacing="1"')
        + "</g></g>"
        # notes
        + f'<g transform="rotate(-6 770 290)">' + t(690, 300, "hi, I’m Justin ↑", "h", 30, PERI) + "</g>"
        + t(560, 425, "spinning since 2024 ↻", "h", 22, MUTED)
        + eq
    )
    css = (".spin{animation:spin 7s linear infinite}"
           ".poster{animation:bob 5s ease-in-out infinite}"
           "@keyframes arm{0%,100%{transform:rotate(0)}50%{transform:rotate(1.6deg)}}"
           ".arm{transform-origin:790px 52px;animation:arm 3.5s ease-in-out infinite}")
    svg("hero", w, h, body, css, "Justin Santosh: the Full Stack tour. AI engineer, full-stack, DevOps, backend.")


def now_playing():
    w, h = 900, 92
    n = len(TRACKS)
    dur = n * 3
    titles = "".join(
        f'<g class="trk{" t0" if i == 0 else ""}" style="animation-delay:{i * 3}s">'
        + t(150, 40, f"TRACK {num} / {n:02d}", "mb", 11, MUTED, 'letter-spacing="1.5"')
        + t(150, 66, f"{title} · {hook}", "d", 19, CREAM) + "</g>"
        for i, (_, num, title, hook, *_r) in enumerate(TRACKS))
    reels = "".join(
        f'<g style="transform-origin:{cx}px 46px;animation:spin 2.4s linear infinite">'
        f'<circle cx="{cx}" cy="46" r="13" fill="{CREAM}"/><circle cx="{cx}" cy="46" r="4" fill="{BG}"/>'
        + "".join(f'<rect x="{cx - 1.5}" y="34" width="3" height="7" fill="{BG}" transform="rotate({a} {cx} 46)"/>' for a in (0, 120, 240))
        + "</g>" for cx in (58, 98))
    btn = lambda cx, fill, icon: (f'<circle cx="{cx}" cy="46" r="20" fill="{fill}" stroke="{LINE}"/>' + icon)
    body = (
        frame(w, h, 46, "#201e1b")
        + f'<rect x="28" y="22" width="100" height="48" rx="12" fill="{BG}" stroke="{LINE}"/>' + reels
        + titles
        + f'<rect x="600" y="44" width="110" height="4" rx="2" fill="{LINE}"/>'
          f'<rect class="bar" x="600" y="44" width="110" height="4" rx="2" fill="{MUSTARD}"/>'
        + btn(752, CARD, f'<path d="M745 46 L756 39 V53Z M758 39 h3 v14 h-3z" fill="{CREAM}" transform="rotate(180 752 46)"/>')
        + btn(800, "#2a3566", f'<path d="M794 37 L810 46 L794 55Z" fill="{CREAM}"/>')
        + btn(848, CARD, f'<path d="M842 39 L853 46 L842 53Z M855 39 h3 v14 h-3z" fill="{CREAM}"/>')
    )
    css = (f".trk{{opacity:0;animation:trk {dur}s infinite}}"
           f"@keyframes trk{{0%{{opacity:0;transform:translateY(6px)}}3%,{100 / n - 3:.1f}%{{opacity:1;transform:none}}{100 / n:.1f}%,100%{{opacity:0}}}}"
           ".bar{transform-origin:600px 46px;animation:bar 3s linear infinite}"
           "@media (prefers-reduced-motion:reduce){.t0{opacity:1}}"
           "@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}")
    svg("nowplaying", w, h, body, css, "Now playing: " + ", ".join(tr[2] for tr in TRACKS))


def receipt():
    w, h = 440, 600
    top, bot = 62, 560
    pts = [f"{x},{top - (7 if i % 2 else 0)}" for i, x in enumerate(range(36, 405, 12))]
    pts += [f"{x},{bot + (7 if i % 2 else 0)}" for i, x in enumerate(range(404, 35, -12))]
    lines, y, i = [], 150, 0
    for row in RECEIPT:
        if row is None:
            lines.append(f'<g class="pr" style="animation-delay:{.4 + i * .18:.2f}s">'
                         + t(60, y - 4, "- " * 26, "m", 11, MUTED) + "</g>")
            y += 24
        else:
            k, v = row
            lines.append(f'<g class="pr" style="animation-delay:{.4 + i * .18:.2f}s">'
                         + t(60, y, k, "m", 12.5, MUTED) + t(380, y, v, "mb", 12.5, PAPER_INK, 'text-anchor="end"') + "</g>")
            y += 26
        i += 1
    bars = "".join(f'<rect x="{110 + j * 7}" y="{y + 8}" width="{[2, 4, 1, 3][j % 4]}" height="34" fill="{PAPER_INK}"/>'
                   for j in range(31))
    body = (
        frame(w, h, 18)
        + f'<g transform="rotate(1.2 220 300)"><polygon points="{" ".join(pts)}" fill="#000" opacity=".35" transform="translate(5 7)"/>'
          f'<polygon points="{" ".join(pts)}" fill="{PAPER}"/>'
        + t(220, 94, "RECEIPT · MADE FOR RECRUITERS", "mb", 13, PAPER_INK, 'text-anchor="middle" letter-spacing="1"')
        + t(60, 114, "30-second read", "m", 11, MUTED) + t(380, 114, "#0001", "m", 11, MUTED, 'text-anchor="end"')
        + "".join(lines)
        + f'<g class="pr" style="animation-delay:{.4 + i * .18:.2f}s">{bars}'
        + t(220, y + 66, "THANK YOU, COME AGAIN ✶", "mb", 12, POSTER, 'text-anchor="middle" letter-spacing="1"')
        + "</g></g>"
    )
    css = ".pr{animation:fadeup .35s ease-out both}"
    svg("receipt", w, h, body, css, "Receipt for recruiters: " + "; ".join(f"{k}: {v}" for k, v in filter(None, RECEIPT)))


def genres():
    w, h = 440, 600
    spots = [(118, 190, -6), (318, 226, 5), (124, 412, 4), (320, 446, -5)]
    stickers = []
    for idx, ((title, sub, fill, ink), (cx, cy, rot)) in enumerate(zip(GENRES, spots)):
        r = 90
        n_t, n_s = len(title), len(sub)
        block = n_t * 24 + n_s * 16
        y0 = cy - block / 2 + 20
        txt = "".join(t(cx, y0 + k * 24, s, "d", 22, ink, 'text-anchor="middle"') for k, s in enumerate(title))
        txt += "".join(t(cx, y0 + n_t * 24 + 4 + k * 16, s, "m", 11, ink, 'text-anchor="middle" opacity=".85"')
                       for k, s in enumerate(sub))
        stickers.append(
            f'<g class="stk" style="animation-delay:{idx * .7}s"><g transform="rotate({rot} {cx} {cy})">'
            f'<circle cx="{cx + 4}" cy="{cy + 6}" r="{r}" fill="#000" opacity=".35"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 7}" fill="none" stroke="{ink}" stroke-opacity=".25" stroke-dasharray="3 5"/>'
            f"{txt}</g></g>")
    sparks = "".join(
        f'<text x="{x}" y="{y}" class="h spark" font-size="26" fill="{MUSTARD}" style="animation-delay:{d}s">✶</text>'
        for x, y, d in ((392, 110, 0), (40, 300, .8), (226, 560, 1.6)))
    body = (frame(w, h, 18) + t(40, 70, "genres I play ↓", "h", 38, PERI) + "".join(stickers) + sparks)
    css = (".stk{animation:bob 4s ease-in-out infinite}"
           ".spark{animation:tw 2.4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}")
    svg("genres", w, h, body, css, "Genres I play: AI engineering, full-stack, DevOps, backend.")


def tools():
    w, h = 900, 190

    def row(items, y, cls, fill, ink):
        x, out = 0, []
        for s in items:
            cw = chip_w(s, 14) + 10
            out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="38" rx="19" fill="{fill}"/>'
                       + t(x + cw / 2, y + 25, s, "mb", 14, ink, 'text-anchor="middle"'))
            x += cw + 12
        one = "".join(out)
        return (f'<g class="{cls}" style="--w:{-x}px">{one}<g transform="translate({x} 0)">{one}</g></g>', x)

    r1, w1 = row(TOOLS_1, 72, "mq1", CARD, CREAM)
    r2, w2 = row(TOOLS_2, 124, "mq2", "#2a2633", PERI)
    body = (frame(w, h, 18) + t(32, 48, "tools I play with ↓", "h", 34, MUSTARD)
            + '<clipPath id="c"><rect x="1" y="60" width="898" height="110"/></clipPath>'
            + f'<g clip-path="url(#c)">{r1}{r2}</g>'
            + f'<rect x="1" y="60" width="40" height="110" fill="url(#fl)"/><rect x="859" y="60" width="40" height="110" fill="url(#fr)"/>'
            + f'<linearGradient id="fl"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
            + f'<linearGradient id="fr"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>')
    css = (f".mq1{{animation:mq1 {w1 / 40:.0f}s linear infinite}}@keyframes mq1{{to{{transform:translateX({-w1}px)}}}}"
           f".mq2{{animation:mq2 {w2 / 40:.0f}s linear infinite}}@keyframes mq2{{from{{transform:translateX({-w2}px)}}to{{transform:translateX(0)}}}}")
    svg("tools", w, h, body, css, "Tools: " + ", ".join(TOOLS_1 + TOOLS_2))


def label(name, big, note, color=CREAM, note_color=PERI):
    w, h = 900, 84
    bw = len(big) * 30 * .78
    body = (frame(w, h, 16) + t(32, 56, big, "d", 30, color, 'letter-spacing="1"')
            + t(48 + bw, 56, note, "h", 30, note_color)
            + f'<circle cx="860" cy="42" r="16" fill="{MUSTARD}" class="pulse"/><circle cx="860" cy="42" r="5" fill="{BG}"/>')
    css = ".pulse{transform-origin:860px 42px;animation:pl 2s ease-in-out infinite}@keyframes pl{50%{transform:scale(.8)}}"
    svg(name, w, h, body, css, f"{big}: {note}")


def track(file, num, title, hook, desc, stack, tag, label_color):
    w, h = 440, 260
    body = (
        frame(w, h, 18, CARD)
        + vinyl(372, 70, 46, label_color, "spin")
        + t(26, 40, f"SIDE A · TRACK {num}", "mb", 11, MUTED, 'letter-spacing="1.5"')
        + t(26, 88, num, "d", 40, MUSTARD)
        + t(26, 132, title, "d", 27 if len(title) < 15 else 23, CREAM)
        + t(26, 160, hook, "s", 21, PERI)
        + t(26, 188, desc[0], "m", 11.5, MUTED) + t(26, 205, desc[1], "m", 11.5, MUTED)
        + chips(26, 238, stack)
        + f'<rect x="172" y="25" width="{chip_w(tag, 10)}" height="21" rx="4" fill="{label_color}"/>'
        + t(172 + chip_w(tag, 10) / 2, 39.5, tag, "mb", 10, PAPER_INK if label_color != POSTER else CREAM, 'text-anchor="middle"')
    )
    svg(f"track-{file}", w, h, body, ".spin{animation:spin 5s linear infinite}", f"Track {num}: {title}, {hook}")


def deep_cut(file, title, hook, stack, i):
    w, h = 290, 170
    body = (
        frame(w, h, 16, CARD)
        + vinyl(248, 40, 24, [POSTER, MUSTARD, PERI][i % 3], "spin")
        + t(20, 34, f"SIDE B · 0{i + 1}", "mb", 10, MUTED, 'letter-spacing="1.5"')
        + t(20, 82, title, "d", 19 if len(title) < 20 else 16.5, CREAM)
        + t(20, 108, hook, "s", 18, PERI)
        + chips(20, 148, stack, 10)
    )
    svg(f"cut-{file}", w, h, body, ".spin{animation:spin 6s linear infinite}", f"Deep cut: {title}, {hook}")


def liner():
    w, h = 900, 420
    rows, y = [], 112
    for i, (kind, s) in enumerate(LINER):
        el = (t(70, y, s, "h", 32, POSTER) if kind == "hand" else t(70, y, s, "s", 24, PAPER_INK))
        rows.append(f'<g class="ln" style="animation-delay:{.3 + i * .35:.2f}s">{el}</g>')
        y += 42 if kind == "hand" else 36
    body = (
        frame(w, h, 18)
        + f'<g transform="rotate(-.6 450 210)"><rect x="34" y="30" width="832" height="362" fill="#000" opacity=".35" transform="translate(6 8)"/>'
          f'<rect x="34" y="30" width="832" height="362" fill="{PAPER}"/><rect x="34" y="30" width="832" height="362" filter="url(#grain)"/>'
        + t(70, 70, "LINER NOTES", "mb", 13, MUTED, 'letter-spacing="3"')
        + t(830, 70, "VOL 01", "mb", 13, MUTED, 'text-anchor="end" letter-spacing="3"')
        + "".join(rows) + "</g>"
    )
    svg("liner", w, h, body, ".ln{animation:fadeup .6s ease-out both}", " ".join(s for _, s in LINER))


def credits():
    w, h = 900, 150
    body = (
        frame(w, h, 18)
        + t(32, 46, "CREDITS · WRITE TO", "mb", 12, MUTED, 'letter-spacing="3"')
        + t(32, 92, "Written, produced and shipped by Justin Santosh.", "s", 28, CREAM)
        + t(32, 124, "recorded at IIIT Naya Raipur · mixed in VS Code · mastered in prod", "m", 12, MUTED)
        + vinyl(830, 75, 48, POSTER, "spin")
    )
    svg("credits", w, h, body, ".spin{animation:spin 6s linear infinite}", "Written, produced and shipped by Justin Santosh.")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    hero()
    now_playing()
    receipt()
    genres()
    tools()
    label("label-side-a", "SIDE A", "the hits — tap a track to open ↓")
    label("label-side-b", "SIDE B", "deep cuts ↓")
    label("label-wrapped", "WRAPPED", "my year in commits ↓")
    for tr in TRACKS:
        track(*tr)
    for i, dc in enumerate(DEEP_CUTS):
        deep_cut(*dc, i)
    liner()
    credits()
