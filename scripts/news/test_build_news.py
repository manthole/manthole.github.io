"""Tests hors ligne du générateur d'actualités : python3 -m unittest scripts/news/test_build_news.py"""
import datetime as dt
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_news as bn  # noqa: E402

NOW = dt.datetime(2026, 11, 5, 20, 0, tzinfo=dt.timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


def rss(*items):
    body = "".join(
        f"<item><title>{t}</title><link>{l}</link><pubDate>{d}</pubDate><description>{s}</description></item>"
        for t, l, d, s in items)
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>{body}</channel></rss>'.encode()


def item(title, source, day, zero=False, attack=True, url=None):
    url = url or f"https://{source}.example/{abs(hash((title, source))) % 10**8}"
    return {"id": bn.hashlib.sha1(url.encode()).hexdigest()[:16], "title": title, "url": url, "source": source,
            "date": dt.datetime(2026, 11, day, 12, tzinfo=dt.timezone.utc).isoformat(), "zero_day": zero, "attack": attack}


class Feeds(unittest.TestCase):
    def test_rss_classification(self):
        data = rss(
            ("Zyxel fixes zero-day exploited to hack 1,000 switches", "https://a.example/1", "Wed, 04 Nov 2026 15:58:19 -0500", "x"),
            ("Ransomware gang hits hospital chain", "https://a.example/2", "Wed, 04 Nov 2026 10:00:00 +0000", ""),
            ("Cyberattaque contre les frigos de l'EFS", "https://a.example/3", "Thu, 05 Nov 2026 16:36:51 +0000", ""),
            ("New AI feature for developers", "https://a.example/4", "Wed, 04 Nov 2026 10:00:00 +0000", "productivity"),
            ("Weekly Recap: breach, ransomware and more", "https://a.example/5", "Wed, 04 Nov 2026 10:00:00 +0000", ""),
        )
        got = {x["url"]: x for x in bn.items_from_feed({"id": "bleeping"}, data, NOW)}
        self.assertTrue(got["https://a.example/1"]["zero_day"])
        self.assertTrue(got["https://a.example/2"]["attack"])
        self.assertTrue(got["https://a.example/3"]["attack"], "titre français")
        self.assertNotIn("https://a.example/4", got, "hors sujet")
        self.assertNotIn("https://a.example/5", got, "récapitulatif exclu")

    def test_atom(self):
        data = (b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Data breach at Acme</title>'
                b'<link rel="alternate" href="https://b.example/x"/><updated>2026-11-04T10:00:00Z</updated></entry></feed>')
        got = bn.items_from_feed({"id": "record"}, data, NOW)
        self.assertEqual(got[0]["url"], "https://b.example/x")

    def test_hostile_feed(self):
        data = rss(
            ("&lt;script&gt;alert(1)&lt;/script&gt; ransomware", "javascript:alert(1)", "Wed, 04 Nov 2026 10:00:00 +0000", ""),
            ("Breach with quote", 'https://c.example/"onmouseover="x', "Wed, 04 Nov 2026 10:00:00 +0000", ""),
            ("Ransomware from the future", "https://c.example/f", "Wed, 04 Nov 2027 10:00:00 +0000", ""),
            ("Ransomware with bad date", "https://c.example/d", "pas une date", ""),
        )
        self.assertEqual(bn.items_from_feed({"id": "thn"}, data, NOW), [], "liens dangereux, dates futures ou invalides rejetés")
        bomb = b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;">]><rss><channel><item><title>&b;</title></item></channel></rss>'
        with self.assertRaises(ValueError):
            bn.parse_feed(bomb)

    def test_merge_prunes_and_validates(self):
        old = item("Old ransomware", "thn", 1)
        old["date"] = "2024-01-01T00:00:00+00:00"
        bad = {"id": "x", "title": "t", "url": "javascript:1", "source": "thn", "date": "2026-11-01T00:00:00+00:00", "zero_day": False, "attack": True}
        new = item("Fresh ransomware", "thn", 4)
        merged = bn.merge([old, bad, new], [new], NOW)
        self.assertEqual([x["title"] for x in merged], ["Fresh ransomware"])


class Clustering(unittest.TestCase):
    def test_same_story_grouped(self):
        items = [
            item("Zyxel fixes zero-day exploited to hack nearly 1,000 network switches", "bleeping", 4, zero=True),
            item("Zyxel Patches Actively Exploited Zero-Day in Network Switches", "thn", 4, zero=True),
            item("Apple fixes WebKit bug in Safari", "securityweek", 4),
            item("Apple pays record bug bounty", "record", 3),
            item("Amadeus breach: more Asian airlines notify passengers", "record", 4),
            item("Japanese airline confirms Amadeus incident", "bleeping", 5),
            item("Attackers exploit CVE-2026-111357 in Ivanti gateways", "thn", 2),
            item("Ivanti Connect Secure flaw CVE-2026-111357 under attack", "securityweek", 3),
        ]
        clusters = bn.cluster(items)
        sizes = sorted((len(c["sources"]), c["lead"]["title"][:10]) for c in clusters)
        by_lead = {c["lead"]["title"].split()[0]: len(c["sources"]) for c in clusters}
        self.assertEqual(by_lead.get("Zyxel"), 2, sizes)
        self.assertEqual(sum(1 for c in clusters if c["lead"]["title"].startswith("Apple")), 2, "deux sujets Apple distincts")
        self.assertTrue(any(len(c["sources"]) == 2 and "Amadeus" in c["lead"]["title"] + " ".join(s["title"] for s in c["sources"]) for c in clusters), sizes)
        self.assertTrue(any(len(c["sources"]) == 2 and "CVE-2026-111357" in c["lead"]["title"] for c in clusters), sizes)
        self.assertEqual(len(clusters[0]["sources"]), 2, "les sujets multi-sources en premier")

    def test_common_word_does_not_merge(self):
        # trouvé sur l'aperçu : « network » rapprochait à tort deux sujets sans rapport
        items = [
            item("Zyxel fixes zero-day exploited to hack nearly 1,000 network switches", "bleeping", 4, zero=True),
            item("Zyxel Patches Actively Exploited Zero-Day in Network Switches", "thn", 4, zero=True),
            item("Ransomware attack disrupts Jaguar dealer network across Europe", "bleeping", 1),
            item("Jaguar Dealer Network Hit by Ransomware, Systems Offline", "thn", 1),
        ]
        clusters = bn.cluster(items, max_gap_days=14)
        self.assertEqual(sorted(len(c["sources"]) for c in clusters), [2, 2], [c["lead"]["title"] for c in clusters])

    def test_entities(self):
        self.assertIn("dreamhost", bn.entities("DreamHost confirms breach of support systems"))
        self.assertIn("efs", bn.entities("Cyberattaque contre les frigos de l'EFS : le plasma visé"))
        self.assertNotIn("network", bn.entities("Zyxel Patches Actively Exploited Zero-Day in Network Switches"))
        self.assertIn("zyxel", bn.entities("Attackers hit Zyxel switches"))
        self.assertIn("zyxel", bn.entities("Zyxel fixes zero-day exploited to hack switches"), "premier mot d'un titre en phrase")
        self.assertEqual(bn.entities("Zyxel Patches Actively Exploited Zero-Day"), set(), "Title Case : rien, et surtout pas zero-day")

    def test_cross_language(self):
        items = [item("Zyxel fixes zero-day exploited to hack nearly 1,000 network switches", "bleeping", 4, zero=True),
                 item("Zyxel : une faille zero-day exploitée sur des commutateurs", "zataz", 4, zero=True)]
        self.assertEqual(len(bn.cluster(items)), 1, "même sujet en français et en anglais")
        same_lang = [item("Apple fixes WebKit bug in Safari", "securityweek", 4), item("Apple pays record bug bounty", "record", 4)]
        self.assertEqual(len(bn.cluster(same_lang)), 2)

    def test_real_titles_from_first_run(self):
        # titres réels du 5 novembre 2026 : un titre en phrase suffit à reconnaître le nom propre
        items = [item("Zyxel Switch Hacks Blamed on Patched Flaw Actually Exploited a Zero-Day", "securityweek", 5, zero=True),
                 item("Zyxel GS1900 Patch Fails to Block Zero-Day Exploit Allowing Root Command Execution", "thn", 5, zero=True),
                 item("Zyxel fixes zero-day exploited to hack nearly 1,000 network switches", "bleeping", 4, zero=True),
                 item("Siemens IoT2050 flaw exploited to plant backdoors", "thn", 3)]
        self.assertEqual(sorted(len(c["sources"]) for c in bn.cluster(items)), [1, 3])

    def test_cti_reports_skipped(self):
        self.assertIsNone(bn.classify("certfr-cti", "Panorama de la cybermenace 2025 (11 mars 2026)", "", "https://x/cti/1"))
        self.assertIsNotNone(bn.classify("certfr-cti", "Ciblage d'entités françaises par Turla", "", "https://x/cti/2"))
        old = item("Panorama de la cybermenace 2025", "certfr-cti", 2)
        self.assertEqual(bn.merge([old], [], NOW), [], "règle appliquée aussi à l'archive")

    def test_zero_day_alone_does_not_merge(self):
        items = [item("Apple fixes zero-day exploited in attacks", "bleeping", 4, zero=True),
                 item("Chrome zero-day exploited in the wild", "record", 4, zero=True)]
        self.assertEqual(len(bn.cluster(items)), 2)

    def test_far_apart_not_grouped(self):
        items = [item("Amadeus breach disclosed", "record", 1), item("Amadeus breach disclosed", "thn", 1)]
        items[1]["date"] = "2026-09-01T00:00:00+00:00"
        self.assertEqual(len(bn.cluster(items, max_gap_days=7)), 2)


class Page(unittest.TestCase):
    def test_render_escapes_and_no_lang_on_titles(self):
        x = item('<img src=x onerror=alert(1)> "ransomware"', "thn", 4)
        html = bn.render_clusters(bn.cluster([x]), 10, "vide", "empty")
        self.assertNotIn("<img", html)
        self.assertIn("&lt;img", html)
        self.assertNotIn('<span class="news-title" lang', html)

    def test_kev(self):
        kev = {"vulnerabilities": [
            {"cveID": "CVE-2026-0001", "vendorProject": "Acme", "product": "Gate", "vulnerabilityName": "Acme <b>RCE</b>",
             "dateAdded": "2026-11-03", "knownRansomwareCampaignUse": "Known"},
            {"cveID": "CVE-2025-0002", "vendorProject": "Old", "product": "X", "vulnerabilityName": "old",
             "dateAdded": "2025-01-03", "knownRansomwareCampaignUse": "Unknown"},
            {"cveID": "pas-un-cve", "vendorProject": "Evil", "product": "X", "vulnerabilityName": "x", "dateAdded": "2026-11-04"},
        ]}
        html = bn.render_kev(kev, NOW)
        self.assertIn("CVE-2026-0001", html)
        self.assertNotIn("CVE-2025-0002", html)
        self.assertNotIn("pas-un-cve", html)
        self.assertIn("&lt;b&gt;RCE", html)
        self.assertIn("news-badge--ransom", html)

    def test_offline_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "about").mkdir()
            shutil.copy(ROOT / "about" / "index.html", tmp / "about" / "index.html")
            self.assertEqual(bn.main(["--root", str(tmp), "--offline"]), 0)
            page = (tmp / "news" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Content-Security-Policy", page, "gabarit du site avec sa CSP")
            self.assertIn('<link rel="canonical" href="https://manthole.github.io/news/" />', page)
            self.assertNotIn("style=", page)
            archive = json.loads((tmp / "data" / "news-archive.json").read_text())
            self.assertEqual(archive["items"], [])


class Fiches(unittest.TestCase):
    def test_playbooks_complete_and_techniques_real(self):
        techs = bn.fx.ref()["techniques"]
        for kind in bn.fx.KINDS:
            pb = bn.fx.PLAYBOOKS[kind]
            self.assertTrue(all(pb["label"]) and all(pb["phrase"]) and all(pb["def"]), kind)
            self.assertGreaterEqual(len(pb["phases"]), 4, kind)
            self.assertEqual(len(pb["protect"]), 3, kind)
            for tfr, ten, xfr, xen, ids in pb["phases"]:
                self.assertTrue(tfr and ten and xfr and xen, kind)
                for t in ids:
                    self.assertIn(t, techs, f"{kind} : {t} absent du référentiel MITRE ATT&CK")

    def test_kind_detection(self):
        cases = {
            "Synology NAS Devices Targeted in Ransomware Attacks Exploiting Patched DSM Flaw": "ransomware",
            "Russian state-linked hackers target iPhone, Android devices in zero-click espionage campaign": "espionage",
            "Cyberattaque contre les frigos de l'EFS : le plasma visé": "ot",
            "NIKKE PC game launcher hacked to spread remote access, data-stealing malware": "supply_chain",
            "Pro-Russian hacktivists claim DDoS attacks on French city websites": "ddos",
            "Microsoft 365 phishing kit bypasses MFA with adversary-in-the-middle proxy": "phishing",
            "DigiCert data breach exposes customer information, identity documents": "breach",
            "Zyxel fixes zero-day exploited to hack nearly 1,000 network switches": "exploit",
            "Lazarus hackers steal $40 million from crypto exchange": "crypto",
            "Acme confirms incident": "intrusion",
            "Attackers Exploit Critical Siemens IoT2050 Flaw to Plant Remote Command Backdoors": "exploit",
        }
        for title, kind in cases.items():
            self.assertEqual(bn.fx.rank_kinds(bn.fx.kind_scores(title))[0], kind, title)
        # le résumé compte moins que le titre, mais apparaît en type secondaire
        self.assertEqual(bn.fx.rank_kinds(bn.fx.kind_scores("Acme patches flaw", "used by ransomware gangs")), ["exploit", "ransomware"])

    def test_actor_sets_kind(self):
        x = bn.normalise(item("Ciblage et compromission d'entités françaises au moyen du mode opératoire d'attaque Turla", "certfr-cti", 4))
        self.assertEqual(bn.cluster([x])[0]["kinds"][0], "espionage")
        y = bn.normalise(item("Hôpital régional : Qilin revendique l'attaque", "zataz", 4))
        self.assertEqual(bn.cluster([y])[0]["kinds"][0], "ransomware")

    def test_actors(self):
        found = lambda t: [a["name"] for _, a in bn.fx.find_actors([t])]
        self.assertIn("APT29", found("APT29-Linked Hackers Hijack Web Analytics Script"))
        self.assertIn("Turla", found("Ciblage d'entités françaises par Turla"))
        self.assertEqual(found("Google removes apps from Play Store after Snake game scam"), [], "mots courants ignorés")
        self.assertEqual(found("turla in lowercase is not a match"), [])

    def _fiche(self, title, kev=None):
        x = item(title, "thn", 4, zero=True)
        x["cves"] = ["CVE-2026-0001"]
        x["actors"] = ["G0016"]
        c = bn.cluster([bn.normalise(x)])[0]
        return bn.render_fiche("f-" + x["id"], c, bn.kev_index(kev))

    def test_render_fiche(self):
        kev = {"vulnerabilities": [{"cveID": "CVE-2026-0001", "vendorProject": "Acme<script>", "product": "Gate",
                                    "vulnerabilityName": "x", "dateAdded": "2026-11-03", "knownRansomwareCampaignUse": "Known",
                                    "shortDescription": "<img src=x onerror=alert(1)>", "requiredAction": "patch", "dueDate": "2026-11-24"}]}
        html = self._fiche('<img src=x onerror=alert(1)> Ransomware hits "Acme"', kev)
        self.assertNotIn("<img", html)
        self.assertNotIn("<script", html)
        self.assertNotIn("style=", html)
        self.assertIn('class="fiche fiche--ransomware"', html)
        self.assertEqual(html.count('class="chain__step"'), 6)
        self.assertIn("attack.mitre.org/techniques/T1486", html)
        self.assertIn("APT29", html, "groupe retrouvé par son identifiant")
        self.assertIn("y compris par des rançongiciels", html)
        self.assertNotIn('<h3 class="fiche__title" id="f-', html.split("lang=")[0] + "x", "titre sans attribut lang")
        kev_html = bn.render_kev_fiche("k-cve-2026-0001", kev["vulnerabilities"][0], [])
        self.assertNotIn("<img", kev_html)
        self.assertIn("24/11/2026", kev_html)

    def test_names_skip_sentence_start(self):
        x = item("Hôpital régional : le rançongiciel Qilin revendique l'attaque", "zataz", 4)
        c = bn.cluster([bn.normalise(x)])[0]
        html = bn.render_fiche("f-x", c, {})
        self.assertNotIn("Hôpital", html.split("Noms cités")[-1].split("</dd>")[0] if "Noms cités" in html else "")
        self.assertIn("Qilin", html)

    def test_normalise_cleans_archive(self):
        x = item("Acme ransomware", "thn", 4)
        x.update({"kinds": {"evil": 9}, "cves": ["<b>"], "actors": ["<script>"]})
        y = bn.normalise(x)
        self.assertEqual(y["kinds"], {"ransomware": 3})
        self.assertEqual(y["cves"], [])
        self.assertEqual(y["actors"], [])

    def test_page_with_fiches(self):
        now = NOW
        items = [bn.normalise(item("Zyxel fixes zero-day exploited to hack switches", "bleeping", 4, zero=True))]
        fiches = {}
        body = bn.build_body(items, None, [], {}, now, fiches)
        self.assertEqual(len(fiches), 1)
        fid = next(iter(fiches))
        self.assertIn(f'href="#{fid}"', body)
        page = bn.retarget((ROOT / "about" / "index.html").read_text(encoding="utf-8"), body, bn.render_fiches(fiches, None, items))
        self.assertIn(f'id="{fid}"', page)
        self.assertIn('<script src="/js/news.js" defer></script>', page)
        self.assertNotIn("style=", page)


if __name__ == "__main__":
    unittest.main()
