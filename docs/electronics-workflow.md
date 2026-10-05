# Electronics Workflow: Schaltungsentwurf bis Fertigung mit Claude Code

- Version: 1.0 (2026-10-05)
- Herkunft: weiterentwickelt aus dem Workflow des Projekts „Hardware-Funkuhr“ ([workflow.md](workflow.md)) und dessen Erkenntnissen ([erkenntnisse.md](erkenntnisse.md))
- Geltungsbereich: Leiterplattenprojekte vom Einzelstück bis zur Kleinserie, z. B. Mikrocontroller-Geräte, Sensorik, Analog- und Audioschaltungen, Stromversorgungen, Funk, Akku-Geräte. Hinweise für besondere Projektarten stehen in Abschnitt 8.

Das Dokument ist projektunabhängig. Es wird zu Projektbeginn nach `docs/` kopiert und bei Bedarf angepasst. Abweichungen hält das Entscheidungslog fest.

---

## 1. Grundsätze

1. **Schaltung als Code.** Die Schaltung wird als Text beschrieben (z. B. Python mit SKiDL), nicht im Schaltplan-Editor gezeichnet. Sie liegt in git, ist diffbar und lässt sich reviewen. Rechnungen stehen direkt neben den Bauteilen.
2. **Gates.** Jede Phase endet mit einer Prüfliste und einer ausdrücklichen Freigabe durch den Menschen. Ohne Freigabe beginnt keine neue Phase.
3. **Datenblatt zuerst.** Kein Kennwert, keine Pinbelegung und keine Bestellnummer aus dem Gedächtnis. Jede Rechnung nennt ihre Quelle (Datenblatt, Seite oder Tabelle).
4. **Prüfungen sind ausführbar.** Grenzwerte stehen als `assert` im Code, Simulationen und Tests laufen per `make` und brechen bei Verletzung ab.
5. **Entscheidungslog.** Jede relevante Entscheidung mit Optionen, Begründung und Konsequenzen (Vorlage in Abschnitt 10).
6. **Erzeugen statt abschreiben.** Stückliste, Pintabellen und Prüfberichte entstehen aus dem Code. Handgepflegte Kopien veralten.
7. **Reproduzierbar.** Versionen festschreiben, Zufall festlegen (Seeds, Hash-Reihenfolge). Zwei Läufe müssen dasselbe Ergebnis liefern.
8. **Lokale, offene Werkzeuge.** Kein Werkzeug, das für Kernfunktionen ein Konto oder einen Cloud-Dienst verlangt (Abschnitt 3).
9. **Sicherheit vor Funktion.** Gefährliche Zustände wie Laden eines Akkus ohne Laderegler, Verpolung, Netzspannung oder Überhitzung werden ausdrücklich betrachtet, gerechnet und, wo möglich, simuliert.
10. **Bezahlen bleibt manuell.** Automatisierung reicht bis zum Warenkorb bzw. Upload.

## 2. Rollen

| Rolle | Aufgaben |
|---|---|
| **Mensch** (Projektverantwortlicher) | Anforderungen, Randbedingungen, Review, Freigaben, Bestellung und Bezahlung, Aufbau, Messungen am echten Gerät |
| **Claude Code** | Recherche (Datenblätter, Verfügbarkeit), Entwurf, Berechnung, Schaltungscode, Simulation, Firmware und Tests, Dokumentation, Exporte, Prüflisten |
| **Prüfwerkzeuge** (ERC/DRC, KiCad-MCP, Simulator, Testläufe) | unabhängige Kontrolle; sie zeichnen und entwerfen nicht |

Arbeitsweise mit Claude Code:

- Pro Sitzung zuerst `CLAUDE.md`, Workflow, Lastenheft und den Phasenstand im README lesen.
- Braucht etwas Administratorrechte (`sudo`), legt Claude den fertigen Befehl vor. Der Mensch führt ihn aus.
- Commit und Push nur nach Freigabe. Commit-Nachrichten in der Projektsprache.
- Bei unerwarteten Problemen, z. B. einem Werkzeug, das nicht wie geplant funktioniert, stoppt Claude und legt Optionen mit Empfehlung vor, statt still umzuplanen.

## 3. Werkzeugkette

### Auswahlkriterien

Ein Werkzeug kommt nur in die Kette, wenn es

