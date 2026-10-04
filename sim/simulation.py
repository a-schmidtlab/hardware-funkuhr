"""Analogsimulation der Funkuhr mit ngspice (Phase 4).

Aufruf: `make` in sim/ (oder `python3 simulation.py`). Schreibt
`ergebnisse.md` und bricht mit Fehler ab, wenn eine Anforderung verletzt ist.

Teile:
  0. Modellprüfung: Modelle gegen Datenblattpunkte
  1. Anzeige: Segmentströme über Akkuspannung und Toleranzen (ungünstige Ecken)
  2. Versorgung: Akku/5 V/Programmer, Verpolung → Akkustrom (nie laden!)
  3. Strombudget und Laufzeit (E3)

Die Schaltungswerte stammen aus hw/*.py; geändert werden sie nur dort.
"""

import itertools
import os
import re
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HIER, "build")
MODELLE = os.path.join(HIER, "modelle.lib")

# Werte aus der Schaltung (hw/anzeige.py, hw/versorgung.py)
R_SEG = 270.0
R_GATE_Q1 = 10e3
R_LECK_BAT54 = 2e6  # 2 µA Sperrstrom bei ca. 4 V (Datenblatt max. 2 µA @ 25 V)
R_INNEN_AKKU = 0.15  # Zelle ca. 50 mΩ + Halter/Schutzplatine ca. 100 mΩ
R_KABEL_5V = 0.2

zeilen = []  # Markdown-Ausgabe
fehler = []


def md(s=""):
    zeilen.append(s)


def pruefe(bedingung, text):
    if not bedingung:
        fehler.append(text)
    return "✓" if bedingung else "✗"


def ngspice(name, netz, messen):
    """Führt eine .op-Analyse aus und liefert die angefragten Größen als dict."""
    os.makedirs(BUILD, exist_ok=True)
    datei = os.path.join(BUILD, f"{name}.cir")
    druck = "\n".join(f"print {m}" for m in messen)
    with open(datei, "w") as f:
        f.write(f"* {name}\n.include {MODELLE}\n{netz}\n.control\nop\n{druck}\n.endc\n.end\n")
    aus = subprocess.run(["ngspice", "-b", datei], capture_output=True, text=True)
    werte = {}
    for m in messen:
        treffer = re.search(re.escape(m.lower()) + r"\s*=\s*([-+0-9.eE]+)", aus.stdout.lower())
        if not treffer:
            raise RuntimeError(f"{name}: {m} nicht gefunden\n{aus.stdout}\n{aus.stderr}")
        werte[m] = float(treffer.group(1))
    return werte


