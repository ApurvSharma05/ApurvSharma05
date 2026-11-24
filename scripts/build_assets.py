#!/usr/bin/env python3
"""
Builds the artwork used by the profile README (everything in assets/).

All text is turned into vector outlines. GitHub does not load web fonts inside
README images, so this is what keeps the type looking the same on every phone,
laptop and browser, and it lets the layout measure every word exactly.

    pip install -r scripts/requirements.txt
    python scripts/build_assets.py

To change wording, projects or the tech stack, edit the CONTENT section below
and run the script again. It writes a dark and a light version of each image.
"""
from __future__ import annotations

import io
import json
import random
from html import escape
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "scripts" / "fonts"
ASSETS = ROOT / "assets"
ICONS = json.loads((ROOT / "scripts" / "icons.json").read_text())

# ════════════════════════════════════════════════════════════════════════════
# CONTENT
# ════════════════════════════════════════════════════════════════════════════

NAME = "Apurv Sharma"
GREETING = "› hi there, i'm"
ROLES = [
    "AI & Data Engineer in the making",
    "building LLM agents & RAG systems",
    "turning messy data into pipelines",
    "open to AI & data internships",
]
HEADER_CHIPS = [
    ("violet", "B.Tech CSE · Data Science"),
    ("pink", "ABES Engineering College ’27"),
    ("cyan", "Ghaziabad, India"),
]
# The four layers of the little network drawn in the banner.
NETWORK_LABELS = ["ingest", "embed", "reason", "ship"]

PROJECTS = [
    dict(
        slug="news-agent", accent="violet", kind="AUTONOMOUS AGENT",
        title="EPC Competitor Intel Agent",
        desc="Reads 23 news feeds every day, filters ~880 articles for 15 competitors "
             "and sends strategic briefings to Telegram, written by Llama 3.3 70B.",
        metrics=[("~880", "articles / run"), ("23", "news feeds"), ("30", "tests")],
        stack=["Groq", "Llama 3.3", "FastAPI", "SQLite", "Docker"],
    ),
    dict(
        slug="talk-to-syllabus", accent="pink", kind="RAG SYSTEM",
        title="Talk-to-Syllabus",
        desc="Chat with your course syllabus. Hybrid dense + BM25 retrieval fused with "
             "RRF, and every answer cites the exact page it came from.",
        metrics=[("hybrid", "dense + BM25"), ("page-level", "citations"), ("27", "tests")],
        stack=["Pinecone", "MiniLM", "Groq", "FastAPI", "Streamlit"],
    ),
    dict(
        slug="agentforge", accent="cyan", kind="MULTI-AGENT SYSTEM",
        title="AgentForge",
        desc="A research team made of AI agents that search, read, critique and write, "
             "turning scattered web pages into structured reports.",
        metrics=[("4", "AI agents"), ("API", "+ Streamlit UI"), ("33", "tests")],
        stack=["LangGraph", "LangChain", "Groq", "SerpAPI", "Streamlit"],
    ),
    dict(
        slug="ipl-analytics", accent="mint", kind="DATA ENGINEERING",
        title="IPL Analytics Platform",
        desc="Ball-by-ball analytics for 19 IPL seasons, with Pandera data contracts, "
             "rules-correct cricket metrics and a FastAPI service.",
        metrics=[("295K", "deliveries"), ("1,243", "matches"), ("19", "seasons")],
        stack=["pandas", "Pandera", "FastAPI", "Docker", "Jupyter"],
    ),
    dict(
        slug="cape", accent="amber", kind="AI DATA PIPELINE",
        title="CAPE",
        desc="Turns a list of company names into evidence-cited business profiles: "
             "finds each website, crawls it asynchronously and exports an audit-ready Excel workbook.",
        metrics=[("async", "httpx crawler"), ("cited", "evidence per field"), ("71", "tests")],
        stack=["Groq", "Ollama", "httpx", "asyncio", "Pydantic"],
    ),
    dict(
        slug="alfa", accent="sky", kind="DOCUMENT AI",
        title="ALFA",
        desc="Turns annual-report PDFs into financial fact-sheets in Excel. Gemini "
             "extracts, Pydantic validates, and a human reviews before export.",
        metrics=[("PDF", "to Excel"), ("human", "in the loop"), ("61", "tests")],
        stack=["Gemini", "pdfplumber", "Pydantic", "openpyxl", "Streamlit"],
    ),
]