- lokal läuft und für seine Kernfunktion kein Konto oder keinen Server braucht,
- textbasierte, versionierbare Dateien erzeugt,
- eine offene Lizenz hat und sich in der Version festschreiben lässt,
- **vor Projektstart praktisch getestet wurde** (Phase 0).

### Empfohlene Werkzeuge (Stand 2026)

| Zweck | Werkzeug | Bemerkung |
|---|---|---|
| Schaltung als Code | SKiDL (Python) | erzeugt Netzliste und KiCad-Schaltplan; Eigenheiten siehe Abschnitt 9 |
| Bibliotheken | KiCad-Standardbibliothek + Projektbibliothek `hw/lib/` | fehlende Teile per Skript aus der Datenblatt-Zeichnung |
| Layout, ERC/DRC, Export | KiCad (aktuelle Hauptversion) | `kicad-cli` für alles Automatisierbare |
| Netzliste → erste Platine | `kinet2pcb` oder KiCad „Platine aus Schaltplan aktualisieren“ | Folgeänderungen ins bestehende Layout über KiCad |
| Routing | Freerouting (headless) | kritische Leitungen von Hand |
| Prüfung durch Claude | KiCad-MCP-Server | Netze, ERC/DRC, BOM, nur lesend |
| Analogsimulation | ngspice, gesteuert per Python | eigene Modelle aus Datenblattwerten mit Modellprüfung |
| Firmware | Hersteller-Toolchain (z. B. avr-gcc, arm-none-eabi-gcc) + Make; Device Packs des Herstellers bei Bedarf | Host-Tests mit gcc und Sanitizern |
| Versionierung | git + GitHub/GitLab | |

**Gegenbeispiel:** atopile war geplant, verlangte aber ab 0.15.8 eine Anmeldung für die Bauteilauswahl, und der Nachfolger läuft im Browser. Solche Wechsel des Geschäftsmodells sind bei jungen Werkzeugen jederzeit möglich. Deshalb gibt es Phase 0, und alle Versionen werden festgeschrieben.

## 4. Repo-Struktur

```text
projekt/
├── CLAUDE.md                # Zusammenarbeit, Regeln, Werkzeugpfade (für Claude Code)
├── README.md                # Kurzbeschreibung + Phasentabelle (wird je Phase aktualisiert)
├── docs/
│   ├── electronics-workflow.md   # dieses Dokument (Kopie, ggf. angepasst)
│   ├── setup.md             # Installation, Versionen, bekannte Werkzeugfehler
│   ├── lastenheft.md        # versioniert, mit Änderungstabelle
│   ├── architektur.md       # Blockschaltbild, Spannungen, Pin-/Strom-/Kostenbudget
│   ├── schaltung.md         # Blöcke, Prüfergebnisse, offene Punkte, Gate-Prüfliste
│   ├── stueckliste.md       # ERZEUGT
│   ├── schaltung-pinbelegung.md  # ERZEUGT
│   ├── erkenntnisse.md      # Learnings, Projektstand, Wiederaufnahme
│   └── decisions/NNN-titel.md
├── hw/                      # Schaltung als Code
│   ├── requirements.txt     # festgeschriebene Versionen
│   ├── Makefile             # make → Netzliste, Schaltplan, ERC, PDF, Dokumente
│   ├── bauteile.py          # Bauteilkatalog (Symbol, Footprint, MPN, Bestellnummer)
│   ├── <block>.py           # ein Modul je Funktionsblock, mit Rechnungen als assert
│   ├── <projekt>.py         # Gesamtschaltung, Ausgaben
│   ├── lib/                 # eigene Symbole/Footprints
│   ├── fp-lib-table, sym-lib-table
│   └── build/               # erzeugt, nicht in git
├── sim/                     # Simulationen (Skript, Modelle, Ergebnisse als Markdown)
├── fw/                      # Firmware: src/, tests/, Makefile (test + Zielplattform)
└── fab/rev-x/               # Fertigungsdaten und Bestellunterlagen je Revision
```

## 5. Phasen

Für jede Phase gilt: **Inhalt → Ergebnisse → Prüfung → Gate**. Typische Fallstricke stehen dabei, damit man sie vorher kennt.

### Phase 0: Einrichtung und Werkzeugprobe

