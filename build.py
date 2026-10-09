#!/usr/bin/env python3
"""Build the website.

    content/config.yml, content/*.yml, content/bio.md, content/papers.bib
        + templates/index.html.j2 + static/
        -> _site/

Pages: _site/index.html, _site/news.html (all news), _site/bib/*.bib (one per paper + all).

Usage:
    python build.py            # build into _site/
    python build.py --serve    # build, then preview at http://localhost:8000
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import html as htmllib
import http.server
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from markdown_it import MarkdownIt
import pybtex.errors
from latex2mathml.converter import convert as tex_to_mathml
from pybtex.database import Entry, Person, parse_file
from pylatexenc.latex2text import LatexNodes2Text

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "_site"

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

_md = MarkdownIt("commonmark", {"typographer": True}).enable(["replacements", "smartquotes"])


def md_inline(text) -> Markup:
    return Markup(_md.renderInline(str(text)))


def md_block(text) -> Markup:
    return Markup(_md.render(str(text)))


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_LOOKUP = {m.lower(): i + 1 for i, m in enumerate(MONTHS)}
MONTH_LOOKUP.update({
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6, "july": 7,
    "august": 8, "september": 9, "sept": 9, "october": 10, "november": 11, "december": 12,
})
PRESENT = "present"


def parse_date(value, where: str):
    """Accepts 2024, "2024", "2024-10", a YAML date, or "present".

    Returns (year, month|None) or PRESENT, or None after recording an error.
    """
    if isinstance(value, dt.date):
        return (value.year, value.month)
    if isinstance(value, int):
        return (value, None)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("present", "now", "today", "current", "ongoing"):
            return PRESENT
        m = re.fullmatch(r"(\d{4})(?:-(\d{1,2}))?(?:-\d{1,2})?", v)
        if m:
            month = int(m.group(2)) if m.group(2) else None
            if month is not None and not 1 <= month <= 12:
                error(f"{where}: month must be 1-12, got {value!r}")
                return None
            return (int(m.group(1)), month)
    error(f"{where}: can't read the date {value!r}. Use 2024, 2024-10, or present.")
    return None


def fmt_date(d) -> str:
    if d == PRESENT:
        return "present"
    year, month = d
    return f"{MONTHS[month - 1]} {year}" if month else str(year)


def date_key(d) -> tuple:
    if d == PRESENT:
        return (9999, 13)
    if d is None:
        return (0, 0)
    return (d[0], d[1] or 0)


def fmt_range(start, end) -> list[str]:
    """Returns the parts of a date range, e.g. ["Nov 2024", "present"]."""
    if end is None or end == start:
        return [fmt_date(start)]
    if start != PRESENT and end != PRESENT and start[1] is None and end[1] is None:
        return [f"{start[0]}–{end[0]}"]
    return [fmt_date(start), fmt_date(end)]


# --------------------------------------------------------------------------
# YAML content
# --------------------------------------------------------------------------

def load_yaml(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        line = f":{mark.line + 1}" if mark else ""
        hint = ""
        bad_line = ""
        if mark:
            lines = path.read_text(encoding="utf-8").splitlines()
            bad_line = lines[mark.line] if mark.line < len(lines) else ""
        if re.search(r":\s*[{\[]", bad_line):
            hint = " (text starting with { or [ must be wrapped in quotes)"
        elif "mapping values are not allowed" in str(e):
            hint = " (a colon inside text? Wrap the text in quotes.)"
        error(f"{path.relative_to(ROOT)}{line}: invalid YAML: {getattr(e, 'problem', e)}{hint}")
        return None


def check_text(value, where: str) -> bool:
    if isinstance(value, bool):
        error(f"{where}: YAML turned this into {value}. Wrap the text in quotes.")
        return False
    if isinstance(value, (dict, list)):
        error(f"{where}: expected text, got a {type(value).__name__}. "
              "If the text contains a colon, wrap it in quotes.")
        return False
    return True


SCHEMAS = {
    "news":       {"required": ["date", "text"], "optional": []},
    "education":  {"required": ["degree", "institution", "start"],
                   "optional": ["end", "location", "details", "url"]},
    "experience": {"required": ["role", "organization", "start"],
                   "optional": ["end", "location", "details", "url"]},
    "teaching":   {"required": ["course", "role", "institution", "start"],
                   "optional": ["end", "details", "url"]},
    "awards":     {"required": ["title", "date"], "optional": ["details", "url"]},
    "supervision": {"required": ["student"],
                    "optional": ["title", "topic", "date", "degree", "role", "supervisor", "details", "url"]},
    "extracurricular": {"required": ["activity", "start"],
                        "optional": ["role", "end", "location", "details", "url"]},
}
# Any other content/<name>.yml listed in `sections` uses this generic shape.
GENERIC = {"required": ["title"], "optional": ["subtitle", "date", "start", "end", "location", "details", "url"]}
DATE_FIELDS = {"date", "start", "end"}


def load_section(name: str) -> list[dict]:
    path = CONTENT / f"{name}.yml"
    if not path.exists():
        return []
    data = load_yaml(path)
    if data is None:
        return []
    rel = path.relative_to(ROOT)
    if not isinstance(data, list):
        error(f"{rel}: expected a list of entries, each starting with '- '")
        return []
    schema = SCHEMAS.get(name, GENERIC)
    allowed = set(schema["required"]) | set(schema["optional"])
    items = []
    for i, raw in enumerate(data, 1):
        where = f"{rel}, entry {i}"
        if not isinstance(raw, dict):
            error(f"{where}: expected fields like 'key: value'")
            continue
        unknown = set(raw) - allowed
        if unknown:
            error(f"{where}: unknown field(s) {', '.join(sorted(unknown))}. "
                  f"Allowed: {', '.join(schema['required'] + schema['optional'])}")
        missing = [k for k in schema["required"] if raw.get(k) in (None, "")]
        if missing:
            error(f"{where}: missing {', '.join(missing)}")
            continue
        item = {}
        ok = True
        for key, value in raw.items():
            if key not in allowed or value is None:
                continue
            if key in DATE_FIELDS:
                d = parse_date(value, f"{where}, {key}")
                ok &= d is not None
                item[key] = d
            elif key == "url":
                ok &= check_text(value, f"{where}, url")
                item[key] = str(value).strip()
            else:
                ok &= check_text(value, f"{where}, {key}")
                item[key] = md_inline(str(value).strip())
        if not ok:
            continue
        if "start" in item:
            item["when"] = fmt_range(item["start"], item.get("end"))
            item["sort"] = (date_key(item.get("end") or item["start"]), date_key(item["start"]))
        elif "date" in item:
            item["when"] = [fmt_date(item["date"])]
            item["sort"] = (date_key(item["date"]),)
        elif name == "supervision":     # no date yet: a thesis in progress, listed first
            item["when"] = ["In progress"]
            item["sort"] = ((9999, 13),)
        else:
            item["when"] = []
            item["sort"] = ((0, 0),)
        item["_order"] = i
        items.append(item)
    # Newest first; entries with the same dates keep the order of the file.
    items.sort(key=lambda it: (tuple(-x for pair in it["sort"] for x in pair), it["_order"]))
    return items


def group_by_date(items: list[dict]) -> list[dict]:
    """Consecutive items with the same displayed date, as {when, items} groups."""
    groups = []
    for it in items:
        if groups and groups[-1]["when"] == it["when"]:
            groups[-1]["items"].append(it)
        else:
            groups.append({"when": it["when"], "items": [it]})
    return groups


def scan_todos() -> None:
    for path in sorted(CONTENT.glob("*")):
        if path.suffix not in (".yml", ".md", ".bib"):
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "TODO" in line:
                warn(f"{path.relative_to(ROOT)}:{n}: {line.strip()}")


# --------------------------------------------------------------------------
# Publications
# --------------------------------------------------------------------------

CATEGORIES = {
    #  key            label  heading
    "conference":  ("C", "Conference papers"),
    "journal":     ("J", "Journal articles"),
    "workshop":    ("W", "Workshop papers"),
    "preprint":    ("P", "Preprints"),
    "underreview": ("U", "Under review"),
}
CATEGORY_ALIASES = {
    "conference": "conference", "conf": "conference", "proceedings": "conference",
    "journal": "journal", "article": "journal",
    "workshop": "workshop",
    "preprint": "preprint", "arxiv": "preprint",
    "underreview": "underreview", "submitted": "underreview", "review": "underreview",
}

# Fields that only the website uses. They are stripped from the BibTeX shown on the page.
SITE_FIELDS = {
    "pubtype", "status", "venue", "award", "selected", "hidden", "equal",
    "pdf", "arxiv", "openreview", "code", "slides", "poster", "video", "project",
    "abstract", "keywords", "file", "urldate",
}
LINK_FIELDS = [
    ("pdf", "PDF"), ("arxiv", "arXiv"), ("openreview", "OpenReview"), ("doi", "DOI"),
    ("url", "Paper"), ("code", "Code"), ("project", "Project"), ("slides", "Slides"),
    ("poster", "Poster"), ("video", "Video"),
]

_latex = LatexNodes2Text(math_mode="text", strict_latex_spaces=True)


def delatex(s: str) -> str:
    s = _latex.latex_to_text(s)
    return re.sub(r"\s+", " ", s).strip()


_EM_OPEN, _EM_CLOSE = "\ue000", "\ue001"


def latex_html(s: str) -> Markup:
    """LaTeX text -> HTML: $...$ becomes MathML, \\emph{...} becomes <em>."""
    s = re.sub(r"<em>(.*?)</em>", r"\\emph{\1}", s)      # PMLR-style abstracts
    out = []
    for i, part in enumerate(re.split(r"(?<!\\)\$(.+?)(?<!\\)\$", s)):
        if i % 2:     # math
            try:
                out.append(tex_to_mathml(part))
            except Exception:
                out.append(htmllib.escape(delatex(f"${part}$")))
            continue
        part = re.sub(r"\\(?:emph|textit)\{([^{}]*)\}", _EM_OPEN + r"\1" + _EM_CLOSE, part)
        # Markdown-style *italics*, as in abstracts copied from arXiv or OpenReview
        part = re.sub(r"(?<![\w*])\*(?=\S)([^*]+?)(?<=\S)\*(?![\w*])", _EM_OPEN + r"\1" + _EM_CLOSE, part)
        text = htmllib.escape(_latex.latex_to_text(part), quote=False)
        out.append(text.replace(_EM_OPEN, "<em>").replace(_EM_CLOSE, "</em>"))
    html = re.sub(r"\s+", " ", "".join(out)).strip()
    # Keep punctuation right after a formula on the same line as the formula.
    html = re.sub(r"(<math\b(?:(?!</math>).)*</math>)([,.;:!?)]+)", r'<span class="nowrap">\1\2</span>', html)
    return Markup(html)


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", delatex(s))
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def norm(s: str | None) -> str:
    return re.sub(r"[\s_\-]", "", (s or "").lower())


def truthy(s: str | None) -> bool:
    return norm(s) in ("true", "yes", "1", "y")


def person_key(p: Person) -> tuple[str, str]:
    last = fold(" ".join(p.prelast_names + p.last_names))
    first = fold(" ".join(p.first_names + p.middle_names))
    return (last, first[:1])


def initials(names: list[str]) -> str:
    out = []
    for name in names:
        parts = [delatex(x) for x in name.split("-")]
        out.append("-".join(f"{x[0]}." for x in parts if x))
    return " ".join(out)


def format_person(p: Person, style: str) -> str:
    last = " ".join(delatex(x) for x in p.prelast_names + p.last_names)
    first_names = p.first_names + p.middle_names
    if style == "initials":
        first = initials(first_names)
    else:
        first = " ".join(delatex(x) for x in first_names)
    lineage = " ".join(delatex(x) for x in p.lineage_names)
    name = " ".join(x for x in (first, last) if x)
    return f"{name}, {lineage}" if lineage else name


def classify(key: str, entry: Entry) -> str | None:
    f = entry.fields
    if norm(f.get("status")) in ("underreview", "submitted"):
        return "underreview"
    if f.get("pubtype"):
        cat = CATEGORY_ALIASES.get(norm(f["pubtype"]))
        if cat is None:
            error(f"papers.bib, {key}: pubtype must be one of "
                  f"{', '.join(CATEGORIES)}; got {f['pubtype']!r}")
        return cat
    etype = entry.type.lower()
    if etype in ("inproceedings", "conference", "proceedings"):
        return "workshop" if "workshop" in f.get("booktitle", "").lower() else "conference"
    if etype == "article":
        journal = f.get("journal", "").lower()
        if not journal or "arxiv" in journal or "corr" in journal or "preprint" in journal:
            return "preprint"
        return "journal"
    if etype in ("misc", "unpublished", "techreport", "online", "preprint"):
        return "preprint"
    error(f"papers.bib, {key}: can't tell what kind of paper an @{etype} is. "
          f"Add pubtype = {{conference}} (or journal, workshop, preprint).")
    return None


def arxiv_id(f) -> str | None:
    if f.get("arxiv"):
        return f["arxiv"].strip()
    if f.get("eprint") and norm(f.get("archiveprefix") or f.get("eprinttype")) in ("arxiv", ""):
        return f["eprint"].strip()
    m = re.search(r"arxiv[^0-9]*(\d{4}\.\d{4,5})", f.get("journal", "") + " " + f.get("url", ""), re.I)
    return m.group(1) if m else None


def link_url(field: str, value: str, f) -> str:
    value = value.strip()
    if field == "arxiv" and not value.startswith("http"):
        return f"https://arxiv.org/abs/{value.removeprefix('arXiv:')}"
    if field == "doi" and not value.startswith("http"):
        return f"https://doi.org/{value}"
    if field == "openreview" and not value.startswith("http"):
        return f"https://openreview.net/forum?id={value}"
    return value


BIBTEX_ORDER = ["title", "booktitle", "series", "journal", "volume", "number", "pages", "year", "month",
                "publisher", "doi", "url", "eprint", "archiveprefix", "primaryclass"]


def to_bibtex(key: str, entry: Entry) -> str:
    """The entry as BibTeX, without the website-only fields."""
    rows = [(role, " and ".join(str(p) for p in entry.persons[role]))
            for role in ("author", "editor") if role in entry.persons]
    fields = [(k, v) for k, v in entry.fields.items() if k.lower() not in SITE_FIELDS]
    fields.sort(key=lambda kv: BIBTEX_ORDER.index(kv[0].lower())
                if kv[0].lower() in BIBTEX_ORDER else len(BIBTEX_ORDER))
    rows += fields
    width = max((len(k) for k, _ in rows), default=0)
    body = ",\n".join(f"  {k.ljust(width)} = {{{v}}}" for k, v in rows)
    return f"@{entry.type}{{{key},\n{body}\n}}"


def year_month(key: str, entry: Entry, required: bool):
    f = entry.fields
    year = f.get("year", "").strip()
    if not re.fullmatch(r"\d{4}", year):
        if required:
            error(f"papers.bib, {key}: missing or invalid year {year!r}")
        return None, 0
    month = 0
    raw = f.get("month", "").strip().lower().rstrip(".")
    if raw:
        month = int(raw) if raw.isdigit() else MONTH_LOOKUP.get(raw, 0)
    return int(year), month


def venue_text(cat: str, entry: Entry, year: int | None) -> str:
    f = entry.fields
    if cat == "underreview":
        return "Under review"
    venue = delatex(f["venue"]) if f.get("venue") else ""
    if not venue:
        if cat in ("conference", "workshop"):
            venue = delatex(f.get("booktitle", ""))
        elif cat == "journal":
            venue = delatex(f.get("journal", ""))
        else:
            venue = "arXiv preprint" if arxiv_id(f) else delatex(
                f.get("howpublished") or f.get("institution") or f.get("note") or "Preprint")
    if year and not re.search(r"\b(19|20)\d{2}\b", venue):
        venue = f"{venue} {year}".strip()
    return venue


def load_publications(cfg: dict) -> tuple[list[dict], bool, list[dict]]:
    path = CONTENT / "papers.bib"
    if not path.exists():
        warn("content/papers.bib not found; the Publications section is hidden")
        return [], False, []
    pybtex.errors.set_strict_mode(True)
    try:
        bib = parse_file(str(path), "bibtex")
    except Exception as e:  # pybtex raises several error types
        error(f"content/papers.bib: {e}")
        return [], False, []

    pcfg = cfg.get("publications") or {}
    style = pcfg.get("author_names", "full")
    if style not in ("full", "initials"):
        error("config.yml: publications.author_names must be 'full' or 'initials'")
        style = "full"
    me = set()
    for name in cfg.get("me") or []:
        me.add(person_key(Person(str(name))))
    if not me:
        warn("config.yml: 'me' is empty, so your name won't be highlighted in author lists")

    buckets: dict[str, list[dict]] = {k: [] for k in CATEGORIES}
    examples = 0
    for pos, (key, entry) in enumerate(bib.entries.items()):
        f = entry.fields
        if key.lower().startswith("example"):
            examples += 1
        if truthy(f.get("hidden")):
            continue
        cat = classify(key, entry)
        if cat is None:
            continue
        if not f.get("title"):
            error(f"papers.bib, {key}: missing title")
            continue
        year, month = year_month(key, entry, required=cat != "underreview")

        equal = set()
        if f.get("equal"):
            try:
                equal = {int(x) for x in re.split(r"[,\s]+", f["equal"].strip()) if x}
            except ValueError:
                error(f"papers.bib, {key}: equal must list author positions, e.g. equal = {{1,2}}")
        authors = []
        found_me = False
        for i, p in enumerate(entry.persons.get("author", []), 1):
            if str(p) == "others":
                authors.append({"name": "et al.", "me": False, "equal": False})
                continue
            is_me = person_key(p) in me
            found_me |= is_me
            authors.append({"name": format_person(p, style), "me": is_me, "equal": i in equal})
        if me and not found_me and authors:
            warn(f"papers.bib, {key}: none of the authors matches 'me' in config.yml")

        links = []
        seen = set()
        for field, label in LINK_FIELDS:
            value = arxiv_id(f) if field == "arxiv" else f.get(field)
            if field == "pdf" and not value and arxiv_id(f):
                value = f"https://arxiv.org/pdf/{arxiv_id(f).removeprefix('arXiv:')}"
            if not value:
                continue
            url = link_url(field, value, f)
            if url in seen:
                continue
            if not re.match(r"(https?://|static/)", url):
                error(f"papers.bib, {key}: {field} should be a full URL or a path under static/; got {value!r}")
                continue
            seen.add(url)
            if field == "url" and "proceedings.mlr.press" in url:
                label = "PMLR"
            links.append({"label": label, "url": url})

        buckets[cat].append({
            "key": key,
            "category": cat,
            "title": latex_html(f["title"]),
            "authors": authors,
            "venue": venue_text(cat, entry, year),
            "award": delatex(f["award"]) if f.get("award") else None,
            "links": links,
            "abstract": latex_html(f["abstract"]) if f.get("abstract") else None,
            "bibtex": None if cat == "underreview" else to_bibtex(key, entry),
            "bibfile": "bib/" + re.sub(r"[^\w.-]", "_", key) + ".bib",
            "selected": truthy(f.get("selected")),
            "_sort": (year or 0, month, pos),
        })

    if examples:
        warn(f"content/papers.bib still contains {examples} example entr{'y' if examples == 1 else 'ies'} "
             "(keys starting with 'example')")

    order = pcfg.get("order") or list(CATEGORIES)
    for k in order:
        if k not in CATEGORIES:
            error(f"config.yml: publications.order has unknown category {k!r}")
    show_ur = pcfg.get("show_under_review", True)
    selected_only = pcfg.get("selected_only", False)

    layout = pcfg.get("layout", "category-year")
    if layout not in ("category-year", "year"):
        error("config.yml: publications.layout must be 'category-year' or 'year'")
        layout = "category-year"

    shown = {}
    for cat in order:
        if cat not in CATEGORIES or (cat == "underreview" and not show_ur):
            continue
        items = sorted(buckets[cat], key=lambda p: p["_sort"])
        prefix = CATEGORIES[cat][0]
        for n, p in enumerate(items, 1):     # oldest = 1, so labels never change
            p["label"] = f"{prefix}{n}"
        if selected_only:
            items = [p for p in items if p["selected"]]
        if items:
            shown[cat] = list(reversed(items))   # newest first

    def by_year(items):
        years = []
        for p in items:
            y = p["_sort"][0] or None
            if not years or years[-1]["year"] != y:
                years.append({"year": y, "items": []})
            years[-1]["items"].append(p)
        return years

    groups = []
    if layout == "year":
        # Published work by year (labels keep their category), then preprints and under review.
        published = [p for cat in shown if cat not in ("preprint", "underreview") for p in shown[cat]]
        rank = {cat: i for i, cat in enumerate(order)}
        published.sort(key=lambda p: (-p["_sort"][0], -p["_sort"][1], rank[p["category"]], -p["_sort"][2]))
        if published:
            groups.append({"key": "published", "heading": None, "years": by_year(published)})
        for cat in ("preprint", "underreview"):
            if cat in shown:
                groups.append({"key": cat, "heading": CATEGORIES[cat][1],
                               "years": [{"year": None, "items": shown[cat]}]})
    else:
        for cat, items in shown.items():
            years = by_year(items) if cat != "underreview" else [{"year": None, "items": items}]
            groups.append({"key": cat, "heading": CATEGORIES[cat][1], "years": years})

    any_equal = any(a["equal"] for items in shown.values() for p in items for a in p["authors"])
    all_items = [p for items in shown.values() for p in items]
    return groups, any_equal, all_items


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

ICONS = {"pareto", "preference", "theory", "safety", "interpretability", "robot", "data", "teaching"}


def load_research() -> dict | None:
    path = CONTENT / "research.yml"
    if not path.exists():
        return None
    data = load_yaml(path)
    if data is None:
        return None
    rel = path.relative_to(ROOT)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        error(f"{rel}: expected an optional 'intro' and a list of 'items'")
        return None
    intro = None
    if data.get("intro"):
        if check_text(data["intro"], f"{rel}, intro"):
            intro = md_inline(str(data["intro"]).strip())
    items = []
    for i, raw in enumerate(data["items"], 1):
        where = f"{rel}, item {i}"
        if not isinstance(raw, dict) or not raw.get("title") or not raw.get("text"):
            error(f"{where}: needs a title and a text")
            continue
        unknown = set(raw) - {"title", "text", "icon"}
        if unknown:
            error(f"{where}: unknown field(s) {', '.join(sorted(unknown))}. Allowed: title, text, icon")
        icon = raw.get("icon") or "theory"
        if icon not in ICONS:
            error(f"{where}: icon must be one of {', '.join(sorted(ICONS))}")
            icon = "theory"
        if check_text(raw["title"], f"{where}, title") and check_text(raw["text"], f"{where}, text"):
            items.append({"title": md_inline(str(raw["title"]).strip()),
                          "text": md_inline(str(raw["text"]).strip()), "icon": icon})
    return {"intro": intro, "items": items} if items else None


SECTION_TITLES = {
    "research": "Research interests",
    "news": "News",
    "publications": "Publications",
    "education": "Education",
    "experience": "Experience",
    "teaching": "Teaching",
    "awards": "Awards",
    "extracurricular": "Extracurricular activities",
}
NAV_TITLES = {"research": "Research", "extracurricular": "Activities"}   # shorter labels for the top bar


LINK_ICONS = [("scholar.google", "scholar"), ("github.com", "github"), ("linkedin.com", "linkedin"),
              ("orcid.org", "orcid")]


def load_facts(cfg: dict, papers: list[dict], theses: int = 0) -> list[dict]:
    """The Quick facts panel. Values may use {publications}, {conference}, {journal}, ..."""
    counted = (cfg.get("publications") or {}).get("count", ["conference", "journal"])
    for cat in counted:
        if cat not in CATEGORIES:
            error(f"content/config.yml: publications.count has unknown category {cat!r}")
    counts = {"publications": sum(p["category"] in counted for p in papers), "all": len(papers),
              "theses": theses}
    for cat in CATEGORIES:
        counts[cat] = sum(p["category"] == cat for p in papers)
    facts = []
    for i, raw in enumerate(cfg.get("facts") or [], 1):
        where = f"content/config.yml, facts entry {i}"
        if not isinstance(raw, dict) or "label" not in raw or "value" not in raw:
            error(f"{where}: needs a label and a value")
            continue
        if not (check_text(raw["label"], f"{where}, label") and check_text(raw["value"], f"{where}, value")):
            continue
        value = str(raw["value"])
        for name in re.findall(r"\{(\w+)\}", value):
            if name not in counts:
                error(f"{where}: unknown placeholder {{{name}}}. Available: "
                      + ", ".join("{" + k + "}" for k in counts))
        value = re.sub(r"\{(\w+)\}", lambda m: str(counts.get(m.group(1), m.group(0))), value)
        facts.append({"label": md_inline(str(raw["label"])), "value": md_inline(value)})
    return facts


def load_config() -> dict:
    path = CONTENT / "config.yml"
    if not path.exists():
        error("content/config.yml is missing")
        return {}
    n_errors = len(errors)
    cfg = load_yaml(path)
    if cfg is None:
        if len(errors) == n_errors:
            error("content/config.yml is empty")
        return {}
    if not isinstance(cfg, dict):
        error("content/config.yml: expected 'key: value' settings")
        return {}
    if not cfg.get("name"):
        error("content/config.yml: 'name' is required")
    for i, link in enumerate(cfg.get("links") or [], 1):
        if not isinstance(link, dict) or not link.get("label") or not link.get("url"):
            error(f"content/config.yml, links entry {i}: needs both label and url")
    for s in cfg.get("sections") or []:
        if s not in SECTION_TITLES and not (CONTENT / f"{s}.yml").exists():
            error(f"content/config.yml: section {s!r} needs a file content/{s}.yml "
                  f"(built-in sections: {', '.join(SECTION_TITLES)})")
    if not isinstance(cfg.get("titles") or {}, dict):
        error("content/config.yml: titles must be 'section: Title' pairs")
        cfg["titles"] = {}
    for key in ("position", "description", "email", "photo", "cv_pdf"):
        cfg.setdefault(key, None)
    cfg["links"] = cfg.get("links") or []
    for link in cfg["links"]:
        if isinstance(link, dict) and not link.get("icon"):
            url = str(link.get("url", ""))
            link["icon"] = next((name for host, name in LINK_ICONS if host in url), "link")
    if cfg.get("email"):
        # Accepts "name.surname@polimi.it" or "name [dot] surname [at] polimi [dot] it".
        email = re.sub(r"\s*\[dot\]\s*", ".", str(cfg["email"]).strip(), flags=re.I)
        email = re.sub(r"\s*\[at\]\s*", "@", email, flags=re.I)
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            error(f"content/config.yml: email {email!r} doesn't look like an address")
        else:
            user, domain = email.split("@")
            # Shown as "name [dot] surname [at] polimi [dot] it"; the page script turns it into a
            # working link from the reversed parts, so the page never contains the plain address.
            cfg["email_display"] = " [at] ".join(part.replace(".", " [dot] ") for part in (user, domain))
            cfg["email_parts"] = (user[::-1], domain[::-1])
    cfg.setdefault("bands", ["research", "news"])
    cfg.setdefault("contact", "Feel free to reach out about research, collaborations, or teaching.")
    if cfg["contact"]:
        cfg["contact"] = md_inline(str(cfg["contact"]))
    for key in ("photo", "cv_pdf"):
        if cfg.get(key) and not (ROOT / cfg[key]).exists():
            warn(f"content/config.yml: {key} points to {cfg[key]}, which doesn't exist; it's left out")
            cfg[key] = None
    return cfg


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build() -> bool:
    errors.clear()
    warnings.clear()
    cfg = load_config()
    if errors:
        return report()

    bio_path = CONTENT / "bio.md"
    bio = md_block(bio_path.read_text(encoding="utf-8")) if bio_path.exists() else ""

    news_limit = int(cfg.get("news_limit", 10))
    news_ticker = int(cfg.get("news_ticker", 5))
    news = load_section("news")
    sections = []
    pubs, any_equal, papers = load_publications(cfg) if "publications" in (cfg.get("sections") or SECTION_TITLES) \
        else ([], False, [])
    facts = load_facts(cfg, papers, theses=len(load_section("supervision")))
    for name in cfg.get("sections") or list(SECTION_TITLES):
        titles = cfg.get("titles") or {}
        title = str(titles.get(name) or SECTION_TITLES.get(name) or name.replace("_", " ").capitalize())
        nav = NAV_TITLES.get(name, title) if name not in titles else title
        sec = {"id": name, "title": title, "nav": nav, "band": name in (cfg.get("bands") or [])}
        if name == "publications":
            if pubs:
                sections.append(sec)
        elif name == "research":
            sec["research"] = load_research()
            if sec["research"]:
                sections.append(sec)
        elif name == "teaching":
            sec["items"] = load_section("teaching")
            sec["supervision"] = load_section("supervision")   # shown inside Teaching
            if sec["items"] or sec["supervision"]:
                sections.append(sec)
        elif name == "news":
            if news:
                sec["items"] = news[:news_limit]
                sections.append(sec)
        else:
            sec["items"] = load_section(name)
            if sec["items"]:
                sections.append(sec)
    scan_todos()
    if errors:
        return report()

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["md"] = md_inline
    env.filters["groupby_date"] = group_by_date
    now = dt.date.today()
    common = dict(
        site=cfg,
        year=now.year,
        updated=f"{now.day} {dt.date(2000, now.month, 1).strftime('%B')} {now.year}",
        version=dt.datetime.now().strftime("%Y%m%d%H%M%S"),
    )
    index = env.get_template("index.html.j2").render(
        **common, home="", sections=sections, bio=bio, facts=facts, pubs=pubs, any_equal=any_equal,
        ticker=news[:news_ticker], news_total=len(news),
    )
    archive = env.get_template("news.html.j2").render(**common, home="index.html", sections=sections, news=news)

    if OUT.exists():
        try:
            shutil.rmtree(OUT)
        except OSError:
            pass  # some synced folders refuse deletes; the files below are overwritten instead
    shutil.copytree(STATIC, OUT / "static", dirs_exist_ok=True)
    (OUT / "index.html").write_text(index, encoding="utf-8")
    (OUT / "news.html").write_text(archive, encoding="utf-8")
    papers = [p for p in papers if p["bibtex"]]
    if papers:
        (OUT / "bib").mkdir(exist_ok=True)
        for p in papers:
            (OUT / p["bibfile"]).write_text(p["bibtex"] + "\n", encoding="utf-8")
        (OUT / "bib" / "publications.bib").write_text(
            "\n\n".join(p["bibtex"] for p in papers) + "\n", encoding="utf-8")
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    return report()


def report() -> bool:
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if errors:
        print(f"\nBuild failed with {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return False
    print(f"Built {OUT.relative_to(ROOT)}/index.html")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="preview at http://localhost:8000 after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    if not build():
        sys.exit(1)
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print(f"Serving on http://localhost:{args.port} (Ctrl+C to stop)")
        with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