# (category, accent, [(label, simple-icons slug or None)])
STACK = [
    ("LANGUAGES", "violet", [("Python", "python"), ("SQL", None)]),
    ("AI & LLMS", "pink", [
        ("LangGraph", "langgraph"), ("LangChain", "langchain"), ("Groq", None),
        ("Llama 3", "meta"), ("Gemini", "googlegemini"), ("Hugging Face", "huggingface"),
        ("Pinecone", None), ("Ollama", "ollama"),
    ]),
    ("DATA & ML", "cyan", [
        ("pandas", "pandas"), ("NumPy", "numpy"),
        ("Jupyter", "jupyter"), ("Plotly", "plotly"), ("Pandera", None),
    ]),
    ("BACKEND & APPS", "mint", [
        ("FastAPI", "fastapi"), ("Flask", "flask"), ("Streamlit", "streamlit"),
        ("Pydantic", "pydantic"), ("Telegram", "telegram"),
    ]),
    ("DATABASES", "amber", [("PostgreSQL", "postgresql"), ("SQLite", "sqlite")]),
    ("CLOUD & TOOLS", "sky", [
        ("AWS", None), ("Docker", "docker"), ("Git", "git"), ("GitHub", "github"),
        ("pytest", "pytest"),
    ]),
]

BUTTONS = [
    ("linkedin", "LinkedIn", "violet"),
    ("email", "Email me", "pink"),
    ("projects", "See my work", "cyan"),
]

FOOTER_TEXT = "thanks for stopping by"
FOOTER_SUB = "let's build something that ships"

# ════════════════════════════════════════════════════════════════════════════
# THEMES
# ════════════════════════════════════════════════════════════════════════════

THEMES = {
    "dark": dict(
        bg1="#0B0B1A", bg2="#131838", dots="#FFFFFF", dots_op=0.07,
        blobs=["#7C3AED", "#DB2777", "#0891B2"], blob_op=0.55,
        card1="#11152C", card2="#0B0F21", border="#252C4A",
        title="#EEF0FF", text="#D4D7EE", body="#A3A9C7", muted="#6E7598",
        chip_bg="#161C36", chip_border="#2A3256", chip_text="#C7CBE6",
        pill_bg="#FFFFFF", pill_bg_op=0.06, pill_border="#FFFFFF", pill_border_op=0.14,
        name=["#C4B5FD", "#F9A8D4", "#67E8F9"],
        accents=dict(violet="#A78BFA", pink="#F472B6", cyan="#22D3EE",
                     mint="#34D399", amber="#FBBF24", sky="#60A5FA"),
        node="#C4B5FD", edge="#A78BFA", edge_op=0.15, pulse="#67E8F9",
        wave=["#7C3AED", "#DB2777", "#0891B2"], wave_op=[0.35, 0.3, 0.45],
    ),
    "light": dict(
        bg1="#FCFAFF", bg2="#EEF0FF", dots="#3B2F6B", dots_op=0.09,
        blobs=["#C4B5FD", "#FBCFE8", "#A5F3FC"], blob_op=0.9,
        card1="#FFFFFF", card2="#FAF8FF", border="#E4DEF7",
        title="#1B1533", text="#2E2850", body="#4F4A6B", muted="#8A85A6",
        chip_bg="#F5F2FF", chip_border="#E2DAFB", chip_text="#4B3F8F",
        pill_bg="#FFFFFF", pill_bg_op=0.75, pill_border="#7C3AED", pill_border_op=0.18,
        name=["#7C3AED", "#DB2777", "#0891B2"],
        accents=dict(violet="#7C3AED", pink="#DB2777", cyan="#0891B2",
                     mint="#059669", amber="#D97706", sky="#2563EB"),
        node="#7C3AED", edge="#7C3AED", edge_op=0.14, pulse="#DB2777",
        wave=["#C4B5FD", "#FBCFE8", "#A5F3FC"], wave_op=[0.7, 0.6, 0.8],
    ),
}

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# ════════════════════════════════════════════════════════════════════════════
# TEXT ENGINE: harfbuzz shaping + glyph outlines
# ════════════════════════════════════════════════════════════════════════════


