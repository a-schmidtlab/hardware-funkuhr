"""Block 4: Anschluss DCF77-Modul CANADUINO V4 (Entscheidung 003).

Das Modul sitzt auf eigener Platine mit Ferritantenne und wird über kurze
Drähte an J DCF angeschlossen. Belegung von J DCF (unsere Festlegung):
    1 VCC (3V3_DCF)   2 GND   3 OUT   4 EN

Modulpins laut Datenblatt (Rev B, 2025-02-26):
- VCC 2–5,5 V, „muss sauber und stabil sein“ → eigener LDO + 10 µF + 100 nF
- OUT: Push-Pull, Pegel = VCC (3,3 V), max. ±20 mA
- EN: offen = an, GND = Stromsparmodus → von der MCU nur auf GND ziehen
  oder hochohmig schalten, nie aktiv auf High (VSYS > 3,3 V)
- AON offen (AGC an), LED offen (Status-LEDs aus) → nicht verdrahtet
"""

from skidl import Net, subcircuit

import bauteile as b

# EN-Serienwiderstand 1 kΩ: begrenzt den Strom, falls die Firmware EN doch
# aktiv auf High treibt (VSYS 4,75 V gegen 3,3 V am Modul):
R_EN = 1e3
assert (4.75 - 3.3) / R_EN < 2e-3  # < 1,5 mA, ungefährlich
# Low-Pegel am Modul, wenn die MCU EN auf GND zieht: Spannungsteiler aus
# R_EN und dem modulinternen Pull-up (Wert unbekannt, angenommen ≥ 10 kΩ)
assert 3.3 * R_EN / (R_EN + 10e3) < 0.4  # 0,3 V → sicher Low

# Pegel DCF_OUT → MCU (Architektur Abschnitt 3): High = 3,3 V, MCU-Schwelle
# 0,6 · VCC, ungünstigster Fall bei externer Versorgung VSYS ≈ 4,75 V
assert 3.3 > 0.6 * 4.75  # 3,3 V > 2,85 V

# Serienwiderstand im Signalweg: dämpft Flanken (Störungen Richtung Antenne)
R_OUT = 1e3


@subcircuit
def dcf(v3v3_dcf, gnd, dcf_out, dcf_en):
    j = b.stiftleiste("j_dcf", 1, 4, "DCF77-Modul")
    j[1] += v3v3_dcf
    j[2] += gnd
    r_out = b.R("r_dcf_out", "1k")
    Net("MODUL_OUT").connect(j[3], r_out[1])
    r_out[2] += dcf_out
    r_en = b.R("r_dcf_en", "1k")
    Net("MODUL_EN").connect(j[4], r_en[1])
    r_en[2] += dcf_en

    c1 = b.C("c_dcf_puffer", "10u")
    v3v3_dcf & c1 & gnd
    c2 = b.C("c_dcf", "100n")
    v3v3_dcf & c2 & gnd