- **Inhalt:** Werkzeuge installieren, Versionen festschreiben (`setup.md`). Dann ein **Probelauf der ganzen Kette** mit einer Mini-Schaltung: Ziel-MCU oder Haupt-IC, ein Widerstand, ein Kondensator → Netzliste → Schaltplan → ERC → Platinendatei → Firmware „Hallo Welt“ übersetzen.
- **Ergebnisse:** `setup.md`, `CLAUDE.md`, Repo-Gerüst.
- **Gate:** Die Kette läuft ohne Konto und ohne Cloud, und bekannte Werkzeugfehler sind notiert.
- **Fallstricke:** Werkzeug verlangt Anmeldung; Simulator oder KiCad-Python nur in einer bestimmten Python-Version; Compiler kennt den Chip nicht (Device Pack nötig); globale KiCad-Bibliothekstabellen fehlen (Projekttabellen anlegen).

### Phase 1: Lastenheft

- **Inhalt:** Zweck, Funktionen, Versorgung, Bedienung, Anzeige/Schnittstellen, Umgebung, Mechanik, Sicherheit, Fertigung, Beschaffung, Budget, Nicht-Ziele. Jede Anforderung bekommt eine ID und eine Priorität (muss / soll / kann / nein). Bekannte Zielkonflikte als Tabelle mit Optionen, z. B. Anzeige gegen Akkulaufzeit.
- **Fertigungsvariante festlegen** (Abschnitt 6).
- **Ergebnisse:** `docs/lastenheft.md` mit Version und Änderungstabelle.
- **Gate:** Freigabe des Lastenhefts. **Spätere Änderungen** heben die Version an und brauchen eine erneute Freigabe.
- **Fallstricke:** grobe Schätzungen wie Laufzeit oder Strom ohne Hinweis „Verifikation in Phase 4“; „nein“-Anforderungen vergessen, obwohl sie Folgen haben, z. B. kein Zellschutz → Tiefentladung muss anders gelöst werden.

### Phase 2: Architektur

- **Inhalt:**
  - Blockschaltbild
  - Hauptkomponenten mit Datenblatt-Kernwerten
  - Spannungsebenen, auch alle optionalen Versorgungen
  - Pin-Budget mit Reserve
  - Strombudget und Laufzeit
  - Kostenschätzung
  - Risiken für den Prototyp
- **Recherche je Hauptkomponente:**
  - Datenblatt: Versorgung, Grenzwerte, Pakete
  - Verfügbarkeit bei mindestens einem API-fähigen Händler
  - Preis
  - Fälschungsrisiko (nur autorisierte Händler)
- **Ergebnisse:** `docs/architektur.md`, Entscheidungen je Hauptkomponente.
- **Gate:** Der Mensch versteht und akzeptiert jede Hauptkomponente einschließlich der Kernwerte.
- **Fallstricke:**
  - Bauteil nicht lieferbar
  - Pegel zwischen Spannungsdomänen nur für den Normalfall geprüft
  - LED- oder Treiberspannung passt nicht zum ganzen Versorgungsbereich
  - Taktgenauigkeit (RC-Oszillator) für zeitkritische Aufgaben überschätzt

### Phase 3: Schaltung (als Code)

- **Inhalt:**
  - **Bauteilkatalog:** Jedes Bauteil genau einmal mit Symbol, Footprint, Hersteller, MPN und Bestellnummer.
  - **Ein Modul je Funktionsblock:** Kopfkommentar mit Skizze und Datenblattwerten, danach die Rechnungen mit Quelle und `assert`.
  - **Gesamtschaltung:** verbindet die Blöcke und erzeugt Netzliste, Schaltplan, Stückliste und Pintabellen.
  - **Feste Bauteilkennungen:** stabile Tags für die spätere Zuordnung zum Layout.
  - **Sprechende Netznamen:** auch für alle Hilfsnetze.
- **Prüfung:**
  - ERC im Schaltungswerkzeug
  - ERC in KiCad
  - KiCad-MCP: ERC und unbeschaltete Pins
  - Gegenprobe Platinendatei: alle Footprints gefunden, Pads am richtigen Netz
  - Wiederholbarkeit: zwei Läufe, gleiche Netzliste
  - Bestellnummern automatisch gegen die Händlerseite abgleichen