def num(n: float, nd: int = 1) -> str:
    s = f"{n:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


class Font:
    def __init__(self, filename: str, key: str):
        tt = TTFont(FONT_DIR / filename)
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        data = buf.getvalue()
        self.tt = TTFont(io.BytesIO(data))
        self.key = key
        self.upm = self.tt["head"].unitsPerEm
        self.cap = getattr(self.tt["OS/2"], "sCapHeight", 0) or self.upm * 0.7
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.cmap = self.tt.getBestCmap()
        self.hb = hb.Font(hb.Face(data))
        self._shapes: dict[str, list] = {}
        self._outlines: dict[int, str] = {}

    def shape(self, text: str):
        if text not in self._shapes:
            missing = sorted({c for c in text if ord(c) not in self.cmap})
            if missing:
                raise ValueError(f"font {self.key} has no glyph for {missing} in {text!r}")
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            hb.shape(self.hb, buf, {"kern": True, "liga": False, "calt": False})
            self._shapes[text] = [
                (i.codepoint, p.x_advance, p.x_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)
            ]
        return self._shapes[text]

    def outline(self, gid: int, transform=None) -> str:
        if transform is None and gid in self._outlines:
            return self._outlines[gid]
        pen = SVGPathPen(self.glyphs, ntos=lambda v: num(v, 1 if transform else 0))
        self.glyphs[self.order[gid]].draw(TransformPen(pen, transform) if transform else pen)
        d = pen.getCommands()
        if transform is None:
            self._outlines[gid] = d
        return d

    def carets(self, text: str, size: float, tracking: float = 0.0) -> list[float]:
        """x position after each glyph (index 0 = start)."""
        scale = size / self.upm
        xs, x = [0.0], 0.0
        for _, adv, _ in self.shape(text):
            x += adv * scale + tracking
            xs.append(x)
        return xs

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        return self.carets(text, size, tracking)[-1] - (tracking if text else 0)

    def wrap(self, text: str, size: float, max_w: float) -> list[str]:
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if cur and self.width(trial, size) > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        return lines + ([cur] if cur else [])


SG4 = Font("space-grotesk-latin-400-normal.woff2", "a")
SG5 = Font("space-grotesk-latin-500-normal.woff2", "b")
SG7 = Font("space-grotesk-latin-700-normal.woff2", "c")
MONO = Font("jetbrains-mono-latin-500-normal.woff2", "m")


class Svg:
    def __init__(self, w: float, h: float, title: str):
        self.w, self.h, self.title = w, h, title
        self.defs: list[str] = []
        self.css: list[str] = []
        self.body: list[str] = []
        self._glyphs: dict[str, str] = {}
        self._icons: set[str] = set()
        self._n = 0

    def uid(self, prefix: str = "u") -> str:
        self._n += 1
        return f"{prefix}{self._n}"

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def text(self, s: str, x: float, y: float, font: Font, size: float, fill: str,
             anchor: str = "start", tracking: float = 0.0, extra: str = "") -> str:
        """Text as <use> references to shared glyph outlines (small files)."""
        x = self._anchor(s, x, font, size, tracking, anchor)
        scale = size / font.upm
        pen, uses = 0.0, []
        for gid, adv, xoff in font.shape(s):
            d = font.outline(gid)
            if d:
                ref = f"{font.key}{gid}"
                self._glyphs.setdefault(ref, d)
                uses.append(f'<use xlink:href="#{ref}" x="{num(pen + xoff, 0)}"/>')
            pen += adv + tracking / scale
        return (f'<g transform="translate({num(x)} {num(y)}) scale({num(scale, 5)} {num(-scale, 5)})"'
                f' fill="{fill}"{extra}>{"".join(uses)}</g>')

    def text_path(self, s: str, x: float, y: float, font: Font, size: float, fill: str,
                  anchor: str = "start", tracking: float = 0.0, extra: str = "") -> str:
        """Text baked into one path in page coordinates (needed for gradient fills)."""
        x = self._anchor(s, x, font, size, tracking, anchor)
        scale = size / font.upm
        pen, ds = 0.0, []
        for gid, adv, xoff in font.shape(s):
            ds.append(font.outline(gid, (scale, 0, 0, -scale, x + (pen + xoff) * scale, y)))
            pen += adv + tracking / scale
        return f'<path d="{"".join(ds)}" fill="{fill}"{extra}/>'

    def icon(self, slug: str, x: float, y: float, size: float, fill: str) -> str:
        if slug not in self._icons:
            self._icons.add(slug)
            self.defs.append(f'<path id="ic-{slug}" d="{ICONS[slug]}"/>')
        return (f'<use xlink:href="#ic-{slug}" transform="translate({num(x)} {num(y)}) '
                f'scale({num(size / 24, 4)})" fill="{fill}"/>')

    @staticmethod
    def _anchor(s, x, font, size, tracking, anchor):
        if anchor == "start":
            return x
        w = font.width(s, size, tracking)
        return x - (w / 2 if anchor == "middle" else w)

    def render(self) -> str:
        glyphs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in self._glyphs.items())
        css = f"<style>{''.join(self.css)}{REDUCED_MOTION}</style>" if self.css else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{num(self.w)}" height="{num(self.h)}" viewBox="0 0 {num(self.w)} {num(self.h)}" '
            f'fill="none" role="img" aria-labelledby="title">'
            f'<title id="title">{escape(self.title)}</title>{css}'
            f'<defs>{glyphs}{"".join(self.defs)}</defs>{"".join(self.body)}</svg>\n'
        )


