"""Block 6: Taster (B1, max. 3) und Testpunkte (H6).

Taster schalten gegen GND; die MCU nutzt ihre internen Pull-ups (ca. 20–50 kΩ).
Die Tasterpins sind gleichzeitig MOSI/MISO/SCK des ISP-Steckers. Der 1-kΩ-
Serienwiderstand schützt den Programmer, falls beim Programmieren ein Taster
gedrückt ist (sonst Kurzschluss eines Programmer-Ausgangs nach GND).
"""

from skidl import Net, subcircuit

import bauteile as b

# Low-Pegel bei gedrücktem Taster: Teiler aus 1 kΩ und internem Pull-up
# (Datenblatt: min. 20 kΩ) muss unter der Low-Schwelle 0,3 · VCC liegen
R_SERIE = 1e3
R_PULLUP_MIN = 20e3
assert 3.0 * R_SERIE / (R_SERIE + R_PULLUP_MIN) < 0.3 * 3.0  # 0,14 V < 0,9 V
# Strom aus einem 5-V-Programmer-Ausgang bei gedrücktem Taster
assert 5.0 / R_SERIE <= 5e-3  # 5 mA, unkritisch


@subcircuit
def taster(taster_netze, gnd):
    for i, net in enumerate(taster_netze, start=1):
        sw = b.taster(f"taster_{i}")
        r = b.R(f"r_taster_{i}", "1k")
        r[1] += net
        Net(f"SW_{i}").connect(r[2], sw[1])
        sw[2] += gnd


@subcircuit
def testpunkte(netze):
    """netze: dict Name → Netz; je ein Lötpad als Messpunkt."""
    for name, net in netze.items():
        tp = b.testpunkt(f"tp_{name.lower()}", name)
        tp[1] += net
