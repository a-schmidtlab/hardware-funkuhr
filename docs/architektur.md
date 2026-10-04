# Architektur – Akku-Funkuhr

- Phase: 2 (Architektur)
- Stand: freigegeben (2026-10-04)
- Bezug: [Lastenheft v1.1](lastenheft.md), Entscheidungen [001](decisions/001-mikrocontroller.md) bis [006](decisions/006-externe-5v-versorgung.md)

## 1. Überblick

Die Uhr besteht aus fünf Blöcken:

1. **Versorgung:** 18650-Zelle mit Verpolschutz, optional externe 5 V über USB-C (nur bei Bedarf bestückt), ein kleiner Spannungsregler nur für den Funkempfänger.
2. **Zeitbasis:** ein RTC-Baustein DS3231 mit eingebautem, temperaturkompensiertem Quarz. Er zählt die Zeit und hält sie auch ohne Empfang genau.
3. **DCF77-Empfänger:** fertiges Modul mit Ferritantenne. Es liefert das demodulierte Zeitsignal als Rechteckpulse.
4. **Mikrocontroller:** ATmega328PB. Er dekodiert DCF77, stellt den DS3231 und steuert die Anzeige.
5. **Anzeige:** sechs einzelne 0,8-Zoll-7-Segment-Ziffern (20,3 mm) in Rot, dazu vier LEDs für die Doppelpunkte und eine Status-LED. Der Mikrocontroller steuert sie im Multiplexbetrieb.

### Begriffe

- **RTC** (Real-Time Clock): Uhrenbaustein, der Sekunden, Minuten, Stunden und Datum selbstständig zählt.
- **TCXO** (temperaturkompensierter Quarzoszillator): Quarz, dessen Temperaturdrift ein Baustein laufend ausgleicht. Dadurch ist er etwa zehnmal genauer als ein normaler Uhrenquarz.
- **I²C:** Zweidrahtbus (Takt SCL und Daten SDA), über den der Mikrocontroller mit dem DS3231 spricht.
- **Multiplexing:** Statt alle 6 × 8 Segmente einzeln anzuschließen, teilen sich alle Ziffern dieselben 8 Segmentleitungen. Es leuchtet immer nur eine Ziffer, aber so schnell im Wechsel (über 100 Mal pro Sekunde), dass das Auge alle gleichzeitig sieht. Das spart Pins und Strom.
- **LDO** (Low-Dropout-Regler): Linearregler, der auch dann noch regelt, wenn die Eingangsspannung nur knapp über der Ausgangsspannung liegt.
- **ISP** (In-System Programming): Programmierschnittstelle der AVR-Mikrocontroller über 6 Pins. Der Chip wird auf der fertigen Platine programmiert.
- **Verpolschutz:** Schaltung, die verhindert, dass ein falsch herum eingelegter Akku die Elektronik beschädigt.
- **Bestückungsoption (DNP, „do not populate“):** Die Platine hat Lötpads und Leiterbahnen für ein Bauteil, das nur bei Bedarf eingelötet wird.
- **Schottky-Diode:** Diode mit kleinem Spannungsverlust (ca. 0,3 V). Sie lässt Strom nur in eine Richtung durch.

## 2. Blockschaltbild

```text
  optional (DNP)
 ┌──────────┐ V5_EXT   ┌──────────┐
 │ USB-C    ├────┬────►│ Schottky ├─────────┐
 │ nur 5 V  │    │     └──────────┘         │
 └──────────┘    │ Gate                     │
                 ▼                          │  VSYS (3,0–4,7 V)
 ┌──────────┐ VBAT_RAW ┌────────────┐       │
 │ 18650    ├─────────►│ P-MOSFET:  ├───────┴──────┬───────────────┬──────────────────────┐
 │ Zelle    │          │ Verpol-    │              │               │                      │
 │ (E1)     │          │ schutz +   │              │               │                      │
 └──────────┘          │ Akku-      │              │               │                      │
                       │ trennung   │              ▼               ▼                      ▼
                       └────────────┘         ┌─────────┐   ┌──────────────┐   ┌────────────────────┐
                                              │ LDO     │   │ ATmega328PB  │   │ Anzeige            │
                                              │ 3,3 V   │   │              │   │ 6 × 7-Segment 0,8" │
                                              └────┬────┘   │              │ 8 │ + Doppelpunkte     │
                                                   │3V3_DCF │  Segmente ───┼──►│ + Status-LED (F5)  │
                                                   ▼        │              │ 7 │                    │
  Ferrit-   ┌──────────────────┐  DCF-Signal        │       │  Stellen ────┼──►│ (Stellentreiber:   │
  antenne ─►│ DCF77-Modul      ├───────────────────►│       │              │   │  N-MOSFETs)        │
            │ (CANADUINO       │◄───────────────────┤ EIN   │              │   └────────────────────┘
            │  MAS6180C)       │                    │       │              │
            └──────────────────┘                    │       │  I²C + 1 Hz  │   ┌────────────────────┐
                                                    │       │◄────────────►│◄─►│ DS3231 (RTC, TCXO) │◄── CR2032
            ┌──────────────────┐                    │       │              │   │ an VSYS            │    (Gangreserve
            │ 3 Taster (B1)    ├───────────────────►│       │              │   └────────────────────┘     beim Akkuwechsel)
            └──────────────────┘                            │              │
            ┌──────────────────┐                            │              │
            │ ISP-Stecker 2×3  │◄──────────────────────────►│              │
            │ UART-Stecker 1×6 │◄──────────────────────────►│              │
            └──────────────────┘                            └──────────────┘
```