def grad(id_: str, stops: list[tuple[float, str, float]], x1=0, y1=0, x2=1, y2=0, user=None) -> str:
    units = ""
    if user:
        x1, y1, x2, y2 = user
        units = ' gradientUnits="userSpaceOnUse"'
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return (f'<linearGradient id="{id_}" x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" '
            f'y2="{num(y2)}"{units}>{s}</linearGradient>')


def radial(id_: str, color: str, alpha: float) -> str:
    return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{color}" stop-opacity="{alpha}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


# ════════════════════════════════════════════════════════════════════════════
# HEADER BANNER
# ════════════════════════════════════════════════════════════════════════════


def build_header(theme: str) -> str:
    t = THEMES[theme]
    W, H = 1200, 420
    s = Svg(W, H, f"{NAME}: {', '.join(ROLES[:3])}")
    s.defs += [
        grad("bg", [(0, t["bg1"], 1), (1, t["bg2"], 1)], 0, 0, 1, 1),
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>',
        f'<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{t["dots"]}" fill-opacity="{t["dots_op"]}"/></pattern>',
        grad("namefill", [(0, t["name"][0], 1), (0.55, t["name"][1], 1), (1, t["name"][2], 1)],
             user=(80, 0, 660, 0)),
        f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="3"/></filter>',
    ]
    for i, c in enumerate(t["blobs"]):
        s.defs.append(radial(f"blob{i}", c, t["blob_op"]))
    s.css += [
        "@keyframes d0{50%{transform:translate(140px,50px)}}",
        "@keyframes d1{50%{transform:translate(-160px,-40px)}}",
        "@keyframes d2{50%{transform:translate(-90px,70px)}}",
        "@keyframes beat{0%,100%{opacity:.55}50%{opacity:1}}",
        ".b0{animation:d0 19s ease-in-out infinite}.b1{animation:d1 23s ease-in-out infinite}"
        ".b2{animation:d2 17s ease-in-out infinite}",
        ".n{animation:beat 3.2s ease-in-out infinite}",
    ]

    layer = [f'<rect width="{W}" height="{H}" fill="url(#bg)"/>']
    for i, (cx, cy, r) in enumerate([(170, 60, 360), (1060, 400, 340), (720, -30, 280)]):
        layer.append(f'<circle class="b{i}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#blob{i})"/>')
    layer.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')

    # ── a tiny neural network: data flows left to right ──
    xs = [790, 890, 990, 1090]
    counts = [3, 5, 5, 3]
    nodes = [[(x, 196 + (k - (n - 1) / 2) * 62) for k in range(n)] for x, n in zip(xs, counts)]
    edges = []
    for a, b in zip(nodes, nodes[1:]):
        for p in a:
            for q in b:
                edges.append(f'M{num(p[0])} {num(p[1])}L{num(q[0])} {num(q[1])}')
    layer.append(f'<path d="{"".join(edges)}" stroke="{t["edge"]}" stroke-opacity="{t["edge_op"]}" '
                 f'stroke-width="1.2"/>')
    rng = random.Random(11)
    for i in range(7):
        pts = [rng.choice(col) for col in nodes]
        d = "M" + "L".join(f"{num(x)} {num(y)}" for x, y in pts)
        layer.append(f'<path d="{d}" stroke="{t["pulse"]}" stroke-opacity=".32" stroke-width="1.6"/>')
        for r, op, flt in [(7, 0.35, ' filter="url(#glow)"'), (3.2, 1, "")]:
            layer.append(
                f'<circle r="{r}" fill="{t["pulse"]}" opacity="0"{flt}>'
                f'<animateMotion dur="3.4s" begin="{num(i * 0.55, 2)}s" repeatCount="indefinite" path="{d}"/>'
                f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;.12;.85;1" '
                f'dur="3.4s" begin="{num(i * 0.55, 2)}s" repeatCount="indefinite"/></circle>')
    for li, col in enumerate(nodes):
        for x, y in col:
            layer.append(
                f'<circle cx="{num(x)}" cy="{num(y)}" r="8" fill="{t["bg2"]}" stroke="{t["node"]}" '
                f'stroke-width="2"/><circle class="n" style="animation-delay:{num(li * 0.4, 1)}s" '
                f'cx="{num(x)}" cy="{num(y)}" r="3.6" fill="{t["node"]}"/>')
    for x, label in zip(xs, NETWORK_LABELS):
        layer.append(s.text(label, x, 386, MONO, 15, t["muted"], anchor="middle"))

    # ── greeting, name, typing roles ──
    acc = t["accents"]
    layer.append(s.text(GREETING, 82, 120, MONO, 23, acc["violet"]))
    name_size = 92
    while SG7.width(NAME, name_size, -1.5) > 600:
        name_size -= 2
    layer.append(s.text_path(NAME, 78, 210, SG7, name_size, "url(#namefill)", tracking=-1.5))
    layer.append(typing_lines(s, t, 82, 266))

    # ── chips ──
    fs = 18.0
    while sum(SG5.width(label, fs) + 48 + 12 for _, label in HEADER_CHIPS) > 860 - 82:
        fs -= 0.5
    x = 82
    for accent, label in HEADER_CHIPS:
        w = SG5.width(label, fs) + 48
        layer.append(
            f'<rect x="{num(x)}" y="300" width="{num(w)}" height="42" rx="21" fill="{t["pill_bg"]}" '
            f'fill-opacity="{t["pill_bg_op"]}" stroke="{t["pill_border"]}" '
            f'stroke-opacity="{t["pill_border_op"]}"/>'
            f'<circle cx="{num(x + 20)}" cy="321" r="5" fill="{acc[accent]}"/>')
        layer.append(s.text(label, x + 34, 321 + fs * 0.36, SG5, fs, t["text"]))
        x += w + 12

    s.add(f'<g clip-path="url(#frame)">{"".join(layer)}</g>')
    return s.render()


