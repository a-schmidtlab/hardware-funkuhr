"""Block 3: Zeitbasis DS3231SN mit CR2032-Gangreserve (Entscheidung 002).

Pins laut Datenblatt DS3231 (Rev. 10):
- VCC mit 0,1–1 µF abblocken
- Pins 5–12 (N.C.) müssen auf Masse; im KiCad-Symbol heißen sie GND
- 32kHz: Open-Drain, darf offen bleiben (wird per Firmware abgeschaltet)
- INT/SQW: Open-Drain, braucht Pull-up → 1-Hz-Takt an INT0
- RST: hat internen 50-kΩ-Pull-up, keinen externen anschließen → offen
- VBAT: Knopfzelle; Abblockkondensator nicht nötig, wenn I²C im
  Backup-Betrieb ruht (hier: ohne VSYS läuft auch die MCU nicht)
- SDA/SCL: Open-Drain, brauchen Pull-ups
"""

from skidl import Net, subcircuit  # NC (= nicht angeschlossen) stellt SKiDL global bereit

import bauteile as b

# I²C-Pull-ups 4,7 kΩ an VSYS (max. ca. 4,75 V):
# Sinkstrom beim Low-Pegel ≤ 3 mA (I²C-Standard)
R_I2C = 4.7e3
assert 4.75 / R_I2C < 3e-3  # 1,0 mA
# Anstiegszeit bei ca. 50 pF Buskapazität (kurze Leitungen):
# t_r ≈ 0,85 · R · C muss < 1 µs sein (Standard-Mode 100 kHz)
assert 0.85 * R_I2C * 50e-12 < 1e-6  # 0,2 µs


@subcircuit
def rtc(vsys, gnd, sda, scl, sqw):
    u = b.rtc_ds3231sn("rtc")
    u["VCC"] += vsys
    u["GND"] += gnd  # Pin 13 und Pins 5–12
    u["SDA"] += sda
    u["SCL"] += scl
    u["~{INT}/SQW"] += sqw
    u["32KHZ"] += NC
    u["~{RST}"] += NC

    c = b.C("c_rtc", "100n")
    vsys & c & gnd

    v_backup = Net("V_BACKUP")
    bt = b.halter_cr2032("knopfzelle")
    bt["+"] += v_backup
    bt["-"] += gnd
    u["VBAT"] += v_backup

    for name, net in (("r_sda", sda), ("r_scl", scl)):
        r = b.R(name, "4k7")
        net & r & vsys
    r_sqw = b.R("r_sqw", "10k")
    sqw & r_sqw & vsys