Räumliche Vorgabe (M3): Das DCF-Modul und seine Antenne sitzen am anderen Platinenende als die Anzeige. Die Antenne zeigt nicht auf die Anzeige. Die optionale USB-C-Buchse kommt ebenfalls ans Anzeigeende, weil USB-Ladegeräte den Empfang stören können.

Akku und 5 V gleichzeitig: Liegen 5 V an, sperrt der P-MOSFET und trennt den Akku ab. Die Uhr läuft dann nur aus den 5 V, und der Akku wird weder geladen noch entladen. Details stehen in [006](decisions/006-externe-5v-versorgung.md).

## 3. Spannungsebenen

| Netz | Spannung | Quelle | Verbraucher |
|---|---|---|---|
| VBAT_RAW | 3,0–4,2 V oder verpolt | Zellenhalter | nur P-MOSFET |
| V5_EXT | 5 V ± 5 % (USB) | optionale USB-C-Buchse | Schottky-Diode, Gate des P-MOSFET |
| VSYS | 3,0–4,2 V (Akku), ca. 4,7 V (extern) | P-MOSFET oder Schottky-Diode | ATmega328PB, DS3231, Anzeige, Taster |
| 3V3_DCF | 3,3 V, bei Akku unter 3,3 V knapp darunter | LDO aus VSYS | nur DCF77-Modul |
| V_BACKUP | 3,0 V | CR2032 | nur Backup-Eingang des DS3231 |

Warum der Mikrocontroller direkt an VSYS hängt und nicht an einem Regler: Der ATmega328PB arbeitet von 1,8 bis 5,5 V. Ein Regler würde nur Strom kosten. Außerdem schaltet der Mikrocontroller die Anzeige, die ebenfalls an VSYS liegt. Gleiche Spannung an beiden Seiten vermeidet Pegelprobleme. Der Empfänger bekommt dagegen einen eigenen Regler, weil er laut Datenblatt eine „saubere, stabile“ Versorgung braucht. Die Anzeige erzeugt auf VSYS Stromspitzen im Multiplextakt, und der LDO filtert sie heraus.

Pegelprüfung DCF-Signal → Mikrocontroller: Das Modul liefert High ≈ 3,3 V. Der ATmega erkennt High ab 0,6 × VCC. Im ungünstigsten Fall, bei externen 5 V und VSYS ≈ 4,7 V, liegt die Schwelle bei 0,6 × 4,7 V = 2,82 V. 3,3 V > 2,82 V, das passt mit 0,48 V Abstand. Bei leerem Akku gilt: VSYS = 3,0 V, Schwelle 1,8 V, Modul ≈ 2,9 V, das passt auch. Deshalb hat der Regler 3,3 V und nicht 3,0 V. Die genaue Rechnung mit Toleranzen folgt in Phase 3.

## 4. Pin-Budget (ATmega328PB, TQFP-32)

Der ATmega328PB hat 27 I/O-Pins. Weil wir den internen Oszillator nutzen, sind die Quarzpins PB6/PB7 frei. Die Zuordnung ist vorläufig, Phase 3 legt sie endgültig fest.

| Funktion | Pins | Vorschlag |
|---|---|---|
| Segmente a–g + DP | 8 | PD4–PD7, PC0–PC3 |
| Stellen 1–6 + Stelle 7 (Doppelpunkte, Status-LED) | 7 | PB0–PB2, PB6, PB7, PE0, PE1 |
| Taster (3) | 3 | PB3–PB5, geteilt mit ISP (MOSI/MISO/SCK) |
| I²C zum DS3231 | 2 | PC4 (SDA), PC5 (SCL) |
| 1-Hz-Takt vom DS3231 | 1 | PD2 (INT0) |
| DCF-Signal | 1 | PD3 (INT1) |
| DCF-Modul ein/aus | 1 | PE2 |
| UART (Debug-Ausgabe, Bootloader) | 2 | PD0 (RXD), PD1 (TXD) |
| Reset (für ISP) | 1 | PC6 |
| Akkuspannung, 5-V-Betrieb erkennen | 0 | intern: VCC wird gegen die 1,1-V-Referenz gemessen (über 4,4 V heißt externe Versorgung) |
| **Reserve** | **1** | PE3 (ADC7), z. B. für einen späteren Lichtsensor |
| **Summe** | **27** | |

## 5. Strombudget (Schätzung, Verifikation in Phase 4)

Die Anzeige verbraucht den meisten Strom. Im Mittel leuchten pro Ziffer 4,9 Segmente (Durchschnitt über 0–9). Bei 6 Ziffern sind das rund 29 Segmente, dazu 4 Doppelpunkt-LEDs und gelegentlich die Status-LED, zusammen etwa 34 leuchtende LEDs.

