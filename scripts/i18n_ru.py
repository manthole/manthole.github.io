"""Traductions russes partagées par les générateurs de pages (clé = texte français, tel qu'il apparaît dans la page).
Un texte absent du dictionnaire scripts/i18n_ru.json est affiché en anglais et signalé une fois."""
import json
import sys
from pathlib import Path

_RU = json.loads((Path(__file__).resolve().parent / "i18n_ru.json").read_text(encoding="utf-8"))
_MISSING = set()


def ru(fr, en):
    t = _RU.get(fr)
    if t is None:
        if fr not in _MISSING:
            _MISSING.add(fr)
            print(f"[ru] traduction manquante, anglais utilisé : {fr[:80]!r}", file=sys.stderr)
        return en
    return t
