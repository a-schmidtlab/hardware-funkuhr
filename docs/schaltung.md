# Schaltung Rev. A (Phase 3)

- Stand: freigegeben (2026-10-04)
- Quelle: `hw/*.py` (SKiDL). Bauen mit `make` in `hw/`.
- Erzeugt: [Stückliste](stueckliste.md), [Pinbelegung](schaltung-pinbelegung.md), dazu in `hw/build/` Netzliste, KiCad-Schaltplan und PDF (nicht in git)

## Aufbau des Codes

| Datei | Inhalt |
|---|---|
| `hw/bauteile.py` | Bauteilkatalog: jedes Bauteil einmal mit Symbol, Footprint, Hersteller, Teilenummer, LCSC-Nummer |
| `hw/versorgung.py` | Block 1: Akku, Verpolschutz/Akkutrennung, USB-C-Option, 3,3-V-Regler |
| `hw/mcu.py` | Block 2: ATmega328PB, Abblockkondensatoren, Reset, ISP- und UART-Stecker, Pinzuordnung |
| `hw/rtc.py` | Block 3: DS3231 mit Knopfzelle und I²C-Pull-ups |
| `hw/dcf.py` | Block 4: Anschluss DCF77-Modul |
| `hw/anzeige.py` | Block 5: 6 Ziffern, Doppelpunkte, Status-LED, Vorwiderstände, Stellentreiber |
| `hw/bedienung.py` | Block 6: 3 Taster, 6 Testpunkte |
| `hw/funkuhr.py` | verbindet die Blöcke, prüft (ERC) und erzeugt alle Ausgaben |
| `hw/lib/` | selbst erstelltes Symbol und Footprint der Anzeige SC08-11SURKWA |

Jede Blockdatei beginnt mit einer Skizze und den Datenblattwerten. Die Rechnungen stehen als Python-Code mit `assert` darin. `make` bricht ab, sobald eine Grenze verletzt ist.

## Blöcke in Kürze

### 1. Versorgung

- **Q1 (AO3401A)** ist Verpolschutz und Akkutrennung zugleich. Ohne 5 V zieht R1 (10 kΩ) das Gate auf Masse, Q1 leitet. Liegen 5 V an V5_EXT, sperrt Q1.
- **D1 (BAT54)** speist V5_EXT nach VSYS. V5_EXT kommt von der USB-C-Buchse (optional) oder vom Programmer ([Entscheidung 008](decisions/008-programmierstecker-an-v5-ext.md)).
- **U1 (XC6206, 3,3 V)** versorgt nur das DCF-Modul.
- **Rechnung:** Der Sperrstrom von D1 hebt das Gate um höchstens 20 mV an. Q1 bleibt also auch bei leerem Akku voll durchgeschaltet.

### 2. Mikrocontroller

- **Pinbelegung:** wie im Pin-Budget der Architektur. Die vollständige Tabelle steht in [schaltung-pinbelegung.md](schaltung-pinbelegung.md) (U2).
- **Abblockkondensatoren:** je 100 nF an VCC und AVCC, 10 µF Puffer, 100 nF an AREF.
- **Takt:** Werkseinstellung (interner RC-Oszillator, 1 MHz). Deshalb kein Quarz, und PB6/PB7 sind frei für die Anzeige.
- **UART-Leitungen** haben 1-kΩ-Schutzwiderstände. DTR geht über 100 nF auf RESET, für einen späteren Bootloader.

### 3. Zeitbasis

- **DS3231SN:** Pins 5–12 auf Masse, wie das Datenblatt es verlangt. 100 nF an VCC, CR2032 direkt an VBAT.
- **Pull-ups:** 4,7 kΩ an SDA/SCL, 10 kΩ an INT/SQW. 32kHz und RST bleiben offen (laut Datenblatt zulässig).

### 4. DCF77-Empfänger

- **Stiftleiste J4:** 1 = 3,3 V, 2 = GND, 3 = OUT, 4 = EN. Das Modul kommt per Draht an J4.
- **Abschalten:** EN schaltet das Modul in den Stromsparmodus. Die Firmware darf EN nur auf Low ziehen oder hochohmig lassen. Ein 1-kΩ-Schutzwiderstand begrenzt den Strom, falls sie EN doch auf High treibt.

### 5. Anzeige

- **Segmentleitungen:** 8 Stück mit je 270 Ω, gemeinsam für alle Stellen.
- **Stellentreiber:** 7 N-MOSFETs (AO3400A), je mit 100-kΩ-Pull-down. So bleibt die Anzeige während Reset und Programmieren dunkel.
- **Stelle 7:** Statt einer Ziffer hängen dort die 4 Doppelpunkt-LEDs (Segmente a–d) und die Status-LED (Segment e).
- **Ströme (Spitze):** 3,8 mA bei 3,0 V, 7,3 mA bei 4,2 V, 9,6 mA bei 5-V-Betrieb. Mittelwert je Segment bei voller Helligkeit und leerem Akku: 0,48–0,54 mA, Ziel sind 0,3 mA.
- **Grenzwerte:** Alle Grenzen aus dem Datenblatt werden eingehalten (Pinstrom, Summenstrom der Portgruppen, Verlustleistung). Die genauen Rechnungen stehen in `hw/anzeige.py`.