Laut Datenblatt liefert die Anzeige SC08-11SURKWA typisch 61 mcd bei 10 mA. Für einen Nachttisch sollte ein mittlerer Segmentstrom von 0,2–0,4 mA reichen, also etwa 1–2 mcd. Ob das tagsüber noch gut lesbar ist, prüft der Prototyp (Phase 5).

| Verbraucher | Strom (Mittelwert) | Quelle |
|---|---|---|
| Anzeige, 34 LEDs × 0,2–0,4 mA | 7–14 mA | Schätzung, oben |
| ATmega328PB, 1 MHz, meist im Idle-Modus | 0,3–0,6 mA | Datenblatt-Kennlinien, grob |
| DS3231 | 0,11–0,2 mA | Datenblatt: I_CCS 110 µA, I_CCA 200 µA bei 3,63 V |
| DCF77-Modul | ca. 0,1 mA | MAS6180C, genaue Zahl in Phase 3 |
| LDO, Verpolschutz | < 0,01 mA | |
| **Summe** | **ca. 8–15 mA** | |

Laufzeit mit 2500–3000 mAh nutzbarer Kapazität:

- günstig: 3000 mAh / 8 mA = 375 h ≈ **15 Tage**
- ungünstig: 2500 mAh / 15 mA = 167 h ≈ **7 Tage**

Das liegt am unteren Rand von E3 („ca. 1–4 Wochen“). Stellschrauben, falls der Prototyp mehr zeigt:

- Nachts per Uhrzeit dunkler schalten. Das kostet nur Firmware und ist kein Lichtsensor im Sinne von A3.
- Die Sekundenziffern dunkler als die Stunden und Minuten betreiben.
- In Rev. B ein Schaltregler für die LED-Versorgung. Er spart etwa 25 %, bringt aber Störungen in die Nähe des Empfängers.

## 6. Kostenschätzung (Einzelstück, ohne Platine)

| Posten | ca. € |
|---|---|
| 6 × Kingbright SC08-11SURKWA | 15–20 |
| DCF77-Modul CANADUINO (DigiKey) | 17 |
| DS3231SN | 4–10 |
| ATmega328PB | 2 |
| Halter 18650, Halter CR2032 + Zelle | 4 |
| MOSFETs, LDO, Widerstände, Kondensatoren, LEDs, Taster, Stecker | 4–6 |
| Option externe 5 V (USB-C-Buchse, Diode, Widerstände), nur wenn bestückt | ca. 1 |
| **Summe** | **ca. 46–59** (mit Option ca. 47–60) |

Das liegt an der Grenze von H7 (≤ 50 €, Priorität „kann“). Sparpotenzial: das Pollin-DCF1 statt CANADUINO (−12 €, aber schlecht lieferbar) und LCSC-Anzeigen statt Kingbright (ca. −10 €, Datenblätter oft dürftig).

## 7. Risiken für den Prototyp (Phase 5)

| Risiko | Warum | Prüfung im Prototyp |
|---|---|---|
| Empfang gestört durch Anzeige | Multiplex-Flanken erzeugen Oberwellen, siehe Hinweis im CANADUINO-Datenblatt. | Empfang mit und ohne laufende Anzeige vergleichen, Abstand variieren. |
| Helligkeit bei 0,2–0,4 mA zu gering | Schätzung, nicht gemessen | Lesbarkeit aus 2 m bei Tag und Nacht (A2) |
| Helligkeit schwankt mit Akkuspannung | Bei Vorwiderständen fällt der Strom von 4,2 V auf 3,0 V auf weniger als die Hälfte. | Firmware gleicht über die PWM-Pulsbreite aus, Akkuspannung variieren. |
| Empfang gestört durch USB-Ladegerät | Ladegeräte sind Schaltnetzteile | Empfang an einem typischen Ladegerät gegen Akkubetrieb vergleichen |
| Tiefentladung der Zelle | S1 ist „nein“, die Elektronik schützt die Zelle also nicht selbst. | Geschützte 18650 verwenden, Firmware-Abschaltung testen (siehe [005](decisions/005-versorgung.md)) |

Multiplexfrequenz: Die Stellen-Umschaltfrequenz soll kein ganzzahliger Teiler von 77 500 Hz sein. Sonst fällt eine Oberwelle genau auf die DCF-Frequenz. Beispiel: Bei 1 kHz liegen die Oberwellen bei 77 000 und 78 000 Hz, jeweils 500 Hz neben dem Signal. Zu vermeiden sind etwa 500 Hz, 250 Hz und 100 Hz.

## 8. Firmware-Werkzeuge (nach Freigabe)

Mit dem ATmega328PB kommen hinzu: `avr-gcc`, `avr-libc`, `avrdude` und ein ISP-Programmer (z. B. USBasp, ca. 5 €). Alternativ läuft das als Arduino-Nano „Arduino as ISP“. Die Installation folgt erst nach der Freigabe dieser Phase.
