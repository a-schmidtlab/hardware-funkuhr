# Simulationsergebnisse Funkuhr Rev. A

Automatisch erzeugt mit `make` in `sim/` (ngspice 42, Modelle in `sim/modelle.lib`). Nicht von Hand ändern.

## 0. Modellprüfung gegen Datenblatt

Jedes Modell wird mit einer Stromquelle bzw. Gatespannung betrieben und mit den Datenblattpunkten verglichen. Bei Höchstwerten darf das Modell bis 0,05 V darüber liegen (pessimistisch), aber höchstens 0,02 V darunter. R_DS(on): ±15 % um den Höchstwert; das entspricht bei 80 mA weniger als 2 mV.

| Bauteil | Bedingung | Datenblatt | Modell | |
|---|---|---|---|---|
| LED typ. | U_F bei 10 mA | 1.85 V | 1.851 V | ✓ |
| LED max. | U_F bei 10 mA | 2.35 V | 2.352 V | ✓ |
| BAT54 max. | U_F bei 0.1 mA | 0.24 V | 0.240 V | ✓ |
| BAT54 max. | U_F bei 1 mA | 0.32 V | 0.323 V | ✓ |
| BAT54 max. | U_F bei 10 mA | 0.40 V | 0.431 V | ✓ |
| BAT54 max. | U_F bei 30 mA | 0.50 V | 0.533 V | ✓ |
| BAT54 max. | U_F bei 100 mA | 0.80 V | 0.799 V | ✓ |
| AO3400A | R_DS(on) bei \|U_GS\| = 2.5 V | ≤ 48 mΩ | 48.0 mΩ | ✓ |
| AO3400A | R_DS(on) bei \|U_GS\| = 4.5 V | ≤ 32 mΩ | 32.0 mΩ | ✓ |
| AO3401A | R_DS(on) bei \|U_GS\| = 2.5 V | ≤ 85 mΩ | 73.9 mΩ | ✓ |
| AO3401A | R_DS(on) bei \|U_GS\| = 4.5 V | ≤ 60 mΩ | 60.0 mΩ | ✓ |

## 1. Anzeige: Segmentströme

Eine aktive Stelle, Gate des Stellentreibers auf VSYS. Ecken: LED typ./max. Flussspannung, MCU-Pin 50/90 Ω (Datenblatt), Vorwiderstand 270 Ω ± 1 %, AO3400A mit V_GS(th) 0,65/1,45 V, 1 bzw. 8 leuchtende Segmente.

| VSYS | Spitzenstrom je Segment min … max | Mittelwert bei 1/7 (volle Helligkeit) min | Stelle max (8 Segmente) |
|---|---|---|---|
| 3.00 V | 2.22 … 3.96 mA | 0.32 mA | 31.7 mA |
| 3.70 V | 4.01 … 6.03 mA | 0.57 mA | 48.2 mA |
| 4.20 V | 5.31 … 7.53 mA | 0.76 mA | 60.2 mA |
| 4.75 V | 6.75 … 9.17 mA | 0.96 mA | 73.3 mA |

Bewertung:

- Ziel 0,3 mA mittlerer Segmentstrom bei leerem Akku (3,0 V), ungünstigste Ecke: 0.32 mA ✓ (Untergrenze 0,25 mA, siehe offener Punkt 4 in schaltung.md)
- Höchster Pinstrom 9.2 mA ≤ 20 mA (Prüfbedingung Datenblatt) ✓
- Summenstrom Portgruppe 1 (5 Segmente) 46 mA ≤ 100 mA ✓
- Stellentreiber höchstens 73 mA (AO3400A: 5,7 A) ✓
- Verlustleistung Vorwiderstand (Spitze) 23 mW ≤ 125 mW ✓

## 2. Versorgung: Akku, externe 5 V, Programmer, Verpolung

Akkustrom positiv = Akku wird entladen, negativ = Akku wird geladen. Laden darf nie vorkommen (E2). Last = Gesamtstrom der Uhr an VSYS. Akku-Innenwiderstand 150 mΩ, BAT54 mit Datenblatt-Höchstwerten und 2 µA Sperrstrom, Q1 mit V_GS(th) = −1,3 V (ungünstig).