- **Ergebnisse:** `hw/`, `docs/schaltung.md` (Blöcke, Prüfergebnisse, offene Punkte, Gate-Prüfliste), erzeugte Stückliste und Pintabellen.
- **Gate (Mindestprüfung durch den Menschen):**
  - Polaritäten: Dioden, Transistoren, Elkos, Batteriehalter, Stecker
  - Pinbelegungen gegen das Datenblatt
  - Versorgung jedes ICs
  - Abblockkondensatoren
  - Schutzbeschaltung: Verpolung, Stecker, Programmer
  - Stückliste mit Bestückungsoptionen
- **Fallstricke:**
  - Bauteile, die eine „Option“ mitversorgen, aber selbst als optional markiert sind
  - Programmer- oder Debug-VCC, das einen Akku laden kann
  - Taster auf Programmierpins ohne Serienwiderstand
  - unbeschaltete Pins, die laut Datenblatt auf Masse müssen

### Phase 4: Simulation und Host-Tests

- **Analog (ngspice):**
  - Bauteilmodelle aus Datenblattwerten, mit Modellprüfung gegen Datenblattpunkte
  - Ecken: Toleranzen × Versorgung × Last × Temperatur bzw. Schwellspannung
  - Sicherheitsfälle: Verpolung, alle Kombinationen von Versorgungsquellen, Kurzschluss, Anlauf
  - Welligkeit und Spektrum, wo Funk oder empfindliche Analogteile betroffen sind
  - Strombudget und Laufzeit
- **Firmware (Host-Tests):**
  - Protokolle und Algorithmen mit Signalgenerator und Störmodellen
  - Monte-Carlo-Läufe
  - Sonderfälle: Grenzen, Überläufe, Kalender
  - Prüfung von Inhalt *und* Zeitpunkt
  - Übersetzung für die Zielplattform mit strengen Warnungen
- **Nicht simulierbar:** Funkempfang, EMV, Wärme im Gehäuse, Mechanik. Das prüft Phase 5.
- **Ergebnisse:** `sim/` mit Skript, Modellen und erzeugten Ergebnissen, `fw/` mit Tests. Dazu eine Zusammenfassung mit Abgleich gegen das Lastenheft und einer Liste „was erst der Prototyp klären kann“.
- **Gate:** Die Ergebnisse erfüllen das Lastenheft, und die Störmodelle sind aus Sicht des Menschen realistisch.
- **Fallstricke:**
  - Modelle unklarer Herkunft
  - nur Nennwerte simuliert
  - Firmware-Test prüft nur Erfolgsfälle
  - Parameter nach Gefühl statt per Variantenvergleich gewählt

### Phase 5: Prototyp

- **Aufbau:** Steckbrett oder Lochraster mit Modulen und Breakouts statt einzelner SMD-Teile.
- **Ziel:** die Risiken prüfen, die nicht simulierbar sind:
  - Empfang und EMV neben Störquellen
  - echte Stromaufnahme
  - Lesbarkeit und Bedienbarkeit
  - Pegel und Polarität fremder Module
  - Erwärmung
- **Messplan vorab:** Was wird gemessen, womit, und was ist das Kriterium?
- **Signale aufzeichnen** und als Testfälle in die Host-Tests übernehmen.
- **Gate:** Die Erkenntnisse sind in Schaltung, Firmware und Entscheidungslog eingeflossen.

### Phase 6: Layout

- **Randbedingungen vom Menschen:**
  - Platinenmaße und Bohrungen
  - Lage der Bedienelemente und Stecker
  - Abstände zu Störquellen, z. B. Antenne zur Anzeige oder zum Schaltregler
  - Gehäusebezug
- **Platzierung durch Claude, visuelle Prüfung durch den Menschen.**
- **Routing:** kritische Leitungen von Hand bzw. vorgegeben (Versorgung, Takt, Analog, Funk, hohe Ströme), den Rest per Freerouting. Massefläche, Rückstrompfade beachten.
- **Prüfung:**
  - DRC mit den Regeln des Herstellers
  - MCP-Review
  - 3D-Ansicht
  - **Ausdruck 1:1 mit aufgelegten Bauteilen**, vor allem bei selbst erstellten Footprints
