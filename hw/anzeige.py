"""Block 5: Anzeige, direkt gemultiplext (Entscheidung 004).

    MCU-Pin ──R 270 Ω──► Segmentleitung a … DP ──► Anode in allen 6 Ziffern
                                                   + LEDs der Stelle 7
    MCU-Pin ──► Gate Q (AO3400A), 100 kΩ nach GND
                       Drain ◄── gemeinsame Kathode der Stelle, Source → GND

Stelle 7 hat statt einer Ziffer 5 einzelne LEDs:
    Segment a, b → Doppelpunkt HH:MM (oben, unten)
    Segment c, d → Doppelpunkt MM:SS (oben, unten)
    Segment e    → Status-LED „letzte Synchronisation > 24 h“ (F5)
Die Firmware kann so jede LED einzeln schalten und dimmen.

Anzeige-Pins SC08-11SURKWA (Datenblatt DSAM8560 V.3A): a=1 b=14 c=12 d=10
e=4 f=2 g=13 DP=9, Kathode 3/5/11/16, Pin 6 ohne Chip.
"""

from skidl import Net, subcircuit

import bauteile as b

SEGMENTE = ["a", "b", "c", "d", "e", "f", "g", "DP"]
STELLEN = 7  # 6 Ziffern + Doppelpunkte/Status
LED_STELLE7 = ["a", "b", "c", "d", "e"]  # 4 Doppelpunkt-LEDs + Status-LED

# --- Rechnungen ------------------------------------------------------------
# Spitzenstrom einer leuchtenden LED während ihrer Stelle:
#   I = (VSYS − U_F − U_DS) / (R_SEG + R_PIN)
# U_F: Flussspannung bei wenigen mA, Datenblatt-Kennlinie ca. 1,8 V (typ.),
#      Höchstwert 2,35 V (bei 10 mA, also bei kleinem Strom eher weniger)
# R_PIN: Innenwiderstand des MCU-Ausgangs. Datenblatt ATmega328PB
#      (DS40001906A, S. 351): VOH ≥ 2,1 V bei 10 mA, VCC = 3 V, 85 °C
#      → ≤ 90 Ω im ungünstigsten Fall; typisch ca. 50 Ω
# U_DS: AO3400A, R_DS(on) < 50 mΩ bei 2,5 V Gate → < 5 mV, vernachlässigt
R_SEG = 270.0
R_PIN = 50.0
R_PIN_MAX = 90.0
U_F_TYP = 1.8
U_F_MAX = 2.35
TASTGRAD = 1 / STELLEN  # jede Stelle leuchtet 1/7 der Zeit


def i_spitze(vsys, u_f=U_F_TYP, r_pin=R_PIN):
    return (vsys - u_f) / (R_SEG + r_pin)


# Leerer Akku (3,0 V): Mittelstrom je Segment bei voller PWM muss das Ziel
# 0,2–0,4 mA (Architektur Abschnitt 5) erreichen
I_ZIEL = 0.3e-3
assert i_spitze(3.0) * TASTGRAD > I_ZIEL  # 3,75 mA · 1/7 = 0,54 mA
assert i_spitze(3.0, r_pin=R_PIN_MAX) * TASTGRAD > I_ZIEL  # 0,48 mA
# Ungünstigste LED und ungünstigster Pin bei leerem Akku erreichen das Ziel
# nur knapp (0,26 mA). Das prüft der Prototyp (Lesbarkeit, Phase 5).
assert i_spitze(3.0, U_F_MAX, R_PIN_MAX) * TASTGRAD > 0.25e-3

# Höchster Strom: externe 5 V (VSYS ≈ 4,75 V), MCU-Pin max. 20 mA
I_MAX = i_spitze(4.75, 1.7)
assert I_MAX < 20e-3  # 9,6 mA
# Stellentreiber führt bis zu 8 Segmente gleichzeitig
assert 8 * I_MAX < 0.2  # 77 mA ≪ 5,7 A (AO3400A); auch < 200 mA VCC-Pin der MCU
# Summenstrom (IOH) je Portgruppe, Datenblatt S. 352: höchstens 100 mA je
#   Gruppe 1: PC0–PC5, PD0–PD4, ADC7, RESET → Segmente e, f, g, DP (PC0–PC3)
#             und a (PD4) = 5 Segmente
#   Gruppe 2: PB0–PB5, PD5–PD7, ADC6, XTAL → Segmente b, c, d (PD5–PD7);
#             die Gates der Stellentreiber ziehen nur µA
assert 5 * I_MAX < 100e-3  # 48 mA
assert 3 * I_MAX < 100e-3  # 29 mA
# Verlustleistung Vorwiderstand (Spitze, ohne Tastgrad): 0805 = 125 mW
assert I_MAX**2 * R_SEG < 0.125  # 25 mW

# Gate-Pull-down 100 kΩ: hält die Stellen während Reset/Programmieren dunkel
# (MCU-Pins sind dann hochohmig). Strom bei High: 4,75 V / 100 kΩ = 48 µA,
# fließt nur während der jeweils aktiven Stelle (1/7 der Zeit).


@subcircuit
def anzeige(seg_mcu, stelle_gate, gnd):
    """seg_mcu: 8 Netze von der MCU (a–DP), stelle_gate: 7 Gate-Netze."""
    # Segmentleitungen nach den Vorwiderständen
    seg = []
    for name, net_mcu in zip(SEGMENTE, seg_mcu):
        s = Net(f"SEG_{name.upper()}")
        r = b.R(f"r_seg_{name.lower()}", "270")
        net_mcu & r & s
        seg.append(s)
    seg_by_name = dict(zip(SEGMENTE, seg))

    # Stellentreiber
    kathode = []
    for i, gate in enumerate(stelle_gate, start=1):
        k = Net(f"KATHODE_{i}")
        q = b.nmos_ao3400a(f"q_stelle_{i}")
        q["G"] += gate
        q["D"] += k
        q["S"] += gnd
        r = b.R(f"r_gate_stelle_{i}", "100k")
        gate & r & gnd
        kathode.append(k)

    # Ziffern 1–6
    for i in range(6):
        d = b.anzeige_sc08(f"ziffer_{i + 1}")
        for name in SEGMENTE:
            seg_by_name[name] += d[name]
        kathode[i] += d["K"]  # alle vier Kathodenpins 3, 5, 11, 16

    # Stelle 7: Doppelpunkte und Status-LED
    for name in LED_STELLE7:
        led = b.led_rot_3mm(f"led_{name}")
        led["A"] += seg_by_name[name]
        led["K"] += kathode[6]
