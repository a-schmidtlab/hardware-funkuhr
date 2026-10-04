"""Bauteilkatalog der Funkuhr.

Jede Funktion verlangt als erstes Argument eine feste Kennung (tag). SKiDL
ordnet Bauteile darüber stabil zu; ohne tag entstünde bei jedem Lauf eine
zufällige Kennung, und das Layout (Phase 6) verlöre die Zuordnung.

Jedes Bauteil wird hier genau einmal mit Symbol, Footprint und Bestellnummer
beschrieben. Die Blöcke (versorgung.py, mcu.py, ...) holen sich ihre Bauteile
nur über diese Funktionen. So steht jede Teileauswahl an einer Stelle.

Alle LCSC-Nummern wurden am 2026-10-04 auf lcsc.com geprüft (Seitentitel =
Herstellerteilenummer). Bauteile ohne LCSC-Nummer kommen von DigiKey/Mouser.
"""

from skidl import Part

# Footprints für Standardbauteile (handlötbar: 0805, SOT-23, TQFP 0,8 mm, THT)
FP_R = "Resistor_SMD:R_0805_2012Metric"
FP_C = "Capacitor_SMD:C_0805_2012Metric"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"

# Widerstände 0805, 1 %, UNI-ROYAL 0805W8F..., alle JLC Basic
WIDERSTAND_LCSC = {
    "270": ("0805W8F2700T5E", "C17590"),
    "1k": ("0805W8F1001T5E", "C17513"),
    "4k7": ("0805W8F4701T5E", "C17673"),
    "5k1": ("0805W8F5101T5E", "C27834"),
    "10k": ("0805W8F1002T5E", "C17414"),
    "100k": ("0805W8F1003T5E", "C17407"),
}

# Keramikkondensatoren 0805, alle JLC Basic
KONDENSATOR_LCSC = {
    "100n": ("YAGEO", "CC0805KRX7R9BB104", "C49678"),  # 50 V, X7R
    "1u": ("Samsung", "CL21B105KBFNNNE", "C28323"),  # 50 V, X7R
    "10u": ("Samsung", "CL21A106KAYNNNE", "C15850"),  # 25 V, X5R
    "22u": ("Samsung", "CL21A226MAQNNNE", "C45783"),  # 25 V, X5R
}


def _felder(p, hersteller=None, mpn=None, lcsc=None, bezug=None, bestueckung=None):
    """Bestellangaben als Felder an das Bauteil hängen (landen in Netzliste/BOM)."""
    if hersteller:
        p.fields["Hersteller"] = hersteller
    if mpn:
        p.fields["MPN"] = mpn
    if lcsc:
        p.fields["LCSC"] = lcsc
    if bezug:
        p.fields["Bezug"] = bezug
    if bestueckung:
        p.fields["Bestückung"] = bestueckung
    return p


def R(tag, wert, bestueckung=None):
    mpn, lcsc = WIDERSTAND_LCSC[wert]
    p = Part("Device", "R", value=wert, footprint=FP_R, tag=tag)
    return _felder(p, "UNI-ROYAL", mpn, lcsc, bestueckung=bestueckung)


def C(tag, wert, bestueckung=None):
    hersteller, mpn, lcsc = KONDENSATOR_LCSC[wert]
    p = Part("Device", "C", value=wert, footprint=FP_C, tag=tag)
    return _felder(p, hersteller, mpn, lcsc, bestueckung=bestueckung)


def pmos_ao3401a(tag):
    """P-MOSFET −30 V, SOT-23, Pins 1=G 2=S 3=D (Symbol und Datenblatt AOS)."""
    p = Part("Transistor_FET", "AO3401A", footprint=FP_SOT23, tag=tag)
    return _felder(p, "AOS", "AO3401A", "C15127")


def nmos_ao3400a(tag):
    """N-MOSFET 30 V, SOT-23, Vgs(th) 0,65–1,45 V, Pins 1=G 2=S 3=D."""
    p = Part("Transistor_FET", "AO3400A", footprint=FP_SOT23, tag=tag)
    return _felder(p, "AOS", "AO3400A", "C20917")


