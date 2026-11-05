#!/usr/bin/env python3
"""Génère la page « Actus » du site : news/index.html et data/news-archive.json.

Lancé par GitHub Actions (toutes les 6 heures et à chaque publication), juste avant Jekyll :
1. télécharge les flux RSS de sources reconnues et le catalogue KEV de la CISA ;
2. garde les articles sur les failles exploitées et sur les attaques ;
3. fusionne avec l'archive déjà publiée sur le site : le site sert lui-même de mémoire,
   sans aucun commit automatique dans le dépôt ;
4. regroupe les articles qui parlent du même sujet et classe les sujets par nombre de sources ;
5. écrit la page (titres, dates et liens seulement : le contenu reste chez les sources).

Sécurité : les flux sont des données NON FIABLES. Téléchargements bornés en taille et en durée,
DTD et entités XML refusées, tout le texte échappé, seuls les liens http(s) conservés.
Une source en panne n'empêche jamais la publication du site.

Usage : python3 scripts/news/build_news.py [--root .] [--offline]
"""
import argparse
import datetime as dt
import email.utils
import hashlib
import html
import json
import math
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiches as fx  # noqa: E402

try:
    from zoneinfo import ZoneInfo
    PARIS = ZoneInfo("Europe/Paris")
except Exception:  # pragma: no cover
    PARIS = dt.timezone.utc

SITE = "https://manthole.github.io"
USER_AGENT = "manthole-news/1.0 (+https://manthole.github.io/news/)"
MAX_BYTES = 8 * 1024 * 1024
TIMEOUT = 25
KEEP_DAYS = 400

# Sources reconnues. « priority » : ordre de préférence pour le titre affiché d'un sujet.
SOURCES = [
    {"id": "bleeping", "name": "BleepingComputer", "home": "https://www.bleepingcomputer.com", "feed": "https://www.bleepingcomputer.com/feed/"},
    {"id": "record", "name": "The Record", "home": "https://therecord.media", "feed": "https://therecord.media/feed"},
    {"id": "thn", "name": "The Hacker News", "home": "https://thehackernews.com", "feed": "https://feeds.feedburner.com/TheHackersNews"},
    {"id": "securityweek", "name": "SecurityWeek", "home": "https://www.securityweek.com", "feed": "https://www.securityweek.com/feed/"},
    {"id": "krebs", "name": "Krebs on Security", "home": "https://krebsonsecurity.com", "feed": "https://krebsonsecurity.com/feed/"},
    {"id": "zataz", "name": "ZATAZ", "home": "https://www.zataz.com", "feed": "https://www.zataz.com/feed/"},
    {"id": "certfr", "name": "CERT-FR (ANSSI)", "home": "https://cert.cyber.gouv.fr", "feed": "https://cert.cyber.gouv.fr/alerte/feed/"},
    {"id": "certfr-cti", "name": "CERT-FR (ANSSI)", "home": "https://cert.cyber.gouv.fr", "feed": "https://cert.cyber.gouv.fr/cti/feed/"},
]
SOURCE_NAMES = {s["id"]: s["name"] for s in SOURCES}
PRIORITY = {s["id"]: i for i, s in enumerate(SOURCES)}
# Miroir GitHub officiel du catalogue de la CISA (le site de la CISA refuse souvent les robots).
KEV_URL = "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json"
ARCHIVE_URL = SITE + "/data/news-archive.json"

ZERO_DAY = re.compile(
    r"\bzero[\s-]?days?\b|\b0[\s-]?days?\b|actively exploited|exploited in the wild|under active exploitation|"
    r"exploited (?:as|in) (?:a )?zero|activement exploit|exploitée?s? dans la nature|faille (?:zero|0)[\s-]?day",
    re.I)
ATTACK = re.compile(
    r"ransomware|ran[cç]ongiciel|cyber[\s-]?attaque|cyber[\s-]?attack|data breach|\bbreach(?:ed|es)?\b|"
    r"fuite de donn|vol de donn|stolen data|steal(?:s|ing)? data|piratage|pirat[ée]e?s?\b|\bhacked\b|"
    r"\bddos\b|supply[\s-]chain attack|extortion|extorsion|leak(?:ed|s)? (?:data|records)|compromis|"
    r"\bwiper\b|espionnage|espionage|intrusion|outage after (?:a )?(?:cyber|attack)",
    re.I)
# Récapitulatifs multi-sujets, contenus sponsorisés : ils fausseraient le regroupement.
EXCLUDE = re.compile(
    r"\bweek(?:ly)? (?:recap|in review)\b|\brecap\b|\bthreatsday\b|in other news|\bwebinar\b|\bsponsored\b|"
    r"\bpodcast\b|\bbulletin d'actualit|livre blanc|\bhow to\b|\bguide\b", re.I)
CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.I)
# rapports de synthèse du CERT-FR : utiles, mais ce ne sont pas des attaques
CTI_REPORT = re.compile(r"panorama|overview|landscape|état de la menace|retour d'expérience|point de situation|"
                        r"intelligence artificielle", re.I)
# éditeurs omniprésents dans l'actualité : leur nom seul ne suffit pas à relier deux articles
BIG_VENDORS = set("""
apple microsoft google chrome android ios iphone windows macos linux amazon aws meta facebook whatsapp
cisco oracle ibm adobe samsung intel amd nvidia openai github gitlab wordpress php java npm pypi
""".split())

STOPWORDS = set("""
a an the of to in on at for from by with and or but as is are was were be been has have had it its this that these those
after before over into about against via new more most than up out not no all any can could will would may might says say
said report reports reported warn warns warned amid how why what who when where which while also just now still yet
le la les un une des du de d l au aux et ou en dans sur par pour avec sans sous chez est sont ont a été être plus moins
qui que quoi dont où ce cet cette ces son sa ses leur leurs se ne pas d'un d'une l'un après avant contre selon face
attack attacks attacked attacker attackers hack hacks hacked hacker hackers hacking breach breaches breached data
ransomware gang gangs group groups threat threats actor actors cyber cyberattack cyberattacks security flaw flaws bug
bugs vulnerability vulnerabilities exploit exploits exploited exploiting exploitation zero day days 0day patch patches
patched fixes fix fixed update updates critical warns million millions users customers companies company firm firms
cyberattaque attaque attaques pirates piratage faille failles fuite données victime victimes vol campagne
malware attaque informatique alerte vulnérabilité vulnérabilités multiples activement nature
rce ddos vpn api sql xss ceo cisa fbi nsa cert anssi nist kev cve cves ai iot ics ot apt dns
zero-day zero-days 0-day 0-days
""".split())


