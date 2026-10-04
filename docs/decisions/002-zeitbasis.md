# 002 – Zeitbasis (RTC)

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

F3 fordert freilaufend höchstens 1 s Abweichung pro Tag. Ein Tag hat 86 400 s, also sind 1 s/Tag = 11,6 ppm (Millionstel). Das muss auch gelten, wenn die Uhr nie DCF-Empfang hatte und von Hand gestellt wurde (F6).

Zum Vergleich: Ein normaler 32,768-kHz-Uhrenquarz hat ±20 ppm Fertigungstoleranz, also bis 1,7 s/Tag. Dazu kommt Temperaturdrift. Er allein erfüllt F3 nicht.

Außerdem ist der Akku wechselbar (E1). Ohne Gangreserve ist die Uhrzeit nach jedem Wechsel weg, bis wieder DCF-Empfang da ist. Das kann bis zur nächsten Nacht dauern.

## Optionen

1. **Uhrenquarz am Mikrocontroller + Kalibrierung per DCF77:** Die Firmware misst die Abweichung zwischen zwei Synchronisationen und rechnet sie heraus. Das ist billig, aber ohne jemals empfangenes DCF-Signal unkalibriert (bis 1,7 s/Tag) und braucht mehr Firmware.
2. **Uhrenquarz mit ±10 ppm:** bestenfalls 0,9 s/Tag bei 25 °C, mit Temperaturdrift knapp darüber. Das ist zu knapp.
3. **DS3231SN** (RTC mit eingebautem TCXO, I²C): ±2 ppm von 0 bis 40 °C ≈ 0,17 s/Tag ohne Kalibrierung. Er hat einen eigenen Backup-Eingang für eine Knopfzelle.

## Entscheidung

Gewählt: **DS3231SN** (Analog Devices/Maxim, SO-16 mit 1,27 mm Pitch), weil:

- er F3 ohne Kalibrierung und ohne DCF-Empfang sicher erfüllt, mit Faktor 6 Reserve.
- seine Backup-Knopfzelle (CR2032) die Zeit beim Akkuwechsel hält.
- er einen 1-Hz-Takt (SQW-Pin) für das Weiterschalten der Sekunden liefert. Die Firmware wird dadurch einfacher.

Datenblatt-Kernwerte (DS3231):

| Wert | |
|---|---|
| Genauigkeit | ±2 ppm (0 bis +40 °C), ±3,5 ppm (−40 bis +85 °C) |
| Versorgung VCC | 2,3–5,5 V |
| Strom an VCC | 110 µA Standby, 200 µA aktiv (bei 3,63 V) |
| Backup-Eingang VBAT | Knopfzelle, wenige µA |
| Schnittstelle | I²C (bis 400 kHz) |
| Ausgänge | SQW/INT (z. B. 1 Hz), 32 kHz (wird abgeschaltet) |
| Gehäuse | SO-16, 300 mil, gut handlötbar |

## Konsequenzen

- Zusatzkosten ca. 4–10 € plus ca. 1,50 € für Knopfzellenhalter und Zelle.
- Er braucht 2 Pins für I²C und 1 Pin für den 1-Hz-Takt.
- Achtung Fälschungen: nur bei autorisierten Händlern kaufen (LCSC, Mouser, DigiKey), nicht auf Marktplätzen.
- Der 32-kHz-Ausgang wird abgeschaltet. Er stört zwar nicht direkt bei 77,5 kHz, aber jede unnötige Taktquelle in Empfängernähe ist zu vermeiden.
- Die CR2032 als zweite Zelle für die Gangreserve ist freigegeben (2026-10-04). Sie hält bei wenigen µA mehrere Jahre.