# ---------------------------------------------------------------------------
# 0. Modellprüfung
# ---------------------------------------------------------------------------
def modellpruefung():
    md("## 0. Modellprüfung gegen Datenblatt")
    md()
    md("Jedes Modell wird mit einer Stromquelle bzw. Gatespannung betrieben und mit den Datenblattpunkten verglichen. "
       "Bei Höchstwerten darf das Modell bis 0,05 V darüber liegen (pessimistisch), aber höchstens 0,02 V darunter. "
       "R_DS(on): ±15 % um den Höchstwert; das entspricht bei 80 mA weniger als 2 mV.")
    md()
    md("| Bauteil | Bedingung | Datenblatt | Modell | |")
    md("|---|---|---|---|---|")
    punkte = [
        ("LED typ.", "LED_TYP", 10e-3, 1.85),
        ("LED max.", "LED_MAX", 10e-3, 2.35),
        ("BAT54 max.", "BAT54", 0.1e-3, 0.24),
        ("BAT54 max.", "BAT54", 1e-3, 0.32),
        ("BAT54 max.", "BAT54", 10e-3, 0.40),
        ("BAT54 max.", "BAT54", 30e-3, 0.50),
        ("BAT54 max.", "BAT54", 100e-3, 0.80),
    ]
    for name, model, i, u_db in punkte:
        w = ngspice("modell_diode", f"I1 0 a DC {i}\nD1 a 0 {model}", ["v(a)"])
        u = w["v(a)"]
        ok = pruefe(-0.02 <= u - u_db <= 0.05, f"Modell {name} bei {i*1e3:g} mA: {u:.3f} V statt {u_db} V")
        md(f"| {name} | U_F bei {i*1e3:g} mA | {u_db:.2f} V | {u:.3f} V | {ok} |")
    # R_DS(on): 100 mA Drainstrom, Gate gegen Source
    for name, model, kanal, ugs, r_db in [
        ("AO3400A", "AO3400A_TYP", "n", 2.5, 0.048), ("AO3400A", "AO3400A_TYP", "n", 4.5, 0.032),
        ("AO3401A", "AO3401A_TYP", "p", 2.5, 0.085), ("AO3401A", "AO3401A_TYP", "p", 4.5, 0.060),
    ]:
        if kanal == "n":
            netz = f"VG g 0 DC {ugs}\nID 0 d DC 0.1\nM1 d g 0 0 {model}"
            u = ngspice("modell_mos", netz, ["v(d)"])["v(d)"]
        else:
            netz = f"VS s 0 DC 5\nVG g 0 DC {5 - ugs}\nID d 0 DC 0.1\nM1 d g s s {model}"
            u = 5 - ngspice("modell_mos", netz, ["v(d)"])["v(d)"]
        r = u / 0.1
        ok = pruefe(abs(r - r_db) <= 0.15 * r_db, f"Modell {name} R_DS(on) bei {ugs} V: {r*1e3:.1f} mΩ")
        md(f"| {name} | R_DS(on) bei \\|U_GS\\| = {ugs} V | ≤ {r_db*1e3:.0f} mΩ | {r*1e3:.1f} mΩ | {ok} |")
    md()


# ---------------------------------------------------------------------------
# 1. Anzeige
# ---------------------------------------------------------------------------
def anzeige_netz(vsys, n_an, led, r_pin, r_seg, mos):
    """Eine aktive Stelle: n_an Segmente leuchten, Gate = VSYS (MCU-High ohne Last)."""
    z = [f"VS vsys 0 DC {vsys}", f"M1 k vsys 0 0 {mos}", "DB1 0 k DBODY"]
    for i in range(n_an):
        z += [f"RP{i} vsys m{i} {r_pin}", f"RS{i} m{i} s{i} {r_seg}", f"D{i} s{i} k {led}"]
    return "\n".join(z)


