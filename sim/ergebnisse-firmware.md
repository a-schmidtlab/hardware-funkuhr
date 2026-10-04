# Ergebnisse Firmware-Tests (Phase 4): DCF77-Dekoder

- Stand: 2026-10-04
- Code: `fw/src/dcf77.c`, Tests: `fw/tests/test_dcf77.c`
- Ausführen: `make test` in `fw/` (Host-gcc mit Address- und UB-Sanitizer), `make avr` (Übersetzung für den ATmega328PB)

## Prüfprinzip

Ein Signalgenerator erzeugt das Empfängersignal Tick für Tick (10 ms), so wie die Firmware es später vom Modul abtastet. Grundlage ist eine vorgegebene Uhrzeit. Optional kommen Störungen hinzu:

| Störung | Bedeutung |
|---|---|
| Taktfehler | MCU-Takt weicht ab (interner RC-Oszillator) |
| Jitter | jede Flanke zufällig um bis zu ±x ms verschoben |
| Störimpulse | kurze Fehlimpulse (Länge und Häufigkeit einstellbar) |
| Pulsausfall | ein Sekundenpuls fehlt ganz |
| Bitfehler | Puls mit vertauschter (100 ↔ 200 ms) oder mehrdeutiger Länge (150 ms) |
| Schaltsekunde | Minute mit 61 Sekunden |

Jede Meldung des Dekoders wird geprüft:
- **Inhalt:** Stimmt die Uhrzeit genau?
- **Zeitpunkt:** Liegt der gemeldete Sekundenbeginn höchstens ±60 ms neben der echten Minutenmarke?

## Ergebnisse

| Test | Ergebnis |
|---|---|
| Minutenrechnung über Monats-, Jahres- und Schaltjahrgrenzen | ✓ |
| Jeder einzelne Bitfehler in den Bits 21–58 wird erkannt (Parität/Bereich) | ✓ 38 von 38 |
| Sauberes Signal, Start mitten in einer Minute | ✓ erste Meldung nach ca. 2,5 Minuten, danach jede Minute |
| Taktfehler −5 % und +5 %, ±5 ms Jitter, über Jahreswechsel | ✓ |
| Störimpulse 10–20 ms, im Mittel 1 je Sekunde, ±10 ms Jitter | ✓ 99 von 100 Läufen synchronisiert nach 6 Minuten |
| Zeitumstellung MEZ → MESZ | ✓ eine Minute verworfen, dann richtig |
| Minute mit Schaltsekunde | ✓ verworfen, danach richtig |
| Kein Signal, Dauerpegel, starkes Dauerrauschen | ✓ keine Meldung |
| Monte-Carlo: 20 000 Minuten, jede Minute andere Störung (von sauber bis schwer gestört, Takt ±7 %) | ✓ 1340 Meldungen, **0 falsch** |
| Übersetzung für ATmega328PB (`-Wall -Wextra -Wconversion -Werror`) | ✓ 1442 Byte Flash, 0 Byte RAM statisch (Zustand ca. 40 Byte im Aufrufer) |

**Gesamt: 61 Prüfungen, 0 Fehler.**

## Was die Tests aufgedeckt haben

Die Tests haben während der Entwicklung drei Schwächen gefunden, die jetzt behoben sind:

1. **Zu enge Pulsfenster:** Mit einer Lücke zwischen „0“ (bis 140 ms) und „1“ (ab 160 ms) verwarf schon ein Störimpuls an der Pulsflanke die ganze Minute.
2. **Zu frühe Minutenmarke:** Ein Störimpuls in den letzten 200 ms von Sekunde 59 wurde als Minutenmarke gedeutet. Die Uhr wäre bis zu 0,2 s zu früh gestellt worden. Gefunden hat das erst die zusätzliche Prüfung des Meldezeitpunkts.
3. **Flankenmessung grundsätzlich störanfällig:** Der Bitwert wird jetzt per Mehrheit in Abtastfenstern bestimmt statt an der fallenden Flanke (siehe [Entscheidung 009](../docs/decisions/009-dcf77-dekoder.md)).

## Variantenvergleich der Abtastfenster

Gemessen mit 200 Läufen des Störimpuls-Tests (Kriterium dort: mindestens 3 Meldungen in 6 Minuten) und dem Monte-Carlo-Test.

| Bitfenster (Ticks) | „0“ bis | „1“ ab | Störimpuls-Test | Monte-Carlo-Meldungen | falsch |
|---|---|---|---|---|---|
| **8–15** | **3** | **5** | **128/200** | **1340** | **0** |
| 9–16 | 3 | 5 | 112/200 | 1343 | 0 |
| 9–15 | 2 | 5 | 96/200 | 1147 | 0 |
| 10–16 | 2 | 5 | 69/200 | 1155 | 0 |
| 8–14 | 2 | 5 | 61/200 | 1183 | 0 |
| 9–16 | 2 | 6 | 61/200 | 1057 | 0 |
| 8–15 | 2 | 6 | 45/200 | 1081 | 0 |

Gewählt: Fenster 8–15, Schwellen 3 und 5. Keine Variante hat je eine falsche Zeit gemeldet. Die Sicherheit kommt aus Paritäten, Raster der Minutenmarke und der Prüfung zweier aufeinanderfolgender Minuten, nicht aus engen Schwellen.

## Grenzen

- Die Störmodelle sind synthetisch. Wie das echte Modul neben der gemultiplexten Anzeige aussieht, zeigt erst der Prototyp (Phase 5). Dabei werden echte Signale aufgezeichnet und als weitere Testfälle übernommen.
- Ob das Modul bei abgesenktem Träger High oder Low ausgibt, legt die Firmware in Phase 5 am echten Modul fest. Der Dekoder erwartet „puls = true“ für die Absenkung.
- Der Dekoder liefert die Zeit und den Zeitpunkt. Das Stellen des DS3231 und das Zeitfenster für die nächtliche Synchronisation (F4) sind Teil der übrigen Firmware.