| Fall | Akku | extern | Last | VSYS | U_GS Q1 | Akkustrom | Strom extern | |
|---|---|---|---|---|---|---|---|---|
| Akku | 3.0 V | – | 1 mA | 3.000 V | -2.98 V | +1.0016 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 3.0 V | – | 15 mA | 2.997 V | -2.98 V | +15.0016 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 3.0 V | – | 80 mA | 2.981 V | -2.97 V | +80.0016 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 3.7 V | – | 1 mA | 3.700 V | -3.68 V | +1.0019 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 3.7 V | – | 15 mA | 3.697 V | -3.68 V | +15.0019 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 3.7 V | – | 80 mA | 3.682 V | -3.66 V | +80.0019 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 4.2 V | – | 1 mA | 4.200 V | -4.18 V | +1.0022 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 4.2 V | – | 15 mA | 4.197 V | -4.17 V | +15.0022 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| Akku | 4.2 V | – | 80 mA | 4.183 V | -4.16 V | +80.0022 mA | -0.00 mA | ✓ ✓ ✓ ✓ |
| USB 4,75 V | – | 4.75 V | 1 mA | 4.427 V | +0.32 V | -0.0000 mA | +1.47 mA | ✓ |
| USB 4,75 V | – | 4.75 V | 15 mA | 4.285 V | +0.46 V | -0.0000 mA | +15.47 mA | ✓ |
| USB 4,75 V | – | 4.75 V | 80 mA | 4.006 V | +0.73 V | -0.0000 mA | +80.47 mA | ✓ |
| USB 4,75 V | 3.0 V | 4.75 V | 1 mA | 4.427 V | +0.32 V | -0.0000 mA | +1.47 mA | ✓ ✓ |
| USB 4,75 V | 3.0 V | 4.75 V | 15 mA | 4.285 V | +0.46 V | -0.0000 mA | +15.47 mA | ✓ ✓ |
| USB 4,75 V | 3.0 V | 4.75 V | 80 mA | 4.006 V | +0.73 V | -0.0000 mA | +80.47 mA | ✓ ✓ |
| USB 4,75 V | 4.2 V | 4.75 V | 1 mA | 4.427 V | +0.32 V | -0.0000 mA | +1.47 mA | ✓ ✓ |
| USB 4,75 V | 4.2 V | 4.75 V | 15 mA | 4.285 V | +0.46 V | -0.0000 mA | +15.47 mA | ✓ ✓ |
| USB 4,75 V | 4.2 V | 4.75 V | 80 mA | 4.006 V | +0.73 V | +0.0000 mA | +80.47 mA | ✓ ✓ |
| Programmer 5,25 V | 3.0 V | 5.25 V | 15 mA | 4.785 V | +0.46 V | -0.0000 mA | +15.52 mA | ✓ ✓ |
| Programmer 3,3 V | 3.0 V | 3.30 V | 15 mA | 2.836 V | +0.46 V | +0.0000 mA | +15.33 mA | ✓ ✓ |
| Programmer 5,25 V | 4.2 V | 5.25 V | 15 mA | 4.785 V | +0.46 V | -0.0000 mA | +15.52 mA | ✓ ✓ |
| Programmer 3,3 V | 4.2 V | 3.30 V | 15 mA | 3.605 V | -0.30 V | +15.0003 mA | +0.33 mA | ✓ ✓ |
| Akku verpolt | -4.2 V | – | 0 mA | -0.000 V | +0.00 V | -0.0000 mA | -0.00 mA | ✓ |
| Akku verpolt | -4.2 V | 4.75 V | 1 mA | 4.427 V | +0.32 V | -0.0000 mA | +1.47 mA | ✓ ✓ |

Hinweise zur Tabelle:

- Bei externer Versorgung und hoher Last kann VSYS unter die Akkuspannung fallen. Dann liefert der Akku über die Body-Diode bzw. den teilweise leitenden Q1 mit (positiver Akkustrom). Das ist Entladen, kein Laden.
- „Programmer 3,3 V“: Q1 sperrt nicht vollständig; die Uhr läuft dann überwiegend aus dem Akku. Auch hier wird nicht geladen.

