# 004 – Anzeige und Ansteuerung

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Gefordert sind 6 Ziffern (HH:MM:SS) als LED-7-Segment mit 20–30 mm Ziffernhöhe, dauerhaft an (A1, A2, A4). Die Versorgung ist eine einzelne Li-Ion-Zelle mit 3,0–4,2 V.

Knackpunkt ist die Flussspannung. Das ist die Spannung, die über einer leuchtenden LED abfällt. Große 7-Segment-Anzeigen (ab ca. 1 Zoll) haben oft 2 LED-Chips pro Segment in Reihe, mit etwa 3,6–4 V Flussspannung. Die leuchten bei einem fast leeren Akku (3,0 V) nicht mehr. Wir brauchen also eine Anzeige mit **einem Chip pro Segment** (ca. 1,8–2 V).

## Optionen

Anzeige:

1. **6 × Einzelziffer 0,8 Zoll (20,3 mm), ein Chip pro Segment**, plus einzelne LEDs für die Doppelpunkte: freie Anordnung, Doppelpunkte genau dort, wo sie hingehören.
2. **Fertige 4-stellige Uhrenanzeige 0,8 Zoll + 2-stellige Anzeige:** weniger Lötstellen, aber zwei unterschiedliche Bauformen mit eventuell unterschiedlicher Farbe und Helligkeit.
3. **1-Zoll-Ziffern (25,4 mm):** meist 2 Chips pro Segment und damit ungeeignet ohne Spannungswandler.

Ansteuerung:

1. **Direktes Multiplexing durch den Mikrocontroller:** Segmentpins → Vorwiderstand → Segment. Ein N-MOSFET pro Stelle schaltet die gemeinsame Kathode nach Masse. Schwankungen der Akkuspannung gleicht die Firmware über die Pulsbreite (PWM) aus.
2. **Konstantstrom-Treiber-IC** (z. B. TLC5916, Schieberegister mit 8 Konstantstromausgängen): gleichmäßige Helligkeit ohne Firmware-Ausgleich, aber ein zusätzlicher IC und ein weiterer Bus.
3. **MAX7219:** braucht 4,0–5,5 V, passt nicht zum Akku.

## Entscheidung

Gewählt: **6 × Kingbright SC08-11SURKWA** (gemeinsame Kathode, Hyper-Rot) plus 4 rote 3-mm-LEDs als Doppelpunkte und 1 LED als Sync-Status (F5), **direkt gemultiplext** vom ATmega328PB, weil:

- die Anzeige einen Chip pro Segment hat (1,85 V typ.). Sie funktioniert damit bis zum Akkuende ohne Spannungswandler.
- sie sehr effizient ist (61 mcd typ. bei 10 mA). Für den Nachttisch reichen Bruchteile eines Milliampere pro Segment.
- direktes Multiplexing die wenigsten Bauteile braucht und gut nachvollziehbar ist.
- Kingbright ein vollständiges Datenblatt liefert und bei DigiKey und Mouser lagernd ist (H2).

Datenblatt-Kernwerte (SC08-11SURKWA):

| Wert | |
|---|---|
| Ziffernhöhe | 20,32 mm (0,8 Zoll), erfüllt A2 |
| Farbe, Material | Hyper-Rot 630 nm, AlGaInP, grauer Rahmen, weiße Segmente |
| Schaltung | gemeinsame Kathode, Dezimalpunkt rechts |
| Flussspannung | 1,85 V typ., 2,35 V max. bei 10 mA |
| Lichtstärke | 61 mcd typ. (21 mcd min.) bei 10 mA |
| Max. Strom | 30 mA Dauer, 185 mA Puls (1/10 Tastgrad, 0,1 ms) |
| Bauform | THT, 20,0 × 27,7 × 8,4 mm |
| Preis | DigiKey ca. 3,40 $ (1 Stück), 2,33 $ (ab 18 Stück) |

Multiplex-Prinzip: 7 Stellen (6 Ziffern + 1 „Stelle“ für die Doppelpunkte und die Status-LED) leuchten nacheinander, jede 1/7 der Zeit. Die Stellenfrequenz liegt bei etwa 1 kHz, die Bildwiederholrate bei etwa 140 Hz, also flimmerfrei.

## Konsequenzen

- Die Helligkeit hängt von der Akkuspannung ab: Der Segmentstrom fällt von 4,2 V auf 3,0 V auf weniger als die Hälfte. Die Firmware misst VCC und passt die Pulsbreite an.
- Stellentreiber: N-MOSFET mit niedriger Schwellspannung, der schon bei 3 V Gatespannung voll durchschaltet (z. B. AO3400A, JLC Basic). Eine Stelle führt bis zu 8 × Segmentspitzenstrom. Die Auswahl folgt in Phase 3.
- Die Stellenfrequenz darf kein Teiler von 77 500 Hz sein (siehe [architektur.md](../architektur.md), Abschnitt 7).
- Die Anzeige kostet mit ca. 15–20 € fast ein Drittel des Budgets. Günstigere LCSC-Anzeigen lassen sich in Phase 3 prüfen, wenn deren Datenblatt die Flussspannung sauber angibt.