# --------------------------------------------------------------------------- téléchargement
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/json, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("réponse trop volumineuse")
    return data


# --------------------------------------------------------------------------- lecture des flux
def clean_text(s, limit=300):
    s = html.unescape(re.sub(r"<[^>]{0,2000}>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]


def safe_url(u):
    u = (u or "").strip()
    try:
        p = urllib.parse.urlsplit(u)
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.netloc or any(c in u for c in "\"'<> \t\r\n"):
        return None
    return u


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError, IndexError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


ATOM = "{http://www.w3.org/2005/Atom}"
DC = "{http://purl.org/dc/elements/1.1/}"


def parse_feed(data):
    """Renvoie [(titre, lien, date, résumé)] d'un flux RSS 2.0 ou Atom."""
    head = data[:20000]
    if re.search(rb"<!DOCTYPE|<!ENTITY", head, re.I) or re.search(rb"<!ENTITY", data, re.I):
        raise ValueError("DTD ou entité XML refusée")
    root = ET.fromstring(data)
    out = []
    for item in root.iter("item"):
        out.append((item.findtext("title"), item.findtext("link"),
                    item.findtext("pubDate") or item.findtext(DC + "date"), item.findtext("description")))
    for entry in root.iter(ATOM + "entry"):
        link = None
        for l in entry.findall(ATOM + "link"):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href")
                break
        out.append((entry.findtext(ATOM + "title"), link,
                    entry.findtext(ATOM + "published") or entry.findtext(ATOM + "updated"),
                    entry.findtext(ATOM + "summary") or entry.findtext(ATOM + "content")))
    return out


def classify(source_id, title, summary, url):
    text = title + " " + summary
    if EXCLUDE.search(title):
        return None
    zero = bool(ZERO_DAY.search(text))
    attack = bool(ATTACK.search(title)) or bool(ATTACK.search(summary[:300]))
    if source_id == "certfr":
        zero = zero or "/alerte/" in url
    if source_id == "certfr-cti":
        if CTI_REPORT.search(title):
            return None
        attack = True
    if not (zero or attack):
        return None
    return {"zero_day": zero, "attack": attack}


def items_from_feed(source, data, now):
    items = []
    for title, link, date, summary in parse_feed(data):
        title = clean_text(title)
        url = safe_url(link)
        d = parse_date(date)
        if not title or not url or not d or d > now + dt.timedelta(days=1):
            continue
        summary = clean_text(summary, 1200)
        tags = classify(source["id"], title, summary, url)
        if not tags:
            continue
        # faits extraits du résumé (le résumé lui-même n'est pas conservé) : type d'attaque, CVE
        kinds = fx.kind_scores(title, summary)
        cves = sorted({c.upper() for c in CVE.findall(title + " " + summary)})[:8]
        actors = [a["id"] for _, a in fx.find_actors([title, summary])]
        items.append({"id": hashlib.sha1(url.encode()).hexdigest()[:16], "title": title, "url": url,
                      "source": source["id"], "date": d.isoformat(timespec="seconds"), **tags,
                      "kinds": kinds, "cves": cves, "actors": actors})
    return items


def valid_item(x):
    return (isinstance(x, dict) and isinstance(x.get("id"), str) and isinstance(x.get("title"), str)
            and safe_url(x.get("url")) and x.get("source") in SOURCE_NAMES and parse_date(x.get("date"))
            and isinstance(x.get("zero_day"), bool) and isinstance(x.get("attack"), bool))


def normalise(x):
    """Champs facultatifs de l'archive (absents des anciennes entrées, ou altérés) : recalculés ou nettoyés."""
    kinds = x.get("kinds")
    if not (isinstance(kinds, dict) and all(k in fx.KINDS and v in (1, 3) for k, v in kinds.items())):
        x["kinds"] = fx.kind_scores(x["title"])
    cves = x.get("cves")
    if not (isinstance(cves, list) and all(isinstance(c, str) and re.fullmatch(r"CVE-\d{4}-\d{4,7}", c) for c in cves)):
        x["cves"] = sorted({c.upper() for c in CVE.findall(x["title"])})
    actors = x.get("actors")
    if not (isinstance(actors, list) and all(isinstance(a, str) and re.fullmatch(r"[GS]\d{4}", a) for a in actors)):
        x["actors"] = [a["id"] for _, a in fx.find_actors([x["title"]])]
    return x


def merge(archive, fresh, now):
    # les filtres s'appliquent aussi à l'archive : une règle ajoutée nettoie l'historique
    by_id = {x["id"]: x for x in archive if valid_item(x) and not EXCLUDE.search(x["title"])
             and not (x["source"] == "certfr-cti" and CTI_REPORT.search(x["title"]))}
    for x in fresh:
        by_id[x["id"]] = x
    limit = now - dt.timedelta(days=KEEP_DAYS)
    kept = [normalise(x) for x in by_id.values() if parse_date(x["date"]) >= limit]
    kept.sort(key=lambda x: x["date"], reverse=True)
    return kept[:20000]


# --------------------------------------------------------------------------- regroupement par sujet
def tokens(title):
    t = unicodedata.normalize("NFKD", title.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    words = re.findall(r"[a-z0-9][a-z0-9\-]{2,}", t)
    out = set()
    for w in words:
        w = w.strip("-")
        if w in STOPWORDS or w.isdigit() or len(w) < 3:
            continue
        if len(w) > 5 and w.endswith(("ches", "shes", "sses", "xes")):
            w = w[:-2]  # switches = switch
        elif len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]  # pluriel simple : airlines = airline
        if w not in STOPWORDS:
            out.add(w)
    return out


FR_HINTS = {"le", "la", "les", "des", "une", "un", "du", "contre", "pour", "dans", "sur", "avec", "par", "est", "sont", "aux"}


def language(title):
    words = set(re.findall(r"[a-zà-ÿ]+", title.lower()))
    return "fr" if words & FR_HINTS or re.search(r"[éèêàçù]", title.lower()) else "en"


def entity_words(title):
    """Mots d'origine qui ressemblent à des noms propres (voir entities)."""
    words = re.findall(r"[A-Za-zÀ-ÿ0-9][\wÀ-ÿ\-]{1,}", title)
    if not words:
        return []
    title_case = sum(1 for w in words if w[0].isupper()) / len(words) > 0.6
    out = []
    for w in words:
        acronym = len(w) >= 3 and w.isupper() and w.isalpha()
        inner = any(any(c.isupper() for c in p[1:]) and any(c.islower() for c in p) for p in w.split("-"))
        capitalised = w[0].isupper() and not title_case
        if (acronym or inner or capitalised) and tokens(w):
            out.append(w)
    return out


def entities(title):
    """Mots qui ressemblent à des noms propres : majuscule en milieu de phrase (seulement dans
    les titres « en phrase », pas Title Case), sigles (EFS, ESG) et noms à majuscule interne
    (DreamHost, OFBiz). Ce sont eux qui désignent un sujet : « network » ne suffit pas."""
    words = re.findall(r"[A-Za-zÀ-ÿ0-9][\wÀ-ÿ\-]{1,}", title)
    if not words:
        return set()
    title_case = sum(1 for w in words if w[0].isupper()) / len(words) > 0.6
    out = set()
    for w in words:
        acronym = len(w) >= 3 and w.isupper() and w.isalpha()
        # majuscule interne dans un même morceau (DreamHost), pas après un tiret (Zero-Day)
        inner = any(any(c.isupper() for c in p[1:]) and any(c.islower() for c in p) for p in w.split("-"))
        # titre « en phrase » : toute majuscule est significative, y compris le premier mot,
        # qui est souvent le nom de l'entreprise (« Zyxel fixes… »)
        capitalised = w[0].isupper() and not title_case
        if acronym or inner or capitalised:
            out |= tokens(w)
    return out


def cluster(items, max_gap_days=7):
    """Regroupe les articles d'un même sujet : même CVE, ou même nom propre (entreprise,
    produit, groupe) peu fréquent dans la période."""
    n = len(items)
    toks = [tokens(x["title"]) for x in items]
    known_entities = set()
    for x in items:
        known_entities |= entities(x["title"])
    cves = [set(c.upper() for c in CVE.findall(x["title"])) for x in items]
    langs = [language(x["title"]) for x in items]
    dates = [parse_date(x["date"]) for x in items]
    df = {}
    for ts in toks:
        for t in ts:
            df[t] = df.get(t, 0) + 1
    rare_limit = max(3, math.ceil(n * 0.02))
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def close(i, j):
        return abs((dates[i] - dates[j]).days) <= max_gap_days

    index = {}
    for i in range(n):
        for t in toks[i]:
            if df[t] <= rare_limit:
                index.setdefault(("t", t), []).append(i)
        for c in cves[i]:
            index.setdefault(("c", c), []).append(i)
    for (kind, key), members in index.items():
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                i, j = members[a], members[b]
                if not close(i, j) or find(i) == find(j):
                    continue
                # même CVE ; ou même nom propre peu fréquent (Zyxel, Amadeus…). Pour un grand éditeur
                # (« Apple » seul relierait des sujets sans rapport), il faut un second mot commun.
                shared = toks[i] & toks[j]
                entity = key in known_entities
                if key in BIG_VENDORS:
                    entity = entity and (len(shared) >= 2 or langs[i] != langs[j])
                if kind == "c" or entity:
                    parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(items[i])
    out = []
    for members in groups.values():
        members.sort(key=lambda x: (PRIORITY.get(x["source"], 99), x["date"]))
        sources = []
        for m in members:
            if SOURCE_NAMES[m["source"]] not in [SOURCE_NAMES[s["source"]] for s in sources]:
                sources.append(m)
        total = {}
        for m in members:
            for k, v in (m.get("kinds") or fx.kind_scores(m["title"])).items():
                total[k] = total.get(k, 0) + v
        actor_ids = list(dict.fromkeys(a for m in members for a in (m.get("actors") or [])))
        for k, v in fx.actor_kind_bonus(actor_ids).items():
            total[k] = total.get(k, 0) + v
        cve_set = set()
        for m in members:
            cve_set |= {c.upper() for c in CVE.findall(m["title"])} | set(m.get("cves") or [])
        out.append({
            "lead": members[0],
            "members": sorted(members, key=lambda x: x["date"]),
            "kinds": fx.rank_kinds(total),
            "cves": sorted(cve_set),
            "actors": actor_ids,
            "sources": sources,
            "zero_day": any(m["zero_day"] for m in members),
            "date": max(m["date"] for m in members),
            "first": min(m["date"] for m in members),
        })
    out.sort(key=lambda c: (len(c["sources"]), c["date"]), reverse=True)
    return out


# --------------------------------------------------------------------------- page
def L(fr, en):
    return f'<span lang="fr">{fr}</span><span lang="en">{en}</span>'


def e(s):
    return html.escape(str(s), quote=True)


def day(iso):
    d = parse_date(iso)
    return d.astimezone(PARIS).strftime("%d/%m/%Y") if d else ""


def link(url, text):
    url = safe_url(url)
    if not url:
        return e(text)
    return f'<a href="{e(url)}" rel="noopener nofollow" target="_blank">{e(text)}</a>'


MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_day(iso):
    d = parse_date(iso)
    if not d:
        return "", ""
    d = d.astimezone(PARIS)
    return f"{d.day} {MONTHS_FR[d.month - 1]} {d.year}", f"{MONTHS_EN[d.month - 1]} {d.day}, {d.year}"


def kind_label(kind):
    fr, en = fx.PLAYBOOKS[kind]["label"]
    return L(e(fr), e(en))


def join_list(words, last_fr="et", last_en="and"):
    words = list(words)
    if len(words) <= 1:
        return "".join(words), "".join(words)
    return (", ".join(words[:-1]) + f" {last_fr} " + words[-1], ", ".join(words[:-1]) + f" {last_en} " + words[-1])


def render_clusters(clusters, limit, empty_fr, empty_en, fiches=None):
    if not clusters:
        return f'<p class="news-empty">{L(empty_fr, empty_en)}</p>'
    rows = []
    for c in clusters[:limit]:
        lead = c["lead"]
        n = len(c["sources"])
        kind = c.get("kinds", ["intrusion"])[0]
        fid = "f-" + re.sub(r"[^0-9a-f]", "", lead["id"])[:16]
        if fiches is not None and (fid not in fiches or len(fiches[fid]["sources"]) < n):
            fiches[fid] = c
        badge = '<span class="news-badge news-badge--zero">zero-day</span> ' if c["zero_day"] else ""
        srcs = " · ".join(link(s["url"], SOURCE_NAMES[s["source"]]) for s in c["sources"])
        count = L(f"{n} source{'s' if n > 1 else ''}", f"{n} source{'s' if n > 1 else ''}")
        # pas d'attribut lang sur les titres : la feuille de style masque les éléments [lang]
        rows.append(f'<li class="news-row news-row--{kind}">'
                    f'<a class="news-open" href="#{fid}" aria-haspopup="dialog">'
                    f'<span class="news-date">{day(c["first"])}</span> <span class="news-kind">{kind_label(kind)}</span> {badge}'
                    f'<span class="news-title">{e(lead["title"])}</span>'
                    f'<span class="news-cta" aria-hidden="true">{L("fiche", "details")} ›</span></a>'
                    f'<span class="news-meta"><span class="news-count">{count}</span> {srcs}</span></li>')
    return '<ol class="news-list">' + "".join(rows) + "</ol>"


def kev_index(kev):
    out = {}
    for v in (kev or {}).get("vulnerabilities", []):
        cve = str(v.get("cveID", ""))
        if re.fullmatch(r"CVE-\d{4}-\d{4,7}", cve):
            out[cve] = v
    return out


def kev_date(v):
    added = str(v.get("dateAdded", ""))
    return "/".join(reversed(added.split("-"))) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", added) else ""


def render_kev(kev, now, fiches=None):
    if not kev:
        return f'<p class="news-empty">{L("Catalogue de la CISA momentanément indisponible.", "CISA catalogue temporarily unavailable.")}</p>'
    vulns = kev.get("vulnerabilities", [])
    since = (now - dt.timedelta(days=30)).date().isoformat()
    year = str(now.astimezone(PARIS).year)
    recent = sorted((v for v in vulns if str(v.get("dateAdded", "")) >= since), key=lambda v: v.get("dateAdded", ""), reverse=True)
    this_year = sum(1 for v in vulns if str(v.get("dateAdded", "")).startswith(year))
    ransom = sum(1 for v in recent if v.get("knownRansomwareCampaignUse") == "Known")
    rows = []
    for v in recent[:12]:
        cve = str(v.get("cveID", ""))
        if not re.fullmatch(r"CVE-\d{4}-\d{4,7}", cve):
            continue
        fid = "k-" + cve.lower()
        if fiches is not None:
            fiches[fid] = v
        known = v.get("knownRansomwareCampaignUse") == "Known"
        badge = f' <span class="news-badge news-badge--ransom">{L("rançongiciel", "ransomware")}</span>' if known else ""
        rows.append(f'<li class="news-row news-row--{"ransomware" if known else "exploit"}">'
                    f'<a class="news-open" href="#{fid}" aria-haspopup="dialog">'
                    f'<span class="news-date">{e(kev_date(v))}</span> '
                    f'<span class="news-title">{e(cve)} — {e(v.get("vendorProject", ""))} {e(v.get("product", ""))}</span>{badge}'
                    f'<span class="news-cta" aria-hidden="true">{L("fiche", "details")} ›</span></a>'
                    f'<span class="news-meta">{e(v.get("vulnerabilityName", ""))}</span></li>')
    stats = L(f"<strong>{len(recent)}</strong> failles ajoutées ces 30 derniers jours (dont {ransom} utilisées par des rançongiciels), <strong>{this_year}</strong> depuis le 1er janvier.",
              f"<strong>{len(recent)}</strong> flaws added in the last 30 days ({ransom} used by ransomware), <strong>{this_year}</strong> since January 1.")
    body = '<ol class="news-list">' + "".join(rows) + "</ol>" if rows else f'<p class="news-empty">{L("Aucune faille ajoutée ces 30 derniers jours.", "No flaw added in the last 30 days.")}</p>'
    more = ""
    if len(recent) > 12:
        more = (f'<p class="news-more">{link("https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "→")} '
                f'{L(f"Les 12 plus récentes sur {len(recent)} : voir le catalogue complet de la CISA.", f"The 12 most recent of {len(recent)}: see the full CISA catalogue.")}</p>')
    return f'<p class="news-stats">{stats}</p>{body}{more}'


# --------------------------------------------------------------------------- fiches détaillées
def render_chain(kind):
    techs = fx.ref().get("techniques", {})
    steps = []
    for i, (tfr, ten, xfr, xen, ids) in enumerate(fx.PLAYBOOKS[kind]["phases"], 1):
        chips = "".join(
            f'<a class="chain__ttp" href="{e(techs[t]["url"])}" rel="noopener" target="_blank" title="MITRE ATT&amp;CK">'
            f'<b>{e(t)}</b> {e(techs[t]["name"])}</a>'
            for t in ids if t in techs and safe_url(techs[t].get("url")))
        steps.append(f'<li class="chain__step"><span class="chain__node" aria-hidden="true">{i}</span>'
                     f'<div class="chain__body"><h5>{L(e(tfr), e(ten))}</h5><p>{L(e(xfr), e(xen))}</p>'
                     + (f'<p class="chain__ttps">{chips}</p>' if chips else "") + '</div></li>')
    return '<ol class="chain">' + "".join(steps) + "</ol>"


def render_protect(kind):
    return '<ul class="fiche__protect">' + "".join(f"<li>{L(e(fr), e(en))}</li>" for fr, en in fx.PLAYBOOKS[kind]["protect"]) + "</ul>"


def schema_sentence(kind):
    phases = fx.PLAYBOOKS[kind]["phases"]
    fr = " → ".join(p[0].lower() for p in phases)
    en = " → ".join(p[1].lower() for p in phases)
    return f"Schéma classique : {fr}.", f"Typical pattern: {en}."


def fiche_shell(fid, kind, kicker, title, body):
    pb = fx.PLAYBOOKS[kind]
    return f"""<section class="fiche fiche--{kind}" id="{fid}" role="dialog" aria-modal="true" aria-labelledby="{fid}-t">
<a class="fiche__backdrop" href="#_" data-fiche-close tabindex="-1" aria-hidden="true"></a>
<div class="fiche__panel" tabindex="-1">
<div class="fiche__bar"><a class="fiche__close" href="#_" data-fiche-close>{L("Fermer", "Close")} <span aria-hidden="true">✕</span></a></div>
<header class="fiche__head">
<p class="fiche__kicker"><span class="fiche__type"><span class="fiche__dot" aria-hidden="true"></span>{kind_label(kind)}</span> {kicker}</p>
<h3 class="fiche__title" id="{fid}-t">{title}</h3>
<p class="fiche__def">{L(e(pb["def"][0]), e(pb["def"][1]))}</p>
</header>
{body}
<p class="fiche__legal">{L(
    "Fiche générée automatiquement à partir des titres et des faits publiés par les sources ; le déroulé est le schéma type de cette catégorie d'attaque, pas la reconstitution exacte de cet incident. Techniques et groupes : MITRE ATT&amp;CK® (© The MITRE Corporation, reproduit avec autorisation). Failles : catalogue KEV de la CISA (domaine public).",
    "Automatically generated from the headlines and facts published by the sources; the sequence is the typical pattern of this attack category, not an exact reconstruction of this incident. Techniques and groups: MITRE ATT&amp;CK® (© The MITRE Corporation, reproduced with permission). Flaws: CISA KEV catalogue (public domain).")}</p>
</div>
</section>"""


def block(title_fr, title_en, inner, cls=""):
    return f'<section class="fiche__block {cls}"><h4>{L(title_fr, title_en)}</h4>{inner}</section>'


def fact(label_fr, label_en, value):
    return f"<dt>{L(label_fr, label_en)}</dt><dd>{value}</dd>"


def kev_line(v):
    cve = v["cveID"]
    known = v.get("knownRansomwareCampaignUse") == "Known"
    extra = L(" — utilisée par des rançongiciels", " — used by ransomware") if known else ""
    return (f'{link("https://nvd.nist.gov/vuln/detail/" + cve, cve)} '
            f'{L(f"(catalogue CISA depuis le {e(kev_date(v))})", f"(CISA catalogue since {e(kev_date(v))})")}{extra}')


# mots fréquents en tête de titre qui ne désignent pas une entreprise ou un produit
COMMON_LEADS = set("""
russian chinese iranian north korean french american european british german japanese indian israeli ukrainian
pro-russian new hackers hacker attackers police government hospital hospitals city cities state national global
major massive critical researchers experts report hôpital hôpitaux mairie ville région gouvernement ministère
police gendarmerie santé banque école université nouvelle nouveau grande fuite piratage alerte attention
""".split())


def render_fiche(fid, c, kevs):
    kind = c["kinds"][0]
    members = c["members"]
    titles = [m["title"] for m in members]
    actors = fx.find_actors(titles)
    seen = {a["id"] for _, a in actors}
    for aid in c.get("actors", []):
        a = fx.actor_by_id(aid)
        if a and aid not in seen and len(actors) < 4:
            actors.append((a["name"], a))
            seen.add(aid)
    actor_names = {a["name"].lower() for _, a in actors} | {m.lower() for m, _ in actors}
    counts = {}
    lower_words = {w.lower() for t in titles for w in re.findall(r"\b[a-zà-ÿ][\wà-ÿ-]*", t)}
    for t in titles:
        words = entity_words(t)
        first = (re.findall(r"[A-Za-zÀ-ÿ0-9][\wÀ-ÿ\-]{1,}", t) or [""])[0]
        for w in words:
            if w.lower() in actor_names or CVE.fullmatch(w) or re.fullmatch(r"\d.*", w):
                continue
            # premier mot d'un titre : majuscule de début de phrase, pas forcément un nom propre
            # (« Hôpital régional… ») : on le garde si c'est un sigle, un nom à majuscule interne,
            # ou s'il n'est pas un mot courant
            if w == first and not (w.isupper() or any(c.isupper() for c in w[1:])) and (
                    w.lower() in lower_words or w.lower() in COMMON_LEADS):
                continue
            key = w.lower()
            counts.setdefault(key, [w, 0])[1] += 1
    names = [w for w, _ in sorted(counts.values(), key=lambda x: -x[1])][:6]
    n = len(c["sources"])
    src_names = [SOURCE_NAMES[s["source"]] for s in c["sources"]]

    facts = [fact("Type", "Type", kind_label(kind) + (
        " · " + L("aussi : ", "also: ") + ", ".join(kind_label(k) for k in c["kinds"][1:]) if len(c["kinds"]) > 1 else ""))]
    period = day(c["first"]) + (f" → {day(c['date'])}" if day(c["first"]) != day(c["date"]) else "")
    facts.append(fact("Période", "Period", e(period)))
    facts.append(fact("Sources", "Sources", f'<span class="news-count">{n}</span> ' + e(", ".join(src_names))))
    if names:
        facts.append(fact("Noms cités", "Names mentioned", e(", ".join(names))))
    cve_lines = []
    for cve in c["cves"][:6]:
        cve_lines.append(kev_line(kevs[cve]) if cve in kevs else link("https://nvd.nist.gov/vuln/detail/" + cve, cve))
    if cve_lines:
        facts.append(fact("Failles (CVE)", "Flaws (CVE)", "<br>".join(cve_lines)))
    for matched, a in actors:
        kind_fr, kind_en = ("Groupe cité", "Group mentioned") if a["kind"] == "group" else ("Logiciel cité", "Malware mentioned")
        facts.append(fact(kind_fr, kind_en,
                          f'{link(a["url"], a["name"])} <span class="fiche__id">{e(a["id"])}</span>'
                          f'<span class="fiche__quote">{e(a["desc"])}</span>'))

    # résumé à réexpliquer
    dfr, den = long_day(c["first"])
    pfr, pen = fx.PLAYBOOKS[kind]["phrase"]
    nfr, nen = join_list([e(x) for x in src_names])
    who_fr = f"{n} média{'s' if n > 1 else ''} ({nfr}) rapporte{'nt' if n > 1 else ''}"
    who_en = f"{n} outlet{'s' if n > 1 else ''} ({nen}) report{'' if n > 1 else 's'}"
    ent_fr, ent_en = join_list([e(x) for x in names[:3]])
    fr = f"Le {dfr}, {who_fr} {pfr}" + (f" impliquant {ent_fr}" if names else "") + "."
    en = f"On {den}, {who_en} {pen}" + (f" involving {ent_en}" if names else "") + "."
    kev_hit = [kevs[x] for x in c["cves"] if x in kevs]
    if kev_hit:
        v = kev_hit[0]
        vp = e(f'{v.get("vendorProject", "")} {v.get("product", "")}'.strip())
        known = v.get("knownRansomwareCampaignUse") == "Known"
        fr += f" La faille {e(v['cveID'])} ({vp}) est confirmée exploitée par la CISA" + (", y compris par des rançongiciels." if known else ".")
        en += f" Flaw {e(v['cveID'])} ({vp}) is confirmed exploited by CISA" + (", including by ransomware." if known else ".")
    elif c["zero_day"] and kind != "exploit":
        fr += " Une faille zero-day est en jeu."
        en += " A zero-day flaw is involved."
    if actors:
        a = actors[0][1]
        fr += f" Les articles citent {e(a['name'])}, référencé par MITRE ATT&amp;CK ({e(a['id'])})."
        en += f" The articles mention {e(a['name'])}, tracked by MITRE ATT&amp;CK ({e(a['id'])})."
    sfr, sen = schema_sentence(kind)
    pitch = (f'<div class="fiche__term"><div class="fiche__termbar"><span class="fiche__prompt" aria-hidden="true">$ explain --30s</span><button class="fiche__copy" type="button">{L("copier", "copy")}</button></div>'
             f'<p class="fiche__pitch">{L(fr + " " + sfr, en + " " + sen)}<span class="fiche__caret" aria-hidden="true"></span></p></div>')

    articles = "".join(
        f'<li><span class="news-date">{day(m["date"])}</span> {link(m["url"], m["title"])} '
        f'<span class="fiche__src">{e(SOURCE_NAMES[m["source"]])}</span></li>' for m in members[:12])
    body = (block("Les faits", "The facts", f'<dl class="fiche__facts">{"".join(facts)}</dl>')
            + block("Comment s'organise ce type d'attaque", "How this type of attack unfolds",
                    f'<p class="fiche__note">{L("Schéma type, phase par phase, avec les techniques MITRE ATT&amp;CK correspondantes.", "Typical pattern, phase by phase, with the matching MITRE ATT&amp;CK techniques.")}</p>'
                    + render_chain(kind))
            + block("Pour le réexpliquer en 30 secondes", "Explain it in 30 seconds", pitch, "fiche__block--pitch")
            + block("Se protéger", "How to defend", render_protect(kind))
            + block("Lire les articles", "Read the articles", f'<ul class="fiche__articles">{articles}</ul>'))
    zero = ' <span class="news-badge news-badge--zero">zero-day</span>' if c["zero_day"] else ""
    kicker = f'<span class="fiche__meta">{day(c["first"])} · {L(f"{n} source" + ("s" if n > 1 else ""), f"{n} source" + ("s" if n > 1 else ""))}</span>{zero}'
    return fiche_shell(fid, kind, kicker, e(c["lead"]["title"]), body)


def render_kev_fiche(fid, v, archive):
    cve = v["cveID"]
    known = v.get("knownRansomwareCampaignUse") == "Known"
    vp = f'{v.get("vendorProject", "")} {v.get("product", "")}'.strip()
    facts = [
        fact("Faille", "Flaw", e(v.get("vulnerabilityName", ""))),
        fact("Produit", "Product", e(vp)),
        fact("Ajoutée au catalogue", "Added to catalogue", e(kev_date(v))),
    ]
    due = str(v.get("dueDate", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", due):
        facts.append(fact("Échéance (agences fédérales américaines)", "Deadline (US federal agencies)", e("/".join(reversed(due.split("-"))))))
    facts.append(fact("Rançongiciels", "Ransomware", L("utilisation connue", "known use") if known else L("pas d'utilisation connue", "no known use")))
    cwes = [c for c in v.get("cwes", []) if isinstance(c, str) and re.fullmatch(r"CWE-\d{1,5}", c)]
    if cwes:
        facts.append(fact("Catégorie (CWE)", "Weakness (CWE)", ", ".join(
            link(f"https://cwe.mitre.org/data/definitions/{c[4:]}.html", c) for c in cwes)))
    facts.append(fact("Fiches de référence", "References", link("https://nvd.nist.gov/vuln/detail/" + cve, "NVD") + " · "
                      + link("https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext=" + cve, "CISA")))
    official = ""
    if v.get("shortDescription"):
        official = (f'<p class="fiche__note">{L("Texte officiel de la CISA (en anglais) :", "Official CISA text:")}</p>'
                    f'<blockquote class="fiche__official">{e(v.get("shortDescription", ""))}'
                    + (f'<br><br><b>{L("Action requise", "Required action")} :</b> {e(v.get("requiredAction", ""))}' if v.get("requiredAction") else "")
                    + "</blockquote>")
    related = [x for x in archive if cve in (x.get("cves") or [])][:8]
    articles = "".join(f'<li><span class="news-date">{day(m["date"])}</span> {link(m["url"], m["title"])} '
                       f'<span class="fiche__src">{e(SOURCE_NAMES[m["source"]])}</span></li>' for m in related)
    dfr, den = long_day(str(v.get("dateAdded", "")) + "T12:00:00+00:00")
    fr = (f"Le {dfr}, la CISA a ajouté {e(cve)}, une faille de {e(vp)} ({e(v.get('vulnerabilityName', ''))}), à son catalogue des failles "
          f"exploitées : des attaques réelles sont confirmées" + (", y compris par des rançongiciels." if known else ".") + " Il faut corriger en priorité.")
    en = (f"On {den}, CISA added {e(cve)}, a flaw in {e(vp)} ({e(v.get('vulnerabilityName', ''))}), to its catalogue of exploited "
          f"vulnerabilities: real-world attacks are confirmed" + (", including by ransomware." if known else ".") + " It must be patched first.")
    sfr, sen = schema_sentence("exploit")
    pitch = (f'<div class="fiche__term"><div class="fiche__termbar"><span class="fiche__prompt" aria-hidden="true">$ explain --30s</span><button class="fiche__copy" type="button">{L("copier", "copy")}</button></div>'
             f'<p class="fiche__pitch">{L(fr + " " + sfr, en + " " + sen)}<span class="fiche__caret" aria-hidden="true"></span></p></div>')
    body = (block("Les faits", "The facts", f'<dl class="fiche__facts">{"".join(facts)}</dl>{official}')
            + block("Comment s'organise ce type d'attaque", "How this type of attack unfolds",
                    f'<p class="fiche__note">{L("Schéma type de l’exploitation d’une faille, avec les techniques MITRE ATT&amp;CK correspondantes.", "Typical pattern of flaw exploitation, with the matching MITRE ATT&amp;CK techniques.")}</p>'
                    + render_chain("exploit"))
            + block("Pour le réexpliquer en 30 secondes", "Explain it in 30 seconds", pitch, "fiche__block--pitch")
            + block("Se protéger", "How to defend", render_protect("exploit"))
            + (block("Dans l'actualité", "In the news", f'<ul class="fiche__articles">{articles}</ul>') if related else ""))
    ransom = f' <span class="news-badge news-badge--ransom">{L("rançongiciel", "ransomware")}</span>' if known else ""
    kicker = f'<span class="fiche__meta">{e(kev_date(v))} · CISA KEV</span>{ransom}'
    return fiche_shell(fid, "ransomware" if known else "exploit", kicker, f"{e(cve)} — {e(vp)}", body)


def render_fiches(fiches, kev, archive):
    kevs = kev_index(kev)
    out = []
    for fid, obj in fiches.items():
        if fid.startswith("k-"):
            out.append(render_kev_fiche(fid, obj, archive))
        else:
            out.append(render_fiche(fid, obj, kevs))
    return '<div class="news-fiches">' + "\n".join(out) + "</div>"


def render_selection(selection):
    rows = []
    for s in selection:
        srcs = " · ".join(link(x.get("url"), x.get("name", "")) for x in s.get("sources", []) if safe_url(x.get("url")))
        if not srcs:
            continue
        rows.append(f'<li><span class="news-date">{e(s.get("date", ""))}</span> '
                    f'<span class="news-title">{L(e(s.get("title_fr", "")), e(s.get("title_en", s.get("title_fr", ""))))}</span>'
                    f'<span class="news-meta">{srcs}</span></li>')
    if not rows:
        return ""
    return (f'<h4 class="news-subtitle">{L("Sélection", "Selection")}</h4><ol class="news-list news-list--selection">'
            + "".join(rows) + "</ol>")


def build_body(archive, kev, selection, status, now, fiches=None):
    def window(days=None, since=None):
        out = []
        for x in archive:
            d = parse_date(x["date"])
            if days is not None and d < now - dt.timedelta(days=days):
                continue
            if since is not None and d < since:
                continue
            out.append(x)
        return out

    year_start = dt.datetime(now.astimezone(PARIS).year, 1, 1, tzinfo=PARIS).astimezone(dt.timezone.utc)
    zero_news = cluster([x for x in window(days=30) if x["zero_day"]])
    week = cluster([x for x in window(days=7) if x["attack"]])
    month = cluster([x for x in window(days=30) if x["attack"]], max_gap_days=10)
    year = cluster([x for x in window(since=year_start) if x["attack"]], max_gap_days=14)
    oldest = min((x["date"] for x in archive), default=None)
    updated = now.astimezone(PARIS).strftime("%d/%m/%Y %H:%M")

    src_list = "".join(
        f'<li>{link(s["home"], s["name"])} — {"✓" if status.get(s["id"]) == "ok" else L("indisponible lors de la dernière mise à jour", "unavailable at last update")}</li>'
        for s in SOURCES if s["id"] != "certfr-cti")
    src_list += f'<li>{link("https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "CISA — Known Exploited Vulnerabilities")} — {"✓" if status.get("kev") == "ok" else L("indisponible", "unavailable")}</li>'
    history = (L(f"Historique depuis le {day(oldest)} : le classement de l'année s'enrichit au fil des semaines.",
                 f"History since {day(oldest)}: the yearly ranking grows week after week.") if oldest else "")

    return f"""<p class="tools-intro">{L(
        "La veille cyber du moment, mise à jour automatiquement toutes les 6 heures à partir de sources reconnues. Clique sur un sujet pour ouvrir sa fiche : type d'attaque, déroulé phase par phase, résumé à réexpliquer et liens vers les articles.",
        "Current cyber news, updated automatically every 6 hours from recognised sources. Click a story to open its sheet: attack type, phase-by-phase sequence, a summary to explain it, and links to the articles.")}</p>
<p class="news-updated">{L("Dernière mise à jour", "Last update")} : {e(updated)} ({L("heure de Paris", "Paris time")})</p>

<section class="news-section">
  <h3>{L("Failles zero-day et exploitées activement", "Zero-day and actively exploited flaws")}</h3>
  <p class="tools-theme__desc">{L(
      "Le catalogue officiel de la CISA (agence américaine de cybersécurité) recense les failles dont l'exploitation par des attaquants est confirmée. C'est la liste à patcher en priorité.",
      "The official catalogue of CISA (US cybersecurity agency) lists flaws whose exploitation by attackers is confirmed. This is the list to patch first.")}</p>
  {render_kev(kev, now, fiches)}
  <h4 class="news-subtitle">{L("Dans l'actualité (30 derniers jours)", "In the news (last 30 days)")}</h4>
  {render_clusters(zero_news, 12, "Aucun article sur une faille zero-day ces 30 derniers jours.", "No zero-day article in the last 30 days.", fiches)}
</section>

<section class="news-section">
  <h3>{L("Grosses attaques de la semaine", "Major attacks this week")}</h3>
  <p class="tools-theme__desc">{L("Les 7 derniers jours, classées par nombre de sources qui en parlent.", "The last 7 days, ranked by how many sources cover them.")}</p>
  {render_clusters(week, 10, "Rien de notable cette semaine pour l'instant.", "Nothing notable this week so far.", fiches)}
</section>

<section class="news-section">
  <h3>{L("Grosses attaques du mois", "Major attacks this month")}</h3>
  <p class="tools-theme__desc">{L("Les 30 derniers jours.", "The last 30 days.")}</p>
  {render_clusters(month, 12, "Pas encore assez d'historique.", "Not enough history yet.", fiches)}
</section>

<section class="news-section">
  <h3>{L("Grosses attaques de l'année", "Major attacks this year")}</h3>
  <p class="tools-theme__desc">{L("Depuis le 1er janvier.", "Since January 1.")} {history}</p>
  {render_selection(selection)}
  {render_clusters(year, 15, "Pas encore assez d'historique.", "Not enough history yet.", fiches)}
</section>

<section class="news-section">
  <h3>{L("Sources et méthode", "Sources and method")}</h3>
  <ul class="news-sources-list">{src_list}</ul>
  <p class="tools-theme__desc">{L(
      "Un article est retenu s'il parle d'une faille exploitée ou d'une attaque. Les articles qui traitent du même sujet sont regroupés (même CVE, même nom d'entreprise ou de produit) ; un sujet repris par plusieurs sources est classé plus haut. Ce classement est automatique : il peut regrouper ou séparer des sujets à tort. Vérifie toujours auprès des sources.",
      "An article is kept if it covers an exploited flaw or an attack. Articles about the same story are grouped (same CVE, same company or product name); a story covered by several sources ranks higher. This ranking is automatic: it can wrongly merge or split stories. Always check the sources.")}</p>
</section>"""


def retarget(template, body, extra=""):
    url = SITE + "/news/"
    desc = "Cyber news updated every 6 hours: actively exploited zero-day flaws and major attacks of the week, month and year, from recognised sources."
    s = re.sub(r"<title[^>]*>.*?</title>", '<title data-fr="Actus :: Manthole — Blog">News :: Manthole — Blog</title>', template, count=1, flags=re.S)
    for attr in ['name="description"', 'itemprop="description"', 'name="twitter:description"', 'property="og:description"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s, count=1)
    for attr in ['itemprop="name"', 'name="twitter:title"', 'property="og:title"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + "News" + m.group(2), s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', s, count=1)
    main = f"""<main class="post">
        <article>
            <h2 class="post-title"><a href="{url}">{L("Actus", "News")}</a></h2>
            <div class="post-content">
{body}
            </div>
        </article>
{extra}
    </main>"""
    s = re.sub(r'<main class="post"[^>]*>.*?</main>', lambda m: main, s, count=1, flags=re.S)
    return s.replace("</body>", '<script src="/js/news.js" defer></script>\n</body>', 1)


# --------------------------------------------------------------------------- programme principal
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--offline", action="store_true", help="aucun accès réseau (page de secours, tests)")
    args = ap.parse_args(argv)
    root = Path(args.root)
    now = dt.datetime.now(dt.timezone.utc)
    status, fresh = {}, []

    archive = []
    if not args.offline:
        # L'archive publiée est la mémoire de la page. Une 404 signifie « première exécution » :
        # on repart de zéro. Toute autre erreur arrête tout, pour ne jamais publier une archive
        # vide par accident : GitHub Pages garde alors en ligne la version précédente.
        try:
            data = json.loads(fetch(ARCHIVE_URL))
            archive = data.get("items", []) if isinstance(data, dict) else []
            print(f"archive publiée : {len(archive)} articles")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                print(f"archive publiée inaccessible (HTTP {exc.code}) : arrêt pour ne pas perdre l'historique")
                return 1
            print("pas encore d'archive publiée : première exécution")
        for src in SOURCES:
            try:
                got = items_from_feed(src, fetch(src["feed"]), now)
                fresh += got
                status[src["id"]] = "ok"
                print(f"ok    {src['name']:<20} {len(got)} article(s) retenu(s)")
            except Exception as exc:
                status[src["id"]] = "erreur"
                print(f"ERR   {src['name']:<20} {type(exc).__name__}: {str(exc)[:120]}")
        if status.get("certfr") == "ok" or status.get("certfr-cti") == "ok":
            status["certfr"] = "ok"
    kev = None
    if not args.offline:
        try:
            kev = json.loads(fetch(KEV_URL))
            if not isinstance(kev, dict) or not isinstance(kev.get("vulnerabilities"), list):
                raise ValueError("format inattendu")
            status["kev"] = "ok"
            print(f"ok    CISA KEV             {len(kev['vulnerabilities'])} failles (version {kev.get('catalogVersion')})")
        except Exception as exc:
            kev = None
            print(f"ERR   CISA KEV             {type(exc).__name__}: {str(exc)[:120]}")

    items = merge(archive, fresh, now)
    selection = []
    sel_path = root / "data" / "news-selection.json"
    if sel_path.exists():
        try:
            selection = json.loads(sel_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            print(f"news-selection.json illisible : {exc}")

    template = (root / "about" / "index.html").read_text(encoding="utf-8")
    fiches = {}
    body = build_body(items, kev, selection, status, now, fiches)
    page = retarget(template, body, render_fiches(fiches, kev, items))
    out = root / "news" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "news-archive.json").write_text(
        json.dumps({"updated": now.isoformat(timespec="seconds"), "items": items}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    print(f"page écrite : {out} ({len(items)} articles en archive)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
