"""Block 1: Versorgung (Entscheidungen 005 und 006).

    18650 ──► Q1 (AO3401A) ──┬──────────────► VSYS (3,0–4,7 V)
                  ▲ Gate     │
    USB-C, ISP, UART ──► V5_EXT ──► D1 (BAT54) ─┘
                  └── R1 10k ──► GND

    VSYS ──► U1 (XC6206, 3,3 V) ──► 3V3_DCF (nur DCF-Modul)

Q1 ist Verpolschutz und Akkutrennung zugleich:
- ohne 5 V liegt das Gate über R1 auf GND → Q1 leitet, der Akku versorgt VSYS
- mit 5 V liegt das Gate auf 5 V → Q1 sperrt, der Akku ist abgetrennt
- Akku verpolt: Gate und Source auf ca. 0 V, Body-Diode sperrt → kein Strom
"""

from skidl import Net, subcircuit  # NC (= nicht angeschlossen) stellt SKiDL global bereit

import bauteile as b

# --- Rechnungen ------------------------------------------------------------

# Sperrstrom der BAT54 (Datenblatt: max. 2 µA bei 25 V, 25 °C) fließt im
# Akkubetrieb von VSYS rückwärts auf V5_EXT und über R1 nach GND.
# Er hebt das Gate von Q1 an. Das Gate muss nahe 0 V bleiben, damit Q1
# auch bei leerem Akku (3,0 V) voll durchschaltet (Vgs ≤ −2,5 V).
I_SPERR_BAT54_MAX = 2e-6  # A
R_GATE = 10e3  # Ω
U_GATE_MAX = I_SPERR_BAT54_MAX * R_GATE
assert U_GATE_MAX < 0.1, U_GATE_MAX  # 20 mV → Vgs bei 3,0 V Akku: −2,98 V

# Mit externen 5 V fließt durch R1 ein Querstrom aus der USB-Quelle
I_R_GATE_5V = 5.0 / R_GATE
assert I_R_GATE_5V < 1e-3  # 0,5 mA, unkritisch für jede USB-Quelle

# LDO XC6206: max. 6 V Eingang; VSYS liegt höchstens bei ca. 4,75 V
U_VSYS_MAX = 4.75
assert U_VSYS_MAX < 6.0

# USB-C: 5,1 kΩ an CC1/CC2 nach GND kennzeichnen ein „Sink“-Gerät.
# Das Netzteil liefert dann 5 V (USB-C-Spezifikation, Rd = 5,1 kΩ ±20 %).


@subcircuit
def versorgung(vsys, v5_ext, v3v3_dcf, gnd):
    # Akku und Verpolschutz/Akkutrennung
    bt = b.halter_18650("akku")
    q = b.pmos_ao3401a("q_akku")
    vbat_raw = Net("VBAT_RAW")
    vbat_raw += bt["+"], q["D"]
    bt["-"] += gnd
    q["S"] += vsys
    q["G"] += v5_ext
    r_gate = b.R("r_gate_akku", "10k")
    v5_ext & r_gate & gnd

    # Pufferkondensator für die Stromspitzen der Anzeige
    c_vsys = b.C("c_vsys", "22u")
    vsys & c_vsys & gnd

    # Optionale externe 5 V über USB-C (nur bei Bedarf bestückt, E6)
    opt = "optional (E6)"
    usb = b.usb_c_nur_strom("usb_c", bestueckung=opt)
    usb["VBUS"] += v5_ext
    usb["GND"] += gnd
    usb["SHIELD"] += gnd
    for cc in ("CC1", "CC2"):
        r_cc = b.R(f"r_{cc.lower()}", "5k1", bestueckung=opt)
        net_cc = Net(f"USB_{cc}")
        net_cc += usb[cc], r_cc[1]
        r_cc[2] += gnd

    # D1 und C immer bestücken: Auch ISP- und UART-Stecker speisen über
    # V5_EXT ein (siehe mcu.py). Ohne D1 würde ein Programmer den Akku
    # abtrennen (Gate auf 5 V), ohne selbst VSYS zu versorgen.
    d = b.schottky_bat54("d_5v")
    d["A"] += v5_ext
    d["K"] += vsys
    d["NC"] += NC  # Pin 2 ist im Gehäuse nicht belegt
    c_5v = b.C("c_5v", "10u")
    v5_ext & c_5v & gnd

    # 3,3 V nur für den DCF-Empfänger (Entkopplung von der Anzeige)
    ldo = b.ldo_xc6206_33("ldo_dcf")
    ldo["VI"] += vsys
    ldo["VO"] += v3v3_dcf
    ldo["GND"] += gnd
    c_in = b.C("c_ldo_ein", "1u")
    vsys & c_in & gnd
    c_out = b.C("c_ldo_aus", "1u")
    v3v3_dcf & c_out & gnd