### 6. Taster und Testpunkte

- **Taster:** schalten über 1 kΩ gegen Masse. Die Pins sind zugleich die ISP-Leitungen, der Widerstand schützt den Programmer, falls beim Programmieren ein Taster gedrückt ist.
- **Testpunkte:** VSYS, 3V3_DCF, DCF_OUT, RTC_SQW, RESERVE (PE3), GND.

## Prüfergebnisse

| Prüfung | Ergebnis |
|---|---|
| Rechnungen (`assert` in allen Blöcken) | alle erfüllt |
| SKiDL-ERC | 0 Fehler, 1 Warnung (INT/SQW: Open-Drain an MCU-Eingang, gewollt) |
| KiCad-ERC | 0 Fehler; 125 Warnungen, nur aus der automatischen Zeichnung: Symbol-Kopie weicht von der Bibliothek ab (82), Pin nicht im Raster (43) |
| KiCad-MCP: ERC | bestanden |
| KiCad-MCP: offene Pins | genau die 10 gewollt freien Pins |
| Platinendatei aus Netzliste (`make pcb`) | alle 79 Footprints gefunden, Anzeigenpins wie im Datenblatt |
| Wiederholbarkeit | zwei Läufe ergeben dieselbe Netzliste |

## Bekannte Grenzen und offene Punkte

1. **Automatischer Schaltplan schwer lesbar:** Er ist elektrisch korrekt, aber Bauteile und Beschriftungen überlappen sich. Für die Prüfung sind die Pintabellen und die Blockdateien maßgeblich. In KiCad lässt er sich von Hand ordnen.
2. **Polung des Knopfzellenhalters:** Plus an Pad 1 ist die KiCad-Konvention. Das Datenblatt des Halters war nicht abrufbar, deshalb wird das in Phase 6 am echten Bauteil geprüft.
3. **Footprint der Anzeige ist selbst erstellt** (nach Datenblatt-Zeichnung). Er wird in Phase 6 mit dem 1:1-Papierausdruck geprüft. Der Bildexport von Footprints mit `kicad-cli` funktioniert auf diesem System generell nicht.
4. **Helligkeit im ungünstigsten Fall:** Kommen schwächste LED, ungünstigster MCU-Pin und leerer Akku zusammen, sind es 0,26 mA statt 0,3 mA. Das wird im Prototyp geprüft (Phase 5). *Geklärt in Phase 4:* Die Simulation mit Datenblatt-Kennlinie ergibt 0,32 mA, siehe [sim/ergebnisse.md](../sim/ergebnisse.md).
5. **Belegung am DCF-Modul selbst** ist nicht dokumentiert. Die Verdrahtung legen wir in Phase 5 am echten Modul fest.
6. **5-V-Betrieb mit Last:** Bei hohem Strom fällt an D1 bis ca. 1 V ab. VSYS kann dann kurz unter die Akkuspannung sinken, und der Akku liefert über die interne Diode von Q1 mit. Laden ist dabei ausgeschlossen. Das prüft Phase 4. *Geklärt in Phase 4:* In keinem Fall fließt Ladestrom, siehe [sim/ergebnisse.md](../sim/ergebnisse.md), Abschnitt 2.
7. **Halter 18650:** Keystone 1042. Es gibt auch die Variante 1042P mit mechanischem Verpolschutz. Das lässt sich in Phase 7 bei der Bestellung entscheiden, der Footprint ist derselbe.
8. **Interner Fehler im Schaltplanzeichner von SKiDL 2.3:** Er scheitert gelegentlich mit einem internen Fehler. `funkuhr.py` versucht es dann mit anderem Startwert erneut. Netzliste und Dokumente betrifft das nicht.

## Prüfliste fürs Gate (Workflow Phase 3)

1. **Polaritäten:** Q1 (D am Akku-Plus, S an VSYS), D1 (Anode an V5_EXT), alle LEDs (Anode an Segmentleitung), Akkuhalter BT1, Knopfzelle BT2 (siehe offener Punkt 2).
2. **Pinbelegungen gegen Datenblatt:** U2 (ATmega328PB), U3 (DS3231), U1 (XC6206), DS1 (Anzeige), J2 (ISP), J3 (UART). Siehe [schaltung-pinbelegung.md](schaltung-pinbelegung.md).
3. **Versorgung jedes ICs:** U1 an VSYS, U2 VCC/AVCC an VSYS, U3 VCC an VSYS und VBAT an V_BACKUP, DCF-Modul an 3V3_DCF.
4. **Abblockkondensatoren:** U2 (C an VCC, AVCC, AREF, dazu 10 µF), U3 (100 nF), U1 (je 1 µF Ein- und Ausgang), DCF-Modul (10 µF + 100 nF).
5. **Stückliste:** Bestellnummern und Bestückungsoption, siehe [stueckliste.md](stueckliste.md).
