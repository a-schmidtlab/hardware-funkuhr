# 009 – Verfahren des DCF77-Dekoders

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Der Dekoder wertet das demodulierte Signal des Empfängermoduls aus: 100-ms-Puls = 0, 200-ms-Puls = 1, fehlender Puls in Sekunde 59 = Minutenmarke.

Das Signal kann gestört sein: durch die Anzeige, durch USB-Netzteile und durch schlechten Empfang. Ziel ist ein Dekoder, der

1. **nie eine falsche Zeit meldet** (die Uhr würde sonst bis zur nächsten Synchronisation falsch gehen) und
2. trotz Störungen oft genug synchronisiert (F4: mindestens einmal täglich).

Die MCU läuft vom internen RC-Oszillator: ±2 % (2,7–4,2 V, 0–50 °C) bzw. ±3,5 % über den ganzen Spannungsbereich (Datenblatt Tabelle 33-4).

## Optionen

1. **Flankenmessung:** Pulslänge zwischen steigender und fallender Flanke. Einfach, aber jeder Störimpuls und jeder Jitter an der fallenden Flanke verfälscht die Länge.
2. **Abtastfenster mit Mehrheitsentscheidung:** Nach dem Sekundenbeginn wird in festen Fenstern gezählt, wie viele Abtastwerte aktiv sind. Ein Störimpuls kippt nur 1–2 Werte.
3. **Korrelation über viele Minuten** (Phasenregelung, Akkumulation, z. B. die „rauschfesten“ Dekoder für Arduino): sehr robust, aber deutlich komplexer und mehr RAM.

## Entscheidung

Gewählt: **2, Abtastfenster mit Mehrheitsentscheidung**, mit diesen Sicherungen:

- **Sekundenbeginn:** entprellt (3 Ticks = 30 ms). Pulse, die früher als 0,9 s nach dem letzten Sekundenbeginn kommen, werden als Störung ignoriert.
- **Bitwert:**
  - Anfangsfenster (Ticks 0–4): Hier muss der Puls aktiv sein.
  - Bitfenster (Ticks 8–15): höchstens 3 von 8 aktiv = 0, mindestens 5 = 1, sonst ist die Minute ungültig.
- **Minutenmarke:** Sie muss auf ±50 ms genau im Sekundenraster dieser Minute liegen. Das Raster wird aus den 59 Sekunden gemessen und enthält den Taktfehler.
- **Bestätigung:** Gemeldet wird erst, wenn Sekunde 0 als Bit 0 erkannt ist.
- **Inhalt:** Feste Bits, drei Paritäten und alle Wertebereiche müssen stimmen.
- **Plausibilität:** Gemeldet wird nur, wenn die Minute genau eine Minute nach der vorigen gültigen Minute liegt.

Begründung:

- In 20 000 simulierten Minuten mit allen Störarten gab es keine falsche Meldung, weder inhaltlich noch zeitlich. Das gilt für alle untersuchten Schwellenvarianten (siehe [sim/ergebnisse-firmware.md](../../sim/ergebnisse-firmware.md)).
- Bei einem Störimpuls pro Sekunde und ±10 ms Jitter synchronisieren 99 von 100 Läufen innerhalb von 6 Minuten. Für eine Synchronisation pro Nacht reicht das weit.
- Klein und gut verständlich: 1,4 KB Flash, ca. 40 Byte RAM.

## Konsequenzen

- Eine Meldung erfolgt ca. 160 ms nach dem Sekundenbeginn. Die Firmware rechnet diesen bekannten Versatz beim Stellen des DS3231 ein.
- Die Zeitumstellung (MEZ ↔ MESZ) und Schaltsekunden kosten je ein bis zwei Minuten ohne Meldung. Das ist bei einer Synchronisation pro Nacht ohne Bedeutung.
- Option 3 bleibt Rückfalloption, falls der Prototyp neben der Anzeige zu selten synchronisiert.
- Echte Signalaufzeichnungen aus Phase 5 werden als zusätzliche Testfälle übernommen.