def typing_lines(s: Svg, t: dict, x0: float, y: float) -> str:
    """Each role is typed out, held, then deleted, one after another, forever."""
    size, type_t, del_t, hold, gap = 27, 0.06, 0.028, 2.1, 0.4
    events = []  # (time, line index, revealed width)
    clock = 0.0
    for i, role in enumerate(ROLES):
        caret = MONO.carets(role, size)
        n = len(caret) - 1
        for k in range(1, n + 1):
            events.append((clock + k * type_t, i, caret[k]))
        start_del = clock + n * type_t + hold
        for k in range(n - 1, -1, -1):
            events.append((start_del + (n - k) * del_t, i, caret[k]))
        clock = start_del + n * del_t + gap
    total = clock
    out = []
    for i, role in enumerate(ROLES):
        mine = [(tm, w) for tm, li, w in events if li == i]
        keys = ["0"] + [num(tm / total, 5) for tm, _ in mine]
        vals = ["0"] + [num(w, 1) for _, w in mine]
        cid = s.uid("type")
        s.defs.append(
            f'<clipPath id="{cid}"><rect x="{num(x0)}" y="{num(y - 30)}" width="0" height="44">'
            f'<animate attributeName="width" values="{";".join(vals)}" keyTimes="{";".join(keys)}" '
            f'calcMode="discrete" dur="{num(total, 3)}s" repeatCount="indefinite"/></rect></clipPath>')
        out.append(f'<g clip-path="url(#{cid})">{s.text(role, x0, y, MONO, size, t["title"])}</g>')
    keys = ["0"] + [num(tm / total, 5) for tm, _, _ in events]
    vals = [num(x0 + 3)] + [num(x0 + w + 3, 1) for _, _, w in events]
    out.append(
        f'<rect x="{num(x0 + 3)}" y="{num(y - 24)}" width="13" height="30" rx="2" '
        f'fill="{t["accents"]["pink"]}">'
        f'<animate attributeName="x" values="{";".join(vals)}" keyTimes="{";".join(keys)}" '
        f'calcMode="discrete" dur="{num(total, 3)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;.15;1" keyTimes="0;.5;1" calcMode="discrete" '
        f'dur="1s" repeatCount="indefinite"/></rect>')
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# PROJECT CARDS
# ════════════════════════════════════════════════════════════════════════════