def anzeige():
    md("## 1. Anzeige: Segmentströme")
    md()
    md("Eine aktive Stelle, Gate des Stellentreibers auf VSYS. Ecken: LED typ./max. Flussspannung, "
       "MCU-Pin 50/90 Ω (Datenblatt), Vorwiderstand 270 Ω ± 1 %, AO3400A mit V_GS(th) 0,65/1,45 V, "
       "1 bzw. 8 leuchtende Segmente.")
    md()
    md("| VSYS | Spitzenstrom je Segment min … max | Mittelwert bei 1/7 (volle Helligkeit) min | Stelle max (8 Segmente) |")
    md("|---|---|---|---|")
    ecken = list(itertools.product(["LED_TYP", "LED_MAX"], [50.0, 90.0], [R_SEG * 0.99, R_SEG * 1.01],
                                   ["AO3400A_MIN", "AO3400A_MAX"], [1, 8]))
    ergebnis = {}
    for vsys in (3.0, 3.7, 4.2, 4.75):
        i_seg = []
        i_stelle = []
        for led, r_pin, r_seg, mos, n_an in ecken:
            messen = [f"i(vs)"] + ["v(k)"]
            w = ngspice("anzeige", anzeige_netz(vsys, n_an, led, r_pin, r_seg, mos), messen)
            i_ges = -w["i(vs)"]
            i_seg.append(i_ges / n_an)
            i_stelle.append(i_ges)
        ergebnis[vsys] = (min(i_seg), max(i_seg), max(i_stelle))
        md(f"| {vsys:.2f} V | {min(i_seg)*1e3:.2f} … {max(i_seg)*1e3:.2f} mA | "
           f"{min(i_seg)/7*1e3:.2f} mA | {max(i_stelle)*1e3:.1f} mA |")
    md()
    i_min_30 = ergebnis[3.0][0]
    i_max = max(v[1] for v in ergebnis.values())
    i_stelle_max = max(v[2] for v in ergebnis.values())
    md("Bewertung:")
    md()
    md(f"- Ziel 0,3 mA mittlerer Segmentstrom bei leerem Akku (3,0 V), ungünstigste Ecke: "
       f"{i_min_30/7*1e3:.2f} mA {pruefe(i_min_30 / 7 >= 0.25e-3, 'Helligkeit bei 3,0 V zu gering')} "
       f"(Untergrenze 0,25 mA, siehe offener Punkt 4 in schaltung.md)")
    md(f"- Höchster Pinstrom {i_max*1e3:.1f} mA ≤ 20 mA (Prüfbedingung Datenblatt) "
       f"{pruefe(i_max <= 20e-3, 'Pinstrom > 20 mA')}")
    md(f"- Summenstrom Portgruppe 1 (5 Segmente) {5*i_max*1e3:.0f} mA ≤ 100 mA "
       f"{pruefe(5 * i_max <= 100e-3, 'Portgruppe > 100 mA')}")
    md(f"- Stellentreiber höchstens {i_stelle_max*1e3:.0f} mA (AO3400A: 5,7 A) "
       f"{pruefe(i_stelle_max < 0.2, 'Stellenstrom zu hoch')}")
    md(f"- Verlustleistung Vorwiderstand (Spitze) {i_max**2*R_SEG*1e3:.0f} mW ≤ 125 mW "
       f"{pruefe(i_max**2 * R_SEG <= 0.125, 'Vorwiderstand überlastet')}")
    md()
    return ergebnis


# ---------------------------------------------------------------------------
# 2. Versorgung
# ---------------------------------------------------------------------------
def versorgung_netz(u_akku, u_ext, i_last, q1):
    z = []
    if u_akku is not None:
        z += [f"VAKKU akku_i 0 DC {u_akku}", f"RAKKU akku_i vbat_raw {R_INNEN_AKKU}"]
    else:
        z += ["RAKKU_OFFEN vbat_raw 0 1e9"]
    z += [f"M1 vbat_raw v5_ext vsys vsys {q1}", "DQ1 vbat_raw vsys DBODY",
          f"RG v5_ext 0 {R_GATE_Q1}",
          "D1 v5_ext vsys BAT54", f"RLECK vsys v5_ext {R_LECK_BAT54}",
          f"ILAST vsys 0 DC {i_last}"]
    if u_ext is not None:
        z += [f"VEXT ext_i 0 DC {u_ext}", f"REXT ext_i v5_ext {R_KABEL_5V}"]
    return "\n".join(z)