## 2b. Störungen auf VSYS durch das Multiplexen

Ungünstigster Fall: Die Stellen wechseln mit 1 kHz zwischen voller Last (Ziffer „8“ mit Punkt, 73 mA) und keiner Last. Akku 3,7 V mit 150 mΩ Innenwiderstand, Q1 ca. 60 mΩ, an VSYS 22 µF + 10 µF + 2 × 100 nF (Keramik, je 5 mΩ ESR, 1 nH). Flanken 1 µs.

| Größe | Wert |
|---|---|
| Spitze-Spitze-Welligkeit VSYS | 15.3 mV |
| Anteil bei 1 kHz (Grundwelle) | 7.24 mV |
| Anteil bei 77,0 kHz | 25.8 µV |
| Anteil bei 77,5 kHz (DCF77) | 0.05 µV |
| Anteil bei 78,0 kHz | 0.0 µV |
| 1-kHz-Anteil hinter dem LDO (40 dB) | 72 µV |

Bewertung:

- Die Oberwellen liegen wie geplant bei 77,0 und 78,0 kHz, also 500 Hz neben DCF77. Bei 77,5 kHz selbst ist der Anteil um den Faktor 558 kleiner ✓
- Welligkeit auf VSYS 15 mV ≤ 50 mV ✓
- Die PSRR des XC6206 bei 77 kHz nennt das Datenblatt nicht; sie ist dort deutlich kleiner als 40 dB. Auch der Empfang über die Antenne (Magnetfeld der Anzeigeströme) lässt sich nicht simulieren. Beides prüft der Prototyp (Phase 5).

## 3. Strombudget und Laufzeit (E3)

Die Helligkeit stellt die Firmware per PWM ein; der mittlere Segmentstrom ist also eine Vorgabe, keine Folge der Akkuspannung. Abschnitt 1 zeigt, dass die Vorgaben bis 3,0 V erreichbar sind.

Leuchtende LEDs im Mittel: 6 Ziffern × 4,9 Segmente + 4 Doppelpunkt-LEDs = 33.4

| Verbraucher | günstig | ungünstig | Quelle |
|---|---|---|---|
| Anzeige (0,2 / 0,4 mA je LED) | 6.68 mA | 13.36 mA | Vorgabe Firmware (Architektur Abschn. 5) |
| ATmega328PB, 1 MHz, ca. halb aktiv/halb Idle | 0.25 mA | 0.90 mA | Datenblatt S. 352: aktiv 0,2/0,5 mA, Idle 0,06/0,15 mA bei 2 V, ×1,85 für 3,7 V |
| DS3231 | 0.11 mA | 0.20 mA | Datenblatt: I_CCS 110 µA, I_CCA 200 µA |
| DCF77-Modul | 0.06 mA | 0.12 mA | MAS6180C/Modul, Pollin DCF1 als Vergleich: < 90 µA typ., 120 µA max. |
| Gate-Pull-downs der Stellen (1/7 · 47 µA) | 0.01 mA | 0.01 mA | 4,7 V / 100 kΩ, je Stelle 1/7 der Zeit |
| LDO, Pull-ups in Ruhe, Leckströme | 0.01 mA | 0.02 mA | XC6206 Ruhestrom ca. 1 µA u. a. |
| **Summe** | **7.1 mA** | **14.6 mA** | |

- günstig: 3000 mAh, niedrige Helligkeit: 3000 mAh / 7.1 mA = **17.6 Tage**
- ungünstig: 2500 mAh, hohe Helligkeit: 2500 mAh / 14.6 mA = **7.1 Tage**

Anforderung E3: ca. 1–4 Wochen. Ergebnis: 7 bis 18 Tage ✓

Nicht enthalten: Nachtabsenkung per Uhrzeit (Firmware-Option). Bei halber Helligkeit von 22 bis 7 Uhr sinkt der Anzeigeanteil um ca. 19 %.

## Gesamtergebnis

Alle Prüfungen bestanden.