def schottky_bat54(tag, bestueckung=None):
    """BAT54 im SOT-23 (Pin 1 = Anode, Pin 3 = Kathode, Pin 2 frei).

    Das KiCad-Symbol BAT54W hat dieselbe Pinbelegung; nur der Footprint ist
    hier SOT-23 statt SOT-323, weil SOT-23 leichter von Hand zu löten ist.
    """
    p = Part("Diode", "BAT54W", value="BAT54", footprint=FP_SOT23, tag=tag)
    return _felder(p, "High Diode", "BAT54", "C466635", bestueckung=bestueckung)


def ldo_xc6206_33(tag):
    """LDO 3,3 V, Ruhestrom ca. 1 µA, SOT-23, Pins 1=GND 2=VO 3=VI."""
    p = Part("Regulator_Linear", "XC6206PxxxMR", value="XC6206P332MR", footprint=FP_SOT23, tag=tag)
    return _felder(p, "TOREX", "XC6206P332MR-G", "C5446")


def mcu_atmega328pb(tag):
    p = Part("MCU_Microchip_ATmega", "ATmega328PB-A",
             footprint="Package_QFP:TQFP-32_7x7mm_P0.8mm", tag=tag)
    return _felder(p, "Microchip", "ATMEGA328PB-AU", "C132230")


def rtc_ds3231sn(tag):
    """DS3231SN. KiCad hat nur das Symbol DS3231M; Pinbelegung im SO-16 ist
    identisch (Datenblatt DS3231: Pins 5–12 N.C., müssen auf Masse)."""
    p = Part("Timer_RTC", "DS3231M", value="DS3231SN",
             footprint="Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm", tag=tag)
    return _felder(p, "Analog Devices (Maxim)", "DS3231SN#T&R", "C9866")


def anzeige_sc08(tag):
    p = Part("funkuhr", "SC08-11SURKWA", footprint="funkuhr:Kingbright_SC08-11", tag=tag)
    return _felder(p, "Kingbright", "SC08-11SURKWA", bezug="DigiKey/Mouser")


def led_rot_3mm(tag):
    """3-mm-LED rot (624 nm, diffus) für Doppelpunkte und Status, passend zur
    Anzeige (630 nm). Pin 1 = Kathode."""
    p = Part("Device", "LED", value="rot 3mm", footprint="LED_THT:LED_D3.0mm", tag=tag)
    return _felder(p, "Everlight", "204-10SURD/S530-A3", "C99772")


def taster(tag):
    p = Part("Switch", "SW_Push", value="Taster", footprint="Button_Switch_THT:SW_PUSH_6mm", tag=tag)
    return _felder(p, "SOFNG", "TS-1102-5016", "C111609")


def halter_18650(tag):
    """Keystone 1042: SMD-Halter für 18650, auch für geschützte (längere) Zellen."""
    p = Part("Device", "Battery_Cell", value="18650",
             footprint="Battery:BatteryHolder_Keystone_1042_1x18650", tag=tag)
    return _felder(p, "Keystone", "1042", bezug="DigiKey/Mouser")


def halter_cr2032(tag):
    p = Part("Device", "Battery_Cell", value="CR2032",
             footprint="Battery:BatteryHolder_MYOUNG_BS-07-A1BJ001_CR2032", tag=tag)
    return _felder(p, "MYOUNG", "BS-07-A1BJ001", "C2979167")


def usb_c_nur_strom(tag, bestueckung=None):
    p = Part("Connector", "USB_C_Receptacle_PowerOnly_6P", value="USB-C 5V",
             footprint="Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal", tag=tag)
    return _felder(p, "GCT", "USB4125-GF-A", bezug="DigiKey/Mouser", bestueckung=bestueckung)


def stiftleiste(tag, reihen, pole, wert):
    if reihen == 1:
        p = Part("Connector_Generic", f"Conn_01x{pole:02d}", value=wert,
                 footprint=f"Connector_PinHeader_2.54mm:PinHeader_1x{pole:02d}_P2.54mm_Vertical", tag=tag)
    else:
        p = Part("Connector_Generic", f"Conn_02x{pole // 2:02d}_Odd_Even", value=wert,
                 footprint=f"Connector_PinHeader_2.54mm:PinHeader_2x{pole // 2:02d}_P2.54mm_Vertical", tag=tag)
    return _felder(p, bezug="beliebige Stiftleiste 2,54 mm")


def testpunkt(tag, name):
    p = Part("Connector", "TestPoint", value=name, footprint="TestPoint:TestPoint_Pad_D1.5mm", tag=tag)
    return p