def versorgung():
    md("## 2. Versorgung: Akku, externe 5 V, Programmer, Verpolung")
    md()
    md("Akkustrom positiv = Akku wird entladen, negativ = Akku wird geladen. Laden darf nie vorkommen (E2). "
       f"Last = Gesamtstrom der Uhr an VSYS. Akku-Innenwiderstand {R_INNEN_AKKU*1e3:.0f} mΩ, "
       f"BAT54 mit Datenblatt-Höchstwerten und 2 µA Sperrstrom, Q1 mit V_GS(th) = −1,3 V (ungünstig).")
    md()
    md("| Fall | Akku | extern | Last | VSYS | U_GS Q1 | Akkustrom | Strom extern | |")
    md("|---|---|---|---|---|---|---|---|---|")
    faelle = []
    for u_akku in (3.0, 3.7, 4.2):
        for i_last in (1e-3, 15e-3, 80e-3):
            faelle.append(("Akku", u_akku, None, i_last))
    for u_akku in (None, 3.0, 4.2):
        for i_last in (1e-3, 15e-3, 80e-3):
            faelle.append(("USB 4,75 V", u_akku, 4.75, i_last))
    for u_akku in (3.0, 4.2):
        faelle.append(("Programmer 5,25 V", u_akku, 5.25, 15e-3))
        faelle.append(("Programmer 3,3 V", u_akku, 3.3, 15e-3))
    for u_ext in (None, 4.75):
        faelle.append(("Akku verpolt", -4.2, u_ext, 1e-3 if u_ext else 0.0))

    for fall, u_akku, u_ext, i_last in faelle:
        messen = ["v(vsys)", "v(v5_ext)"]
        if u_akku is not None:
            messen.append("i(vakku)")
        if u_ext is not None:
            messen.append("i(vext)")
        w = ngspice("versorgung", versorgung_netz(u_akku, u_ext, i_last, "AO3401A_MAX"), messen)
        vsys = w["v(vsys)"]
        ugs = w["v(v5_ext)"] - vsys
        i_akku = -w.get("i(vakku)", 0.0)
        i_ext = -w.get("i(vext)", 0.0)
        bewertung = []
        if u_akku is not None and u_akku > 0:
            bewertung.append(pruefe(i_akku > -1e-6, f"{fall}, Akku {u_akku} V: Ladestrom {i_akku*1e6:.1f} µA"))
        if u_akku is not None and u_akku < 0:
            bewertung.append(pruefe(abs(i_akku) < 10e-6, f"{fall}: Strom {i_akku*1e6:.1f} µA aus verpoltem Akku"))
        if fall == "Akku":
            bewertung.append(pruefe(ugs <= -2.5, f"Akku {u_akku} V: U_GS nur {ugs:.2f} V"))
            bewertung.append(pruefe(u_akku - vsys < 0.05, f"Akku {u_akku} V, {i_last*1e3:g} mA: Verlust {u_akku - vsys:.3f} V"))
        if i_last > 0:
            bewertung.append(pruefe(vsys >= 2.7 if fall != "Programmer 3,3 V" else vsys >= 2.4,
                                    f"{fall}: VSYS nur {vsys:.2f} V"))
        akku = "–" if u_akku is None else f"{u_akku:+.1f} V".replace("+", "")
        ext = "–" if u_ext is None else f"{u_ext:.2f} V"
        md(f"| {fall} | {akku} | {ext} | {i_last*1e3:g} mA | {vsys:.3f} V | {ugs:+.2f} V | "
           f"{i_akku*1e3:+.4f} mA | {i_ext*1e3:+.2f} mA | {' '.join(bewertung) or '–'} |")
    md()
    md("Hinweise zur Tabelle:")
    md()
    md("- Bei externer Versorgung und hoher Last kann VSYS unter die Akkuspannung fallen. Dann liefert der Akku "
       "über die Body-Diode bzw. den teilweise leitenden Q1 mit (positiver Akkustrom). Das ist Entladen, kein Laden.")
    md("- „Programmer 3,3 V“: Q1 sperrt nicht vollständig; die Uhr läuft dann überwiegend aus dem Akku. Auch hier wird nicht geladen.")
    md()