- **Gate:** DRC fehlerfrei, die Papierprobe passt, und die offenen Punkte aus Phase 3 sind abgearbeitet.

### Phase 7: Fertigung

- **Export:** Gerber, Bohrdaten, Stückliste; bei PCBA zusätzlich Bestückungsdaten (CPL).
- **Platine:** Upload beim Hersteller (z. B. Aisler, JLCPCB, PCBWay) und dessen Gerber-Vorschau prüfen.
- **Bauteile:** Stückliste → Warenkorb (LCSC, Mouser, DigiKey, Reichelt). Reserve für Kleinteile, Mindestbestellmengen und Versandkostengrenzen beachten.
- **Gate:** Der Mensch prüft Vorschau und Warenkorb und bezahlt selbst. Die Unterlagen kommen nach `fab/rev-x/`.

### Phase 8: Inbetriebnahme und Rückblick

- **Reihenfolge:**
  1. Sichtprüfung
  2. Widerstand der Versorgung gegen Masse
  3. Versorgung ohne ICs bzw. mit Strombegrenzung am Labornetzteil
  4. Firmware flashen
  5. Funktionstest gegen das Lastenheft
  6. Messung von Strom und Laufzeit
- **Rückblick:** Fehler, Abweichungen, Änderungen für die nächste Revision. Ein Issue pro Punkt, dazu ein Nachtrag in `erkenntnisse.md`.

## 6. Fertigungsvarianten

| Variante | Bauteile | Bestückung |
|---|---|---|
| **Handlötbar** | THT oder SMD ≥ 0805; ICs in SOIC, SOT-23, TSSOP, (T)QFP mit ≥ 0,65 mm Pitch; kein QFN, BGA oder Pads unter dem Gehäuse | selbst |
| **Fertigungsbestückt (PCBA)** | beliebig, bevorzugt aus dem Standardkatalog des Bestückers (z. B. JLC „Basic Parts“) | Fertiger |

Empfehlung: Rev. A handlötbar, aber schon mit Teilen, die der Bestücker führt. Dann ist der Wechsel auf PCBA bei Rev. B nur ein Export.

## 7. Querschnittsthemen

### 7.1 Datenblätter und Bauteile

- Datenblatt vom Hersteller oder einem großen Händler laden und die verwendeten Werte mit Seite oder Tabelle zitieren. PDFs mit `pdftotext -layout` durchsuchen, Zeichnungen mit `pdftoppm` als Bild ansehen.
- Für Rechnungen **Garantiewerte (min./max.)** verwenden, typische Werte nur für die Erwartung.
- Bestellnummern automatisch prüfen: Der Seitentitel der Händlerseite muss die MPN enthalten.
- Verfügbarkeit und Fälschungsrisiko prüfen: nur autorisierte Händler, bei kritischen ICs keine Marktplätze.
- Fehlende Symbole und Footprints per Skript aus dem Datenblatt erzeugen, in `hw/lib/` ablegen und in Phase 6 per Papierausdruck prüfen.

### 7.2 Versorgung und Sicherheit

- **Alle Versorgungskombinationen auflisten:** Batterie bzw. Akku, extern, USB, Programmer, Debug-Adapter, verpolt, teilweise gesteckt. Für jede prüfen: Wohin fließt Strom? Wird ein Akku geladen? Bleiben Pegel gültig?
- **Li-Ion:**
  - nie ungeregelt laden
  - Tiefentladung verhindern, durch geschützte Zellen oder Abschaltung
  - Verpolschutz
  - Halter für die tatsächliche Zellenlänge wählen (geschützte Zellen sind länger)
- **Verpolschutz:** Ein P-MOSFET als „ideale Diode“ verliert kaum Spannung. Er kann zugleich die Akkutrennung bei externer Versorgung übernehmen. Leckströme am Gate nachrechnen.
- **Netzspannung:** nur mit eigenem Sicherheitskonzept (Abschnitt 8), sonst fertige, zugelassene Netzteile verwenden.

### 7.3 EMV, Funk und empfindliche Analogteile

- Störquellen (Multiplexen, Schaltregler, Takte) räumlich und frequenzmäßig von Empfängern trennen. Schaltfrequenzen so wählen, dass keine Oberwelle auf die Nutzfrequenz fällt.
- Empfindliche Teile über einen eigenen Regler oder ein Filter versorgen. Die Störunterdrückung (PSRR) bei der relevanten Frequenz beachten, Datenblätter nennen oft nur 1 kHz.
- Welligkeit und Spektrum simulieren. Kopplung über Felder kann nur der Prototyp zeigen.

