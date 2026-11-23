"""Ajoute le russe (6e langue) aux pages HTML du site, à partir de scripts/i18n_ru.json (clé = texte français).
Idempotent : un texte qui a déjà sa version russe n'est pas modifié. À relancer après un générateur de pages.
  - groupes de <span lang> fr/en/es/pt/de → ajout de <span lang="ru"> ;
  - blocs <div|p lang="fr"> … <div|p lang="de"> → ajout du bloc russe (id préfixés « ru- ») ;
  - titres (data-ru), placeholders (data-ph-ru), menu des langues, infobulles multilingues.
Usage : python3 scripts/add_ru.py [racine du site]"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RU = json.loads((HERE / "i18n_ru.json").read_text(encoding="utf-8"))
MISSING = []

_IN = r'((?:(?!</span>).)*)'   # contenu d'un span de langue (jamais de span imbriqué)
SPAN5 = re.compile(r'<span lang="fr">' + _IN + r'</span>(\s*)<span lang="en">' + _IN + r'</span>\s*<span lang="es">' + _IN +
                   r'</span>\s*<span lang="pt">' + _IN + r'</span>\s*<span lang="de">' + _IN + r'</span>(?!\s*<span lang="ru">)', re.S)
MENU_RU = ('<li role="none"><button type="button" role="menuitemradio" aria-checked="false" data-set-lang="ru">'
           '<span class="lang-list__code">RU</span><span class="lang-list__name">Русский</span>'
           '<span class="lang-list__check" aria-hidden="true"></span></button></li>')


def tr(fr, en, where):
    t = RU.get(fr)
    if t is None:
        MISSING.append((where, fr[:90]))
        return en
    return t


def block_end(s, i, tag):
    depth = 1
    for t in re.finditer(rf"<{tag}\b|</{tag}>", s[i:]):
        depth += -1 if t.group(0).startswith("</") else 1
        if depth == 0:
            return i + t.start(), i + t.end()
    raise ValueError(f"bloc <{tag}> non fermé")


def add_blocks(s, tag, where):
    pos = 0
    while True:
        m = re.compile(rf'<{tag} lang="fr">').search(s, pos)
        if not m:
            return s
        a, b = block_end(s, m.end(), tag)
        fr = s[m.end():a]
        end = b
        en = None
        for lang in ("en", "es", "pt", "de"):
            m2 = re.compile(rf'\s*<{tag} lang="{lang}">').match(s, end)
            if not m2:
                break
            c, end = block_end(s, m2.end(), tag)
            if lang == "en":
                en = s[m2.end():c]
        pos = end
        if re.compile(rf'\s*<{tag} lang="ru">').match(s, end):
            continue
        body = re.sub(r'\bid="([^"]+)"', r'id="ru-\1"', tr(fr, en or fr, where))
        ins = f'\n<{tag} lang="ru">{body}</{tag}>'
        s = s[:end] + ins + s[end:]
        pos = end + len(ins)


def process(s, where="?"):
    s = SPAN5.sub(lambda m: m.group(0) + m.group(2) + f'<span lang="ru">{tr(m.group(1), m.group(3), where)}</span>', s)
    for tag in ("div", "p"):
        s = add_blocks(s, tag, where)

    def title(m):
        if "data-ru=" in m.group(0):
            return m.group(0)
        attrs, en = m.group(1), m.group(2).strip()
        fr = re.search(r'data-fr="([^"]*)"', attrs).group(1)
        return f'<title{attrs} data-ru="{tr(fr, en, where)}">{m.group(2)}</title>'
    s = re.sub(r'<title( data-fr="[^"]*"[^>]*)>(.*?)</title>', title, s, count=1, flags=re.S)

    def ph(m):
        if "data-ph-ru=" in m.group(0):
            return m.group(0)
        return m.group(0) + f' data-ph-ru="{tr(m.group(1), m.group(2), where)}"'
    s = re.sub(r'data-ph-fr="([^"]*)"\s+data-ph-en="([^"]*)"(?:\s+data-ph-(?:es|pt|de)="[^"]*")*(?![^>]*data-ph-ru)', ph, s)

    if 'data-set-lang="de"' in s and 'data-set-lang="ru"' not in s:
        s = re.sub(r'(<li role="none"><button[^>]*data-set-lang="de">.*?</button></li>)', lambda m: m.group(1) + MENU_RU, s, count=1, flags=re.S)
    s = s.replace("Langue · Language · Idioma · Língua · Sprache\"", "Langue · Language · Idioma · Língua · Sprache · Язык\"")
    s = s.replace("Mode clair · Light mode · Modo claro · Heller Modus\"", "Mode clair · Light mode · Modo claro · Heller Modus · Светлая тема\"")
    return s


def main(argv):
    root = Path(argv[0]) if argv else HERE.parent
    files = subprocess.check_output(["git", "-C", str(root), "ls-files", "*.html"]).decode().split()
    changed = 0
    for f in files:
        p = root / f
        s = p.read_text(encoding="utf-8")
        o = process(s, f)
        if o != s:
            p.write_text(o, encoding="utf-8")
            changed += 1
    print(f"russe : {changed} page(s) mise(s) à jour")
    if MISSING:
        print(f"[ru] {len(MISSING)} texte(s) sans traduction (affichés en anglais) :", file=sys.stderr)
        for w, t in MISSING[:30]:
            print(f"  {w}: {t!r}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
