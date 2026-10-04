"""Funkuhr – Gesamtschaltung (Phase 3).

Aufruf über `make` in hw/. Erzeugt in build/:
    funkuhr.net        Netzliste für KiCad
    funkuhr.kicad_sch  KiCad-Schaltplan (automatisch gezeichnet)
und in ../docs/:
    schaltung-pinbelegung.md   Pin → Netz für alle ICs, Transistoren, Stecker
    stueckliste.md             Stückliste mit Bestellnummern
"""

import os
from collections import OrderedDict

from skidl import (
    Part,
    ERC,
    KICAD10,
    POWER,
    Net,
    generate_netlist,
    generate_schematic,
    lib_search_paths,
    set_default_tool,
)

# default_circuit und NC stellt SKiDL beim Import global bereit

set_default_tool(KICAD10)
HIER = os.path.dirname(os.path.abspath(__file__))
lib_search_paths[KICAD10].append(os.path.join(HIER, "lib"))

import anzeige  # noqa: E402
import bedienung  # noqa: E402
import dcf  # noqa: E402
import mcu  # noqa: E402
import rtc  # noqa: E402
import versorgung  # noqa: E402

BUILD = os.path.join(HIER, "build")
DOCS = os.path.join(HIER, "..", "docs")

# --- Netze -------------------------------------------------------------------
gnd = Net("GND")
vsys = Net("VSYS")
v5_ext = Net("V5_EXT")
v3v3_dcf = Net("3V3_DCF")
for n in (gnd, vsys):
    n.drive = POWER

seg_mcu = [Net(f"MCU_SEG_{s.upper()}") for s in anzeige.SEGMENTE]
stelle = [Net(f"STELLE_{i}") for i in range(1, anzeige.STELLEN + 1)]
taster = [Net(f"TASTER_{i}") for i in range(1, 4)]  # = MOSI, MISO, SCK
sig = {name: Net(name) for name in ("SDA", "SCL", "RTC_SQW", "DCF_OUT", "DCF_EN", "RESET", "RESERVE")}

# --- Blöcke ------------------------------------------------------------------
versorgung.versorgung(vsys, v5_ext, v3v3_dcf, gnd)
mcu.mcu(vsys, v5_ext, gnd, seg_mcu, stelle, taster, sig)
rtc.rtc(vsys, gnd, sig["SDA"], sig["SCL"], sig["RTC_SQW"])
dcf.dcf(v3v3_dcf, gnd, sig["DCF_OUT"], sig["DCF_EN"])
anzeige.anzeige(seg_mcu, stelle, gnd)
bedienung.taster(taster, gnd)
bedienung.testpunkte(OrderedDict([
    ("VSYS", vsys), ("3V3_DCF", v3v3_dcf), ("DCF_OUT", sig["DCF_OUT"]),
    ("RTC_SQW", sig["RTC_SQW"]), ("RESERVE", sig["RESERVE"]), ("GND", gnd),
]))

# --- Prüfen und Ausgeben ---------------------------------------------------------
os.makedirs(BUILD, exist_ok=True)
ERC()
generate_netlist(file_=os.path.join(BUILD, "funkuhr.net"))


def _bauteile():
    teile = [p for p in default_circuit.parts if p.footprint]
    return sorted(teile, key=lambda p: (p.ref_prefix, int("".join(c for c in p.ref if c.isdigit()) or 0)))


def _feld(p, name):
    return p.fields.get(name, "") or ""