# ---------------------------------------------------------------------------
# 2b. Störungen auf VSYS durch das Multiplexen (Eingangsfilter DCF)
# ---------------------------------------------------------------------------
def welligkeit():
    md("## 2b. Störungen auf VSYS durch das Multiplexen")
    md()
    md("Ungünstigster Fall: Die Stellen wechseln mit 1 kHz zwischen voller Last (Ziffer „8“ mit Punkt, 73 mA) "
       "und keiner Last. Akku 3,7 V mit 150 mΩ Innenwiderstand, Q1 ca. 60 mΩ, an VSYS 22 µF + 10 µF + 2 × 100 nF "
       "(Keramik, je 5 mΩ ESR, 1 nH). Flanken 1 µs.")
    md()
    os.makedirs(BUILD, exist_ok=True)
    datei = os.path.join(BUILD, "welligkeit.cir")
    netz = """* welligkeit
VAKKU a 0 DC 3.7
RAKKU a b 0.15
RQ1 b vsys 0.06
C1 vsys c1 22u
R1 c1 c1l 5m
L1 c1l 0 1n
C2 vsys c2 10u
R2 c2 c2l 5m
L2 c2l 0 1n
C3 vsys 0 100n
C4 vsys 0 100n
ILAST vsys 0 PULSE(0 73m 0 1u 1u 499u 1m)
.tran 0.2u 12m 2m 0.2u
.control
run
let span = vecmax(v(vsys)) - vecmin(v(vsys))
print span
linearize v(vsys)
fft v(vsys)
let mag = mag(v(vsys))
meas sp m1k find mag at=1k
meas sp m77k find mag at=77k
meas sp m775k find mag at=77.5k
meas sp m78k find mag at=78k
print m1k m77k m775k m78k
.endc
.end
"""
    with open(datei, "w") as f:
        f.write(netz)
    aus = subprocess.run(["ngspice", "-b", datei], capture_output=True, text=True).stdout.lower()
    def wert(name):
        m = re.search(re.escape(name) + r"\s*=\s*([-+0-9.e]+)", aus)
        if not m:
            raise RuntimeError(f"welligkeit: {name} fehlt\n{aus}")
        return float(m.group(1))
    span, m1k, m77k, m775k, m78k = (wert(n) for n in ("span", "m1k", "m77k", "m775k", "m78k"))
    psrr_1k = 10 ** (-40 / 20)  # XC6206: 40 dB bei 1 kHz (Datenblatt, typ.)
    md("| Größe | Wert |")
    md("|---|---|")
    md(f"| Spitze-Spitze-Welligkeit VSYS | {span*1e3:.1f} mV |")
    md(f"| Anteil bei 1 kHz (Grundwelle) | {m1k*1e3:.2f} mV |")
    md(f"| Anteil bei 77,0 kHz | {m77k*1e6:.1f} µV |")
    md(f"| Anteil bei 77,5 kHz (DCF77) | {m775k*1e6:.2f} µV |")
    md(f"| Anteil bei 78,0 kHz | {m78k*1e6:.1f} µV |")
    md(f"| 1-kHz-Anteil hinter dem LDO (40 dB) | {m1k*psrr_1k*1e6:.0f} µV |")
    md()
    md("Bewertung:")
    md()
    md(f"- Die Oberwellen liegen wie geplant bei 77,0 und 78,0 kHz, also 500 Hz neben DCF77. Bei 77,5 kHz selbst "
       f"ist der Anteil um den Faktor {m77k/max(m775k,1e-12):.0f} kleiner {pruefe(m775k < m77k / 10, 'Störung direkt bei 77,5 kHz')}")
    md(f"- Welligkeit auf VSYS {span*1e3:.0f} mV ≤ 50 mV {pruefe(span <= 50e-3, 'VSYS-Welligkeit zu groß')}")
    md("- Die PSRR des XC6206 bei 77 kHz nennt das Datenblatt nicht; sie ist dort deutlich kleiner als 40 dB. "
       "Auch der Empfang über die Antenne (Magnetfeld der Anzeigeströme) lässt sich nicht simulieren. "
       "Beides prüft der Prototyp (Phase 5).")
    md()


