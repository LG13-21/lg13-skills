"""skill-catalog: build (inventura vsech skills -> SKILL_CATALOG.md + catalog.json) a pick (vyber skillu k ukolu)."""
import argparse, json, math, re, sys, unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HOME = Path.home() / ".claude"
OUT = Path(__file__).parent
SOURCES = [
    ("lg13-skills", Path("L:/GitHub/lg13-skills/plugins/lg13-skills/skills")),
    ("user", HOME / "skills"),
]
CACHE = HOME / "plugins" / "cache"
CATS = [
    ("legal-filing", r"filing|podan|f-cycle|f\d\d|lock|f-filing|legal|isds|chatgpt-legal|diamond|judi|cge|slim-diet|writing-doc|ai-cleaning|attachment|priloh|ocr|spis"),
    ("komunikace", r"ping|pong|heartbeat|notify|slack|team|avengers|cockpit|tom-|chat-|gpt|chatgpt|email|queue|wake"),
    ("session", r"init|save|restart|checkpoint|autosave|\bsr\b|end\b|bootstrap|store|remember|compact|edge-check|budget|limit|food|pacer|token"),
    ("tm-ingest", r"tmonkey|tampermonkey|atom|ingest|listen|hear|rain|rag"),
    ("vyhledavani", r"search|find|catalog|picker|read|harvest"),
    ("dev-proces", r"superpowers|debug|test|plan|review|brainstorm|worktree|code-review|simplify|verify|skill-creator|writing-skills"),
    ("infra", r"mysql|ftp|config|hook|loop|schedule|ctx|context-mode|mcp|chrome|run\b|init"),
]


def fm(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        cur = None
        for line in m.group(1).splitlines():
            if re.match(r"^[A-Za-z_-]+:", line):
                k, _, v = line.partition(":")
                cur = k.strip()
                out[cur] = v.strip().strip('"\'')
            elif cur and line.strip():
                out[cur] += " " + line.strip()
    return out


def fallback_desc(t):
    t = re.sub(r"^---.*?\n---", "", t, flags=re.S)
    for line in t.splitlines():
        l = line.strip().lstrip("> ").strip()
        if l and not l.startswith(("#", "```", "|", "---")):
            return l[:300]
    return ""


def category(name, desc):
    hay = (name + " " + desc[:200]).lower()
    for cat, rx in CATS:
        if re.search(rx, name.lower()):
            return cat
    for cat, rx in CATS:
        if re.search(rx, hay):
            return cat
    return "ostatni"


def collect():
    roots = list(SOURCES)
    if CACHE.exists():
        for plug in sorted(CACHE.glob("*/*")):
            vers = sorted([v for v in plug.iterdir() if (v / "skills").is_dir()], key=lambda p: p.stat().st_mtime)
            if vers:
                roots.append((f"{plug.parent.name}/{plug.name}", vers[-1] / "skills"))
    items, seen = [], set()
    for src, root in roots:
        if not root.is_dir():
            continue
        for md in sorted(root.glob("*/SKILL.md")):
            if md.parent.name.startswith("_") or src.startswith("lg13/"):
                continue
            try:
                t = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            f = fm(t)
            name = f.get("name") or md.parent.name
            key = (src.split("/")[-1], name)
            if key in seen:
                continue
            seen.add(key)
            desc = f.get("description", "") or fallback_desc(t)
            dep = "deprecated" in (desc + t[:600]).lower() and "replaced" in (desc + t[:600]).lower()
            items.append({"name": name, "source": src, "path": str(md), "description": desc,
                          "category": category(name, desc), "deprecated": dep,
                          "no_desc": not desc})
    return items


def build():
    items = collect()
    (OUT / "catalog.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    by = {}
    for i in items:
        by.setdefault(i["category"], []).append(i)
    L = [f"# SKILL CATALOG ({len(items)} skills)", "",
         "Generovano `skill_catalog.py build`. Vyber k ukolu: `skill_catalog.py pick \"ukol\"`.", ""]
    for cat in sorted(by):
        L += [f"## {cat} ({len(by[cat])})", "", "| skill | zdroj | kdy |", "|---|---|---|"]
        for i in sorted(by[cat], key=lambda x: x["name"]):
            d = i["description"].replace("|", "/")
            d = (d[:110] + "...") if len(d) > 110 else d
            flag = " [DEPRECATED]" if i["deprecated"] else ""
            L.append(f"| {i['name']}{flag} | {i['source']} | {d or '(bez popisu)'} |")
        L.append("")
    issues = [i for i in items if i["no_desc"] or i["deprecated"]]
    L += ["## Problemy", ""] + [f"- {i['name']} ({i['source']}): {'bez description' if i['no_desc'] else 'deprecated'}" for i in issues]
    (OUT / "SKILL_CATALOG.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"catalog: {len(items)} skills, {len(by)} kategorii, {len(issues)} problemu -> {OUT/'SKILL_CATALOG.md'}")


def tok(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z0-9]{3,}", s)]


SYN = {
    "soubor": "file", "soubory": "file", "najdi": "search find", "hledej": "search find", "hledani": "search find",
    "uloz": "save", "ulozit": "save", "stav": "state status", "podani": "filing", "priloha": "attachment",
    "prilohy": "attachment", "odeslat": "send", "odesli": "send", "zbyva": "usage limit budget", "limit": "usage budget",
    "chyba": "bug error debug", "padajici": "failing", "nefunguje": "bug debug", "rozbite": "bug debug",
    "pomoc": "help", "zprava": "message", "vlakno": "thread", "kontrola": "check review audit",
    "zkontroluj": "check review audit", "nahraj": "upload", "stahni": "download", "spust": "run start",
    "dokument": "document", "rozsir": "extend", "uklid": "cleanup", "plan": "plan",
}


def expand(words):
    out = []
    for w in words:
        out.append(w)
        out += tok(SYN.get(w, ""))
    return out


def stem(w):
    return w[:4]


def pick(query, n):
    cat = OUT / "catalog.json"
    if not cat.exists():
        build()
    items = [i for i in json.loads(cat.read_text(encoding="utf-8")) if not i["deprecated"]]
    docs = []
    for i in items:
        nm = tok(i["name"].replace("-", " "))
        ds = tok(i["description"])
        docs.append((Counter(map(stem, ds)), set(map(stem, nm)), len(ds) or 1))
    N = len(docs)
    if not N:
        print("zadna shoda - katalog je prazdny, spust `skill_catalog.py build`")
        return
    df =Counter(w for c, _, _ in docs for w in set(c))
    avg = sum(l for _, _, l in docs) / N
    q = list(map(stem, expand(tok(query))))
    res = []
    for i, (c, nm, l) in zip(items, docs):
        s = 0.0
        for w in q:
            idf = math.log(1 + (N - df[w] + .5) / (df[w] + .5))
            tf = c[w]
            s += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * l / avg)) if tf else 0
            if w in nm:
                s += idf * 2
        if s:
            res.append((s, i))
    res.sort(key=lambda x: -x[0])
    if not res:
        print("zadna shoda - zkus jine klicove slovo nebo `skill_catalog.py build`")
        return
    for s, i in res[:n]:
        d = i["description"]
        print(f"{s:5.1f}  /{i['name']}  [{i['category']}/{i['source']}]\n       {d[:140]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("pick")
    p.add_argument("query", nargs="+")
    p.add_argument("-n", type=int, default=5)
    a = ap.parse_args()
    build() if a.cmd == "build" else pick(" ".join(a.query), a.n)


if __name__ == "__main__":
    main()