def card_frame(s: Svg, t: dict, W: float, H: float, accent: str, glow_at=(0.92, 0.0)) -> str:
    s.defs += [
        grad("cardbg", [(0, t["card1"], 1), (1, t["card2"], 1)], 0, 0, 0.4, 1),
        radial("cardglow", accent, 0.22 if t is THEMES["dark"] else 0.16),
        f'<clipPath id="cardclip"><rect x="1" y="1" width="{num(W - 2)}" height="{num(H - 2)}" rx="18"/></clipPath>',
        grad("edge", [(0, accent, 0.9), (0.5, accent, 0.15), (1, accent, 0)], user=(0, 0, W * 0.7, 0)),
    ]
    gx, gy = W * glow_at[0], H * glow_at[1]
    return (
        f'<rect x="1" y="1" width="{num(W - 2)}" height="{num(H - 2)}" rx="18" fill="url(#cardbg)" '
        f'stroke="{t["border"]}" stroke-width="1.5"/>'
        f'<g clip-path="url(#cardclip)"><circle cx="{num(gx)}" cy="{num(gy)}" r="230" fill="url(#cardglow)"/>'
        f'<rect x="0" y="0" width="{num(W)}" height="3" fill="url(#edge)"/></g>'
    )


def build_card(index: int, p: dict, theme: str) -> str:
    t = THEMES[theme]
    acc = t["accents"][p["accent"]]
    W, H, pad = 480, 286, 28
    s = Svg(W, H, f'{p["title"]}: {p["desc"]}')
    out = [card_frame(s, t, W, H, acc)]

    out.append(s.text(f"{index:02d}", pad, 46, MONO, 13.5, acc))
    out.append(s.text(p["kind"], pad + 31, 46, MONO, 12, t["muted"], tracking=1.5))
    # "open" arrow, top right
    cx, cy = W - pad - 14, 40
    out.append(
        f'<circle cx="{cx}" cy="{cy}" r="16" fill="{acc}" fill-opacity=".12" stroke="{acc}" '
        f'stroke-opacity=".4"/><path d="M{cx - 5} {cy + 5}L{cx + 5} {cy - 5}M{cx - 3} {cy - 5}H{cx + 5}V{cy + 3}" '
        f'stroke="{acc}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')

    title_size = 25
    while SG7.width(p["title"], title_size, -0.4) > W - 2 * pad - 40:
        title_size -= 1
    out.append(s.text(p["title"], pad, 88, SG7, title_size, t["title"], tracking=-0.4))

    lines = SG4.wrap(p["desc"], 14.5, W - 2 * pad)
    if len(lines) > 3:
        raise ValueError(f'description of {p["title"]} needs {len(lines)} lines; keep it to 3')
    for k, line in enumerate(lines):
        out.append(s.text(line, pad, 116 + k * 21.5, SG4, 14.5, t["body"]))

    x = pad
    for value, label in p["metrics"]:
        out.append(s.text(value, x, 206, SG7, 21, acc, tracking=-0.3))
        out.append(s.text(label, x, 225, MONO, 11.5, t["muted"]))
        x += max(SG7.width(value, 21), MONO.width(label, 11.5)) + 28
    if x - 30 > W - pad:
        raise ValueError(f'metrics of {p["title"]} are too wide')

    x, y = pad, H - pad - 24
    for chip in p["stack"]:
        w = MONO.width(chip, 12) + 20
        if x + w > W - pad:
            raise ValueError(f'tech chips of {p["title"]} do not fit; drop "{chip}" or shorten it')
        out.append(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="26" rx="13" '
            f'fill="{t["chip_bg"]}" stroke="{t["chip_border"]}"/>')
        out.append(s.text(chip, x + 10, y + 17.3, MONO, 12, t["chip_text"]))
        x += w + 7
    s.add(*out)
    return s.render()


