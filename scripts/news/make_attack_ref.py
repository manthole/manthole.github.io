#!/usr/bin/env python3
"""Extrait de MITRE ATT&CK le petit référentiel utilisé par les fiches de la page Actus.

À relancer à la main quand ATT&CK publie une nouvelle version (deux fois par an) :
    git clone --depth 1 --filter=blob:none --sparse https://github.com/mitre-attack/attack-stix-data.git stix
    git -C stix sparse-checkout set --no-cone /enterprise-attack/enterprise-attack.json /ics-attack/ics-attack.json
    python3 scripts/news/make_attack_ref.py stix/enterprise-attack/enterprise-attack.json stix/ics-attack/ics-attack.json

Sortie : scripts/news/attack_ref.json
- techniques : celles citées dans fiches.PLAYBOOKS (nom officiel + lien) ;
- actors : groupes et logiciels malveillants (nom, alias, première phrase de la description).
© The MITRE Corporation. Reproduit et distribué avec l'autorisation de The MITRE Corporation.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiches  # noqa: E402

# Noms trop courants dans des titres d'actualité ordinaires : ils provoqueraient des faux positifs.
AMBIGUOUS = set("""
agenda anchor apostle armageddon aurora avenger axiom bazar cannon carbon chaos chimera cicada cleaver comnie
confucius crimson crutch cuba denis disco dok doki elise embargo epic equation explosive flame flamer havoc helminth
icebot inception james karma kessel kevin kido komplex krypton leviathan linfo lucifer machete mafalda mango mantis
matryoshka maze megazord meteor milan mirage moneybird mosquito nebulae newscaster ninja octopus okrum page pandora
patchwork penquin peppy play pony prestige proton raindrop ramsay rancor rattlesnake reaper reaver remsec rover royal
samurai scorpion seasalt shark sibot silence snake solar soldier spark spica strider tick tomiris torisma trinity
truvasys tunnus turian valak waterbear windigo wiper zinc nickel mercury silicon rtm gref taal webmasters projectm
controlx msupdater
""".split())
SHORT_OK = {"Ryuk", "Clop", "QBot", "Duqu", "Pysa", "APT1", "APT2", "APT3", "APT5", "FIN4", "FIN5", "FIN6", "FIN7", "FIN8", "WCry"}


def ext_id(o):
    for r in o.get("external_references", []):
        if r.get("source_name") in ("mitre-attack", "mitre-ics-attack") and r.get("external_id"):
            return r["external_id"], r.get("url", "")
    return None, None


def first_sentence(text):
    text = re.sub(r"\(Citation:[^)]*\)", "", text or "")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.{40,320}?[.!?])(?:\s|$)", text)
    return (m.group(1) if m else text[:320]).strip()


def good_name(n):
    if not n or n.lower() in AMBIGUOUS:
        return False
    if len(n) < 5 and n not in SHORT_OK:
        return False
    return not n.islower()


def main(paths):
    objs = []
    for p in paths:
        objs += json.loads(Path(p).read_text(encoding="utf-8"))["objects"]
    live = [o for o in objs if not o.get("revoked") and not o.get("x_mitre_deprecated")]
    techniques = {}
    for o in live:
        if o.get("type") == "attack-pattern":
            i, u = ext_id(o)
            if i:
                techniques[i] = {"name": o["name"], "url": u}
    used = {t for pb in fiches.PLAYBOOKS.values() for ph in pb["phases"] for t in ph[4]}
    missing = sorted(used - techniques.keys())
    if missing:
        sys.exit(f"techniques absentes d'ATT&CK : {missing}")
    actors = []
    for o in live:
        if o.get("type") not in ("intrusion-set", "malware"):
            continue
        i, u = ext_id(o)
        names = sorted({n for n in [o["name"]] + o.get("aliases", []) + o.get("x_mitre_aliases", []) if good_name(n)})
        if not i or not names:
            continue
        actors.append({"id": i, "name": o["name"], "kind": "group" if o["type"] == "intrusion-set" else "malware",
                       "url": u, "names": names, "desc": first_sentence(o.get("description", ""))})
    actors.sort(key=lambda a: a["id"])
    version = next((o.get("x_mitre_version") for o in objs if o.get("type") == "x-mitre-collection"), "")
    out = {"attack_version": version, "techniques": {k: techniques[k] for k in sorted(used)}, "actors": actors}
    dest = Path(__file__).resolve().parent / "attack_ref.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{dest} : {len(used)} techniques, {len(actors)} groupes et logiciels (ATT&CK {version})")


if __name__ == "__main__":
    main(sys.argv[1:])