### 7.4 Mikrocontroller-Grundausstattung

- Abblockkondensatoren an jedem Versorgungspin, dazu ein Puffer, AREF bzw. VREF nach Datenblatt.
- Reset: Pull-up nach Application Note des Herstellers; Programmierschnittstelle (ISP, SWD, UPDI) als Stecker.
- Debug-UART mit Serienwiderständen bei möglichen Pegelunterschieden.
- Pins, die mit der Programmierschnittstelle geteilt werden, mit Serienwiderständen schützen.
- Treiber-Gates mit Pull-down, damit während Reset und Programmieren nichts schaltet.
- Testpunkte für Versorgungen und wichtige Signale.
- Pin-Budget mit mindestens einem Reservepin.

### 7.5 Firmware-Architektur für Testbarkeit

- Hardwareunabhängige Module (Protokolle, Rechenlogik, Zustandsautomaten) ohne Registerzugriffe schreiben. Sie bekommen Zeit und Eingänge als Parameter, z. B. `tick(pegel)`.
- Host-Tests mit Sanitizern; dieselben Module mit dem Zielcompiler und strengen Warnungen übersetzen, z. B. `-Wconversion` für 8-Bit-Ziele.
- Bei sicherheits- oder genauigkeitskritischen Ausgaben ein hartes Kriterium festlegen („nie falsch“) und getrennt davon die Leistung optimieren („so oft wie möglich“).

## 8. Anpassung an Projektarten

| Projektart | Zusätzlich beachten |
|---|---|
| **Akku- und Batteriegeräte** | Strombudget mit Schlafzuständen, Laufzeit in Phase 4, Tiefentladung, Laden nur mit Laderegler, Verhalten beim Batteriewechsel (Gangreserve) |
| **Netzbetriebene Geräte** | Netzteil möglichst als zugelassenes Fertigmodul. Bei eigener Netzschaltung: Luft- und Kriechstrecken, Isolationskoordination, Sicherung, Schutzklasse, Prüfung nach Norm. Das gehört nicht in ein Lernprojekt ohne Fachaufsicht. |
| **Stromversorgungen und Leistung** | Verlustleistung und Wärme (thermischer Widerstand), Stromdichte der Leiterbahnen, Schaltregler-Layout nach Herstellerempfehlung, Anlauf und Kurzschluss simulieren, Regelstabilität (AC-Analyse) |
| **Analog und Audio** | Rauschen, Masseführung, Toleranzecken und Monte-Carlo in ngspice, Frequenzgang (AC), Versorgungsfilter |
| **Funk (RF)** | fertige, zertifizierte Module bevorzugen, Antennenabstand und Freiflächen nach Modul-Datenblatt, impedanzkontrollierte Leitungen beim Hersteller anfragen; Simulation ersetzt keine Messung |
| **Schnelle Digitaltechnik** (USB, Speicher, > 50 MHz) | Lagenaufbau, Impedanzen und Längenabgleich nach Herstellerregeln, meist 4 Lagen; Freerouting ungeeignet, von Hand routen |
| **Sensorik und Messtechnik** | Referenzspannung, Kalibrierkonzept, Temperaturdrift, Testpunkte für Abgleich |
| **Zeit- und Taktgenauigkeit** | Fehlerbudget in ppm (1 s/Tag = 11,6 ppm), Temperaturverhalten; TCXO bzw. RTC statt RC-Oszillator |
| **Serien ab ca. 50 Stück** | PCBA, Bauteile aus dem Standardkatalog des Bestückers, Testadapter bzw. Testpunkte für die Prüfung in der Fertigung, Programmierung in der Fertigung |

## 9. Werkzeugspezifische Hinweise

### SKiDL (Stand 2.3, 2026-10)

