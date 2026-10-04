# 001 – Mikrocontroller

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Der Mikrocontroller dekodiert DCF77, liest und stellt die RTC, multiplext die Anzeige und fragt die Taster ab. Randbedingungen:

- Er läuft direkt an der Versorgung VSYS: 3,0–4,2 V aus der Zelle, ca. 4,7 V mit der optionalen externen Versorgung ([006](006-externe-5v-versorgung.md)).
- Er ist handlötbar (H1: Pitch ≥ 0,65 mm, kein QFN).
- Er hat eine Programmierschnittstelle (H5).
- Er bietet etwa 25 I/O-Pins (siehe Pin-Budget in [architektur.md](../architektur.md)).
- Er braucht wenig Strom und passt zum Prototyp mit Arduino Nano (Workflow Phase 5).

## Optionen

1. **ATmega328P** (TQFP-32, 0,8 mm Pitch): der Chip des Arduino Nano. 20 digitale I/O plus 2 reine Analogeingänge. Das reicht nur knapp: Die Taster müssten über eine Widerstandsleiter an einen Analogeingang, und es bleibt keine Reserve.
2. **ATmega328PB** (TQFP-32, 0,8 mm Pitch): Nachfolger des 328P mit 27 I/O, zwei zusätzlichen Timern und je zwei UART, SPI und I²C. Er ist weitgehend codekompatibel zum 328P, Arduino unterstützt ihn über „MiniCore“.
3. **STM32G031** (TSSOP-20, 0,65 mm Pitch): ARM Cortex-M0+, sparsamer, mit eingebauter RTC und Kalibrierung. Er hat aber zu wenige Pins für direktes Multiplexing und bräuchte deshalb einen Anzeigetreiber-IC. Dazu kommen eine steilere Lernkurve und eine andere Werkzeugkette (SWD, STM32CubeIDE oder libopencm3).
4. **ATtiny3216** (SOIC-20) + Anzeigetreiber-IC: wenige Pins. Der Treiber-IC (z. B. TLC5916) kostet zusätzlich Fläche und Geld.

## Entscheidung

Gewählt: **ATmega328PB-AU** (LCSC C132230, ca. 1,90 € Einzelstück), weil:

- er genug Pins für direktes Multiplexing hat, ohne zusätzlichen Treiber-IC, und 1 Pin Reserve bleibt.
- er im TQFP-32 mit 0,8 mm Pitch handlötbar ist.
- er bei 1,8–5,5 V läuft, also im ganzen Akkubereich und an externen 5 V ohne Regler.
- der Prototyp auf einem Arduino Nano (328P) laufen kann und der Code fast unverändert übernommen wird.
- AVR einfach und gut dokumentiert ist. Das passt zum Lernziel.

Datenblatt-Kernwerte (ATmega328PB):

| Wert | |
|---|---|
| Versorgung | 1,8–5,5 V |
| Max. Takt | 4 MHz ab 1,8 V, 10 MHz ab 2,7 V, 20 MHz ab 4,5 V |
| Geplanter Takt | interner 8-MHz-RC-Oszillator, geteilt auf 1 MHz (sparsam, ab 1,8 V zulässig) |
| Speicher | 32 KB Flash, 2 KB RAM, 1 KB EEPROM |
| I/O | 27 Pins, bis 20 mA je Pin (Summenstrom pro Portgruppe beachten, Phase 3) |
| ADC | 10 bit, interne Referenz 1,1 V |
| Programmierung | ISP (6-polig: MOSI, MISO, SCK, RESET, VCC, GND) |

## Konsequenzen

- Takt aus dem internen RC-Oszillator: Er ist ungenau (±1–2 %), reicht aber für die DCF-Pulsbreiten (100 ms vs. 200 ms). Die genaue Zeit kommt vom DS3231 (siehe [002](002-zeitbasis.md)).
- Die Taster teilen sich die Pins mit dem ISP. Während des Programmierens darf keiner gedrückt sein.
- Der Prototyp mit Arduino Nano (328P) hat weniger Pins. Er wird deshalb mit reduzierter Anzeige aufgebaut, z. B. 4 Stellen.
- Werkzeuge nach Freigabe: `avr-gcc`, `avr-libc`, `avrdude`, ISP-Programmer (USBasp oder „Arduino as ISP“).
- JLC-Basic-Teil? Nein, „Extended“. H3 ist nur „soll“.