# ════════════════════════════════════════════════════════════════════════════
# TECH STACK PANEL
# ════════════════════════════════════════════════════════════════════════════


def build_stack(theme: str) -> str:
    t = THEMES[theme]
    W, pad, label_w = 1000, 34, 196
    chip_h, gap, row_gap, fs = 42, 10, 16, 17
    rows, y = [], pad
    for cat, accent, items in STACK:
        x, row_y, row = pad + label_w, y, []
        for label, slug in items:
            w = 16 + 20 + 10 + SG5.width(label, fs) + 18
            if x + w > W - pad:
                x, row_y = pad + label_w, row_y + chip_h + gap
            row.append((x, row_y, w, label, slug))
            x += w + gap
        rows.append((cat, accent, y, row))
        y = row_y + chip_h + row_gap
    H = y - row_gap + pad
    s = Svg(W, H, "Tech stack: " + "; ".join(
        f"{c.title()}: {', '.join(l for l, _ in items)}" for c, _, items in STACK))
    out = [card_frame(s, t, W, H, t["accents"]["violet"], glow_at=(0.97, 0.0))]
    for cat, accent, y0, row in rows:
        acc = t["accents"][accent]
        out.append(f'<circle cx="{pad + 5}" cy="{num(y0 + chip_h / 2)}" r="4" fill="{acc}"/>')
        out.append(s.text(cat, pad + 18, y0 + chip_h / 2 + 4.8, MONO, 13.5, t["muted"], tracking=1.3))
        for x, cy, w, label, slug in row:
            out.append(
                f'<rect x="{num(x)}" y="{num(cy)}" width="{num(w)}" height="{chip_h}" rx="{chip_h / 2}" '
                f'fill="{t["chip_bg"]}" stroke="{t["chip_border"]}"/>')
            ix, iy = x + 16, cy + (chip_h - 20) / 2
            if slug:
                out.append(s.icon(slug, ix, iy, 20, acc))
            else:
                out.append(f'<rect x="{num(ix + 3.5)}" y="{num(iy + 3.5)}" width="13" height="13" rx="3.5" '
                           f'fill="{acc}" transform="rotate(45 {num(ix + 10)} {num(iy + 10)})"/>')
            out.append(s.text(label, ix + 30, cy + chip_h / 2 + 6, SG5, fs, t["text"]))
    s.add(*out)
    return s.render()


# ════════════════════════════════════════════════════════════════════════════
# BUTTONS AND FOOTER
# ════════════════════════════════════════════════════════════════════════════