def stueckliste():
    gruppen = OrderedDict()
    for p in _bauteile():
        key = (p.value, p.footprint, _feld(p, "MPN"), _feld(p, "LCSC"), _feld(p, "Bestückung"))
        gruppen.setdefault(key, []).append(p)
    z = ["# Stückliste Funkuhr Rev. A", "",
         "Automatisch erzeugt aus `hw/funkuhr.py` (`make` in `hw/`). Nicht von Hand ändern.", "",
         "| Anzahl | Referenzen | Wert | Footprint | Hersteller | MPN | LCSC | Bezug | Bestückung |",
         "|---|---|---|---|---|---|---|---|---|"]
    for (wert, fp, mpn, lcsc, best), ps in gruppen.items():
        p0 = ps[0]
        z.append(f"| {len(ps)} | {', '.join(p.ref for p in ps)} | {wert} | {fp.split(':')[-1]} | "
                 f"{_feld(p0, 'Hersteller')} | {mpn} | {lcsc} | {_feld(p0, 'Bezug') or ('LCSC' if lcsc else '')} | "
                 f"{best or 'immer'} |")
    z.append("")
    z.append(f"Bauteile gesamt: {len(_bauteile())}, Positionen: {len(gruppen)}")
    return "\n".join(z) + "\n"


def pinbelegung():
    z = ["# Pinbelegung Funkuhr Rev. A", "",
         "Automatisch erzeugt aus `hw/funkuhr.py` (`make` in `hw/`). Nicht von Hand ändern.", "",
         "Für jeden IC, Transistor und Stecker: welcher Pin hängt an welchem Netz.", ""]
    for p in _bauteile():
        if p.ref_prefix not in ("U", "Q", "J", "D", "DS"):
            continue
        if p.ref_prefix == "DS" and p.ref != _erste_anzeige():
            continue
        z.append(f"## {p.ref} – {p.value}")
        if p.value == "SC08-11SURKWA":
            z.append("")
            z.append("Stellvertretend für alle sechs Ziffern; die anderen unterscheiden sich nur im Kathodennetz "
                     "(KATHODE_1 … KATHODE_6).")
        z.append("")
        z.append("| Pin | Name | Netz |")
        z.append("|---|---|---|")
        for pin in sorted(p.pins, key=lambda x: (len(x.num), x.num)):
            net = pin.net.name if pin.is_connected() and pin.net is not None else "–"
            if pin.net is not None and pin.net.__class__.__name__ == "NCNet":
                net = "nicht angeschlossen"
            z.append(f"| {pin.num} | {pin.name} | {net} |")
        z.append("")
    return "\n".join(z)


def _erste_anzeige():
    return next(p.ref for p in _bauteile() if p.value == "SC08-11SURKWA")


with open(os.path.join(DOCS, "stueckliste.md"), "w", encoding="utf-8") as f:
    f.write(stueckliste())
with open(os.path.join(DOCS, "schaltung-pinbelegung.md"), "w", encoding="utf-8") as f:
    f.write(pinbelegung())

# --- Schaltplan ------------------------------------------------------------------
# PWR_FLAG kennzeichnet für die KiCad-ERC Netze, die von einer passiven Quelle
# gespeist werden (Akku über Q1, Knopfzelle) bzw. Masse. Die Flags kommen erst
# nach Netzliste und Dokumenten dazu: Sie haben keinen Footprint und gehören
# nur in den Schaltplan, nicht aufs Layout.
for net in (gnd, vsys, Net.get("V_BACKUP")):
    Part("power", "PWR_FLAG", tag=f"flag_{net.name.lower()}")[1] += net

# auto_stub: schwer zu zeichnende Netze werden zu Beschriftungen, GND/VSYS zu
# Versorgungssymbolen. Der Zeichner von SKiDL 2.3 scheitert gelegentlich mit
# einem internen Fehler (KeyError in route.py); dann mit anderem seed erneut.
# Der Schaltplan ist nur Ansicht – Netzliste und Dokumente stehen schon.
for seed in range(1, 6):
    try:
        generate_schematic(filepath=BUILD, top_name="funkuhr", title="Funkuhr Rev. A",
                           auto_stub=True, seed=seed)
        break
    except Exception as e:  # noqa: BLE001
        print(f"Schaltplan-Zeichnung mit seed={seed} gescheitert: {e!r}")
else:
    raise SystemExit("FEHLER: Schaltplan konnte nicht gezeichnet werden (Netzliste ist aktuell)")
