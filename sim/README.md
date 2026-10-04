# Simulation (Phase 4)

- Stand: freigegeben (2026-10-04)
- Analog: [ergebnisse.md](ergebnisse.md), erzeugt mit `make` in `sim/` (ngspice 42, Modelle in [modelle.lib](modelle.lib))
- Firmware: [ergebnisse-firmware.md](ergebnisse-firmware.md), Tests mit `make test` in `fw/`

## Was simuliert wurde

| Teil | Inhalt | Ergebnis |
|---|---|---|
| Modellprüfung | LED, BAT54, AO3400A, AO3401A gegen Datenblattpunkte | ✓ alle Modelle passen |
| Anzeige | Segmentströme bei 3,0 / 3,7 / 4,2 / 4,75 V, alle ungünstigen Ecken (32 je Spannung) | ✓ |
| Versorgung | Akku, USB, Programmer 5,25 V und 3,3 V, verpolter Akku, Last 1–80 mA | ✓ Akku wird in keinem Fall geladen |
| Störungen auf VSYS | Multiplexen mit 1 kHz, Welligkeit und Spektrum um 77,5 kHz | ✓ |
| Strombudget | Summe aller Verbraucher, Laufzeit | ✓ 7–18 Tage |
| DCF77-Dekoder | 61 Prüfungen, davon 20 000 gestörte Minuten | ✓ 0 falsche Meldungen |

## Abgleich mit dem Lastenheft

| Anforderung | Nachweis in Phase 4 |
|---|---|
| F2 Zeitsynchronisation per DCF77, inkl. Sommer-/Winterzeit | Dekoder liefert Zeit und MEZ/MESZ, Umstellung getestet |
| F3 ≤ 1 s/Tag ohne Empfang | DS3231 ±2 ppm = 0,17 s/Tag (Datenblatt, Entscheidung 002); nicht simulierbar |
| F4 Synchronisation ≥ 1× täglich | Dekoder synchronisiert auch bei starken Störungen in wenigen Minuten (99/100 Läufe < 6 min) |
| E3 Laufzeit ca. 1–4 Wochen | 7 bis 18 Tage je nach Helligkeit und Zelle |
| S2 Verpolschutz | verpolter Akku: Strom < 1 µA, VSYS bleibt bei 0 V |
| E2 kein Laden im Gerät | in allen Fällen mit USB oder Programmer: Ladestrom ≤ 0 (siehe Tabelle 2) |
| A2 Ablesbarkeit | mittlerer Segmentstrom ≥ 0,32 mA bis 3,0 V in der ungünstigsten Ecke; Lesbarkeit selbst prüft Phase 5 |
| M3 Antenne vs. Anzeige | Oberwellen des Multiplexens liegen bei 77,0/78,0 kHz, bei 77,5 kHz um Faktor > 500 kleiner; Feldkopplung prüft Phase 5 |

## Was die Simulation nicht abdeckt (→ Phase 5)

- Funkempfang und magnetische Kopplung der Anzeigeströme in die Ferritantenne
- Störunterdrückung (PSRR) des XC6206 bei 77 kHz. Das Datenblatt nennt nur 40 dB bei 1 kHz.
- Lesbarkeit der Anzeige bei Tag und Nacht
- Pegel und Polarität des echten Modulausgangs
- Störungen durch ein echtes USB-Ladegerät

## Änderungen an der Schaltung durch Phase 4

Keine. Die offenen Punkte 4 (Helligkeit bei leerem Akku) und 6 (5-V-Betrieb mit Last) aus [docs/schaltung.md](../docs/schaltung.md) sind durch die Simulation geklärt. Die Helligkeit erreicht in der ungünstigsten Ecke 0,32 mA. Bei 5-V-Betrieb fließt nie Ladestrom in den Akku.

## Prüfliste fürs Gate (Workflow Phase 4)

1. [ergebnisse.md](ergebnisse.md), Abschnitt 0: Passen die Modelle zu den Datenblattwerten?
2. Abschnitt 2: In keiner Zeile ist der Akkustrom negativ (Laden).
3. Abschnitt 3: Ist die Laufzeit von 7 bis 18 Tagen für dich in Ordnung?
4. [ergebnisse-firmware.md](ergebnisse-firmware.md): Sind die Störarten aus deiner Sicht realistisch genug? Fehlt ein Fall?
5. [Entscheidung 009](../docs/decisions/009-dcf77-dekoder.md): Verfahren des Dekoders