def button_icon(kind: str, x: float, cy: float, c: str, t: dict, s: Svg) -> str:
    if kind == "linkedin":
        return (f'<rect x="{num(x)}" y="{num(cy - 10)}" width="20" height="20" rx="4.5" fill="{c}"/>'
                + s.text("in", x + 10, cy + 5.5, SG7, 14, t["card1"], anchor="middle"))
    if kind == "email":
        return (f'<rect x="{num(x)}" y="{num(cy - 8)}" width="21" height="16" rx="3.5" stroke="{c}" stroke-width="2"/>'
                f'<path d="M{num(x + 2)} {num(cy - 5)}L{num(x + 10.5)} {num(cy + 1.5)}L{num(x + 19)} {num(cy - 5)}" '
                f'stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<path d="M{num(x + 10)} {num(cy - 9)}V{num(cy + 8)}M{num(x + 3)} {num(cy + 1)}L{num(x + 10)} '
            f'{num(cy + 8)}L{num(x + 17)} {num(cy + 1)}" stroke="{c}" stroke-width="2.2" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def build_button(kind: str, label: str, accent: str, theme: str) -> str:
    t = THEMES[theme]
    acc = t["accents"][accent]
    fs, H = 16, 50
    W = 22 + 21 + 11 + SG5.width(label, fs) + 24
    s = Svg(W, H, label)
    s.defs.append(grad("btn", [(0, acc, 0.16), (1, acc, 0.04)]))
    s.add(f'<rect x="1" y="1" width="{num(W - 2)}" height="{H - 2}" rx="{(H - 2) / 2}" fill="{t["card1"]}"/>'
          f'<rect x="1" y="1" width="{num(W - 2)}" height="{H - 2}" rx="{(H - 2) / 2}" fill="url(#btn)" '
          f'stroke="{acc}" stroke-opacity=".55" stroke-width="1.5"/>',
          button_icon(kind, 22, H / 2, acc, t, s),
          s.text(label, 22 + 21 + 11, H / 2 + 5.6, SG5, fs, t["title"]))
    return s.render()


def build_footer(theme: str) -> str:
    t = THEMES[theme]
    W, H = 1200, 190
    s = Svg(W, H, f"{FOOTER_TEXT}. {FOOTER_SUB}.")
    s.css += [
        "@keyframes w{to{transform:translateX(-600px)}}",
        ".w0{animation:w 16s linear infinite}.w1{animation:w 11s linear infinite reverse}"
        ".w2{animation:w 21s linear infinite}",
    ]
    waves = []
    for i, (base, amp) in enumerate([(112, 24), (130, 19), (150, 14)]):
        pts = [f"M0 {base}"]
        for k in range(6):  # 6 humps of 300px covers 1800px; animation shifts by 600px
            x0 = k * 300
            pts.append(f"Q{x0 + 75} {base - amp} {x0 + 150} {base}T{x0 + 300} {base}")
        pts.append(f"V{H}H0Z")
        waves.append(f'<path class="w{i}" d="{"".join(pts)}" fill="{t["wave"][i]}" '
                     f'fill-opacity="{t["wave_op"][i]}"/>')
    sparkle = (f'<path d="M0 -9C1 -2 2 -1 9 0C2 1 1 2 0 9C-1 2 -2 1 -9 0C-2 -1 -1 -2 0 -9Z" '
               f'fill="{t["accents"]["pink"]}"/>')
    tw = SG7.width(FOOTER_TEXT, 24, -0.3)
    s.add(*waves,
          s.text(FOOTER_TEXT, W / 2, 56, SG7, 24, t["title"], anchor="middle", tracking=-0.3),
          f'<g transform="translate({num(W / 2 - tw / 2 - 22)} 48)">{sparkle}</g>',
          f'<g transform="translate({num(W / 2 + tw / 2 + 22)} 48)">{sparkle}</g>',
          s.text(FOOTER_SUB, W / 2, 84, MONO, 14, t["muted"], anchor="middle"))
    return s.render()


# ════════════════════════════════════════════════════════════════════════════


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    written = []

    def write(name: str, svg: str) -> None:
        (ASSETS / name).write_text(svg, encoding="utf-8")
        written.append((name, len(svg.encode())))

    for theme in THEMES:
        write(f"header-{theme}.svg", build_header(theme))
        write(f"stack-{theme}.svg", build_stack(theme))
        write(f"footer-{theme}.svg", build_footer(theme))
        for i, p in enumerate(PROJECTS, 1):
            write(f"card-{p['slug']}-{theme}.svg", build_card(i, p, theme))
        for kind, label, accent in BUTTONS:
            write(f"btn-{kind}-{theme}.svg", build_button(kind, label, accent, theme))
    for name, size in written:
        print(f"  {name:<38} {size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
