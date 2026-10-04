"""Block 2: Mikrocontroller ATmega328PB (Entscheidung 001).

Pinbelegung nach docs/architektur.md, Abschnitt 4. Takt: interner 8-MHz-RC-
Oszillator mit Teiler 8 = 1 MHz. Das ist die Werkseinstellung (Fuses) eines
neuen ATmega328PB, deshalb sind PB6/PB7 (XTAL) als normale I/O nutzbar.

Programmier-/Debug-Stecker:
- J ISP (2×3, Atmel-Standard): 1 MISO, 2 VCC, 3 SCK, 4 MOSI, 5 RESET, 6 GND
- J UART (1×6, FTDI-Belegung): 1 GND, 2 CTS, 3 VCC, 4 TXD, 5 RXD, 6 DTR

VCC beider Stecker geht auf V5_EXT, nicht auf VSYS. Ein Programmer, der
Strom liefert, trennt so den Akku ab (wie USB-C, siehe versorgung.py) und
lädt ihn nie. Läge VCC direkt auf VSYS, würde Q1 (durchgeschaltet) den
Akku aus dem Programmer laden.
"""

from skidl import Net, subcircuit  # NC (= nicht angeschlossen) stellt SKiDL global bereit

import bauteile as b

# Zuordnung Funktion → Pinname im KiCad-Symbol ATmega328PB-A
PIN_SEGMENT = ["PD4", "PD5", "PD6", "PD7", "PC0", "PC1", "PC2", "PC3"]  # a b c d e f g DP
PIN_STELLE = ["PB0", "PB1", "PB2", "XTAL1/PB6", "XTAL2/PB7", "PE0", "PE1"]  # Stelle 1–6, 7 = Doppelpunkte/Status
PIN_TASTER = ["PB3", "PB4", "PB5"]  # geteilt mit ISP: MOSI, MISO, SCK
PIN = {
    "SDA": "PC4",
    "SCL": "PC5",
    "RTC_SQW": "PD2",  # INT0, 1-Hz-Takt vom DS3231
    "DCF_OUT": "PD3",  # INT1, DCF-Signal
    "DCF_EN": "PE2",  # DCF-Modul ein/aus
    "RXD": "PD0",
    "TXD": "PD1",
    "RESET": "~{RESET}/PC6",
    "MOSI": "PB3",
    "MISO": "PB4",
    "SCK": "PB5",
}
PIN_RESERVE = "PE3"

# Serienwiderstände UART: schützen, falls ein 3,3-V-USB-Seriell-Adapter
# an einer mit 4,2 V laufenden MCU hängt (Strom durch Schutzdioden < 1 mA).
R_UART = 1e3
assert (4.2 - 3.3 - 0.3) / R_UART < 1e-3


@subcircuit
def mcu(vsys, v5_ext, gnd, seg, stelle, taster, sig):
    """seg: 8 Netze (a–g, DP), stelle: 7 Netze (Gates), taster: 3 Netze,
    sig: dict mit SDA, SCL, RTC_SQW, DCF_OUT, DCF_EN, RESERVE."""
    u = b.mcu_atmega328pb("mcu")

    # Versorgung: je 100 nF direkt an VCC und AVCC, dazu 10 µF als Puffer
    u["VCC"] += vsys
    u["AVCC"] += vsys
    u["GND"] += gnd
    for name in ("c_vcc", "c_avcc"):
        c = b.C(name, "100n")
        vsys & c & gnd
    c_bulk = b.C("c_mcu_puffer", "10u")
    vsys & c_bulk & gnd
    # AREF: Referenz ist AVCC bzw. intern 1,1 V; AREF nur abblocken
    c_aref = b.C("c_aref", "100n")
    Net("AREF").connect(u["AREF"], c_aref[1])
    c_aref[2] += gnd

    # Anzeige und Taster
    for net, pin in zip(seg, PIN_SEGMENT):
        net += u[pin]
    for net, pin in zip(stelle, PIN_STELLE):
        net += u[pin]
    for net, pin in zip(taster, PIN_TASTER):
        net += u[pin]

    # RTC, DCF
    for name in ("SDA", "SCL", "RTC_SQW", "DCF_OUT", "DCF_EN"):
        sig[name] += u[PIN[name]]
    sig["RESERVE"] += u[PIN_RESERVE]

    # Reset: 10 kΩ Pull-up (Microchip AN2519); kein Kondensator gegen GND,
    # damit ISP ungestört bleibt
    reset = sig["RESET"]
    reset += u[PIN["RESET"]]
    r_reset = b.R("r_reset", "10k")
    reset & r_reset & vsys

    # ISP-Stecker
    isp = b.stiftleiste("j_isp", 2, 6, "ISP")
    isp[1] += taster[1]  # MISO = PB4
    isp[2] += v5_ext
    isp[3] += taster[2]  # SCK = PB5
    isp[4] += taster[0]  # MOSI = PB3
    isp[5] += reset
    isp[6] += gnd

    # UART-Stecker (FTDI-Belegung, Sicht des Adapters: TXD sendet zur MCU)
    uart = b.stiftleiste("j_uart", 1, 6, "UART")
    uart[1] += gnd
    uart[2] += NC  # CTS wird nicht genutzt
    uart[3] += v5_ext
    r_rx = b.R("r_rxd", "1k")
    Net("UART_TXD").connect(uart[4], r_rx[1])
    Net("MCU_RXD").connect(r_rx[2], u[PIN["RXD"]])
    r_tx = b.R("r_txd", "1k")
    Net("UART_RXD").connect(uart[5], r_tx[1])
    Net("MCU_TXD").connect(r_tx[2], u[PIN["TXD"]])
    # DTR über 100 nF auf RESET: automatischer Reset für einen Bootloader
    c_dtr = b.C("c_dtr", "100n")
    Net("UART_DTR").connect(uart[6], c_dtr[1])
    c_dtr[2] += reset