- `NC` und `default_circuit` stellt SKiDL beim Import global bereit, sie sind nicht importierbar.
- **Jedes Bauteil mit `tag`**, sonst entstehen bei jedem Lauf neue Kennungen, und das Layout verliert die Zuordnung.
- Schaltplan: `generate_schematic(auto_stub=True, seed=…)`. Bei sporadischen internen Fehlern mit anderem Seed wiederholen. Der Schaltplan ist eine Ansichtshilfe, maßgeblich sind Netzliste und Pintabellen.
- `PYTHONHASHSEED=0` setzen, sonst ist die Ausgabe nicht wiederholbar.
- PWR_FLAG erst *nach* `generate_netlist()` hinzufügen, nur für die KiCad-ERC des Schaltplans.
- Für KiCad-ERC und Ansicht im Build-Ordner eine Projektdatei und Bibliothekstabellen anlegen, mit angepasstem `${KIPRJMOD}`.
- Hilfsnetze ausdrücklich benennen, statt `&`-Ketten mit automatischen Namen.
- `kinet2pcb` übernimmt eigene Felder (z. B. Bestellnummer) nicht. Die Stückliste deshalb aus dem Code erzeugen.
- KiCads `pcbnew` gibt es nur im System-Python. Die Python-Umgebung deshalb mit `--system-site-packages` anlegen.

### KiCad-Kommandozeile

- `kicad-cli sch erc`, `sch export pdf`, `pcb drc`, `pcb export gerbers/drill/pos`. Alles im Makefile.
- Bekannte Ausfälle der jeweiligen Version in `setup.md` notieren (Beispiel: `fp export svg` scheiterte durchgehend).

### ngspice

- Steuerung per Python: Netzliste schreiben, `ngspice -b` aufrufen, Werte aus `print` bzw. `meas` lesen, Prüfungen in Python.
- Modelle: Diode (IS, N, RS) und MOSFET Level 1 (VTO, KP, RD) aus zwei bis drei Datenblattpunkten anpassen und die Modellprüfung mitlaufen lassen.

## 10. Vorlagen

### 10.1 Entscheidungslog (`docs/decisions/NNN-titel.md`)

```markdown
# NNN – Titel

- Datum:
- Status: vorgeschlagen | akzeptiert | ersetzt durch NNN

## Kontext
Welches Problem, welche Randbedingungen (mit Anforderungs-IDs)?

## Optionen
1. …
2. …

## Entscheidung
Gewählt: …, weil …
Datenblatt-Kernwerte (bei Bauteilentscheidungen): Tabelle

## Konsequenzen
Was folgt daraus, welche Risiken bleiben, was prüft welche Phase?
```

### 10.2 Lastenheft (Gliederung)

1. Zweck
2. Funktionale Anforderungen
3. Anzeige und Schnittstellen
4. Energie
5. Sicherheit
6. Bedienung
7. Mechanik und Umgebung
8. Herstellung und Beschaffung, mit Fertigungsvariante, Bezugsquellen (API-fähig), Budget
9. Offene Punkte und Zielkonflikte, mit Optionstabelle
10. Nicht-Ziele
11. Änderungen (Version, Datum, Änderung)

Jede Anforderung: ID, Text, Priorität (muss / soll / kann / nein).

### 10.3 Gate-Prüfliste (Muster)

```markdown
## Prüfliste fürs Gate (Phase N)
1. <konkreter Prüfschritt mit Verweis auf Datei/Abschnitt>
2. …
Offene Punkte, die bewusst in spätere Phasen gehen: …
Fragen an den Menschen: …
```

### 10.4 Startauftrag an Claude Code

> Lies `CLAUDE.md`, `docs/electronics-workflow.md`, `docs/lastenheft.md` und den Phasenstand im `README.md`. Wir sind in Phase N.
> Arbeite nur diese Phase ab, prüfe jeden Kennwert am Datenblatt, halte Entscheidungen im Entscheidungslog fest und stoppe am Gate mit einer Prüfliste.
> Bei unerwarteten Problemen: stoppen und Optionen mit Empfehlung vorlegen.

### 10.5 `CLAUDE.md` (Mindestinhalt)

- Sprache, Vorkenntnisse des Menschen, Erklärtiefe
- Regeln: `sudo` nur vorlegen, Commit und Push nur nach Freigabe, Bezahlen manuell
- Reihenfolge der Pflichtlektüre (Workflow, Lastenheft, README-Phasenstand)
- Werkzeuge mit Pfaden und Eigenheiten (Verweis auf `setup.md`)