# ---------------------------------------------------------------------------
# 3. Strombudget und Laufzeit
# ---------------------------------------------------------------------------
def strombudget(anzeige_erg):
    md("## 3. Strombudget und Laufzeit (E3)")
    md()
    md("Die Helligkeit stellt die Firmware per PWM ein; der mittlere Segmentstrom ist also eine Vorgabe, "
       "keine Folge der Akkuspannung. Abschnitt 1 zeigt, dass die Vorgaben bis 3,0 V erreichbar sind.")
    md()
    # Leuchtende LEDs: Ziffern 0–9 haben im Mittel 4,9 Segmente; 6 Ziffern + 4 Doppelpunkte
    n_led = 6 * 4.9 + 4
    md(f"Leuchtende LEDs im Mittel: 6 Ziffern × 4,9 Segmente + 4 Doppelpunkt-LEDs = {n_led:.1f}")
    md()
    md("| Verbraucher | günstig | ungünstig | Quelle |")
    md("|---|---|---|---|")
    posten = [
        ("Anzeige (0,2 / 0,4 mA je LED)", n_led * 0.2e-3, n_led * 0.4e-3, "Vorgabe Firmware (Architektur Abschn. 5)"),
        ("ATmega328PB, 1 MHz, ca. halb aktiv/halb Idle", 0.25e-3, 0.9e-3,
         "Datenblatt S. 352: aktiv 0,2/0,5 mA, Idle 0,06/0,15 mA bei 2 V, ×1,85 für 3,7 V"),
        ("DS3231", 0.11e-3, 0.2e-3, "Datenblatt: I_CCS 110 µA, I_CCA 200 µA"),
        ("DCF77-Modul", 0.06e-3, 0.12e-3, "MAS6180C/Modul, Pollin DCF1 als Vergleich: < 90 µA typ., 120 µA max."),
        ("Gate-Pull-downs der Stellen (1/7 · 47 µA)", 7e-6, 7e-6, "4,7 V / 100 kΩ, je Stelle 1/7 der Zeit"),
        ("LDO, Pull-ups in Ruhe, Leckströme", 0.01e-3, 0.02e-3, "XC6206 Ruhestrom ca. 1 µA u. a."),
    ]
    summe_g = sum(p[1] for p in posten)
    summe_u = sum(p[2] for p in posten)
    for name, g, u, q in posten:
        md(f"| {name} | {g*1e3:.2f} mA | {u*1e3:.2f} mA | {q} |")
    md(f"| **Summe** | **{summe_g*1e3:.1f} mA** | **{summe_u*1e3:.1f} mA** | |")
    md()
    tage = []
    for kap_mah, i, text in ((3000, summe_g, "günstig: 3000 mAh, niedrige Helligkeit"),
                             (2500, summe_u, "ungünstig: 2500 mAh, hohe Helligkeit")):
        t = kap_mah / (i * 1e3) / 24
        tage.append(t)
        md(f"- {text}: {kap_mah} mAh / {i*1e3:.1f} mA = **{t:.1f} Tage**")
    md()
    md(f"Anforderung E3: ca. 1–4 Wochen. Ergebnis: {tage[1]:.0f} bis {tage[0]:.0f} Tage "
       f"{pruefe(tage[1] >= 7, 'Laufzeit unter einer Woche')}")
    md()
    md("Nicht enthalten: Nachtabsenkung per Uhrzeit (Firmware-Option). Bei halber Helligkeit von 22 bis 7 Uhr "
       "sinkt der Anzeigeanteil um ca. 19 %.")
    md()


def main():
    md("# Simulationsergebnisse Funkuhr Rev. A")
    md()
    md("Automatisch erzeugt mit `make` in `sim/` (ngspice 42, Modelle in `sim/modelle.lib`). Nicht von Hand ändern.")
    md()
    modellpruefung()
    erg = anzeige()
    versorgung()
    welligkeit()
    strombudget(erg)
    md("## Gesamtergebnis")
    md()
    if fehler:
        md("**Nicht bestanden:**")
        md()
        for f in fehler:
            md(f"- {f}")
    else:
        md("Alle Prüfungen bestanden.")
    with open(os.path.join(HIER, "ergebnisse.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen) + "\n")
    print("\n".join(zeilen))
    if fehler:
        print(f"\n{len(fehler)} Prüfung(en) nicht bestanden", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
