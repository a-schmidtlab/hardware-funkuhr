# Erkenntnisse und Projektstand

- Stand: 2026-10-05, Projekt nach Phase 4 pausiert
- Der allgemeine Workflow für künftige Projekte, der aus diesen Erkenntnissen entstanden ist: [electronics-workflow.md](electronics-workflow.md)

## 1. Projektstand

| Phase | Stand | Wichtigste Ergebnisse |
|---|---|---|
| 1. Lastenheft | freigegeben (v1.1) | [lastenheft.md](lastenheft.md); E6 (externe 5 V) nachträglich ergänzt |
| 2. Architektur | freigegeben | [architektur.md](architektur.md), Entscheidungen 001–006 |
| 3. Schaltung | freigegeben | `hw/*.py` (SKiDL), [schaltung.md](schaltung.md), [stueckliste.md](stueckliste.md), [schaltung-pinbelegung.md](schaltung-pinbelegung.md), Entscheidungen 007–008 |
| 4. Simulation | freigegeben | [sim/README.md](../sim/README.md), DCF77-Dekoder `fw/src/dcf77.c`, Entscheidung 009 |
| 5. Prototyp | **nächster Schritt** | – |
| 6.–8. | offen | – |

### Wiederaufnahme: so geht es weiter

1. Kurz prüfen, ob alles noch baut:
   - `make` in `hw/` (Netzliste, Schaltplan, ERC)
   - `make` in `sim/` (Analogsimulation)
   - `make test` in `fw/` (Dekoder-Tests)

   Falls ein Paket aktualisiert wurde, die Versionen in `hw/requirements.txt` und [setup.md](setup.md) vergleichen.
2. Phase 5 beginnen: Einkaufsliste für den Steckbrett-Prototyp und ein Messplan. Prüfen soll der Prototyp:
   - Empfang neben der laufenden Anzeige (Abstand, Ausrichtung, mit und ohne Multiplexen)
   - Störungen durch ein echtes USB-Ladegerät
   - Lesbarkeit bei Tag und Nacht, gemessene Stromaufnahme
   - Polarität und Pegel des Modulausgangs (`puls = true` im Dekoder)
   - echte Signalaufzeichnungen als zusätzliche Testfälle für den Dekoder
3. Offene Punkte für Phase 6 aus [schaltung.md](schaltung.md):
   - Polung des Knopfzellenhalters am echten Teil prüfen
   - Footprint der Anzeige per Papierausdruck im Maßstab 1:1 prüfen
4. Typ des vorhandenen ISP-Programmers in [setup.md](setup.md) festhalten. Eventuell ist eine udev-Regel nötig.

## 2. Erkenntnisse zum Workflow

### Werkzeuge

- **Werkzeuge vor der Festlegung praktisch testen.** atopile war im Workflow fest eingeplant. Erst beim Start von Phase 3 zeigte sich, dass die Bauteilauswahl inzwischen eine Anmeldung beim Hersteller verlangt und der Nachfolger nur noch im Browser läuft (Entscheidung 007). Ein Probelauf mit einer Mini-Schaltung (MCU, Widerstand, Kondensator → Netzliste → Platine) gehört deshalb in die Einrichtung vor Phase 1, nicht erst in Phase 3.
- **Auswahlkriterien für Werkzeuge:** läuft lokal, braucht kein Konto, Dateien sind textbasiert und versionierbar, die Lizenz ist offen, die Version lässt sich festschreiben. Start-ups mit Cloud-Geschäftsmodell können Bedingungen jederzeit ändern.
- **SKiDL** (Python) funktioniert gut als „Schaltung als Code“. Es hat aber Eigenheiten, die man kennen muss (Abschnitt 4).
- **Bekannte Fehler einer Werkzeugversion** gehören in die Setup-Doku, z. B. `kicad-cli fp export svg` scheitert auf diesem System bei jedem Footprint.

### Datenblätter und Bestellnummern

- **Kein Wert aus dem Gedächtnis.** Zweimal waren meine Annahmen falsch: der ATmega328PB-Ausgangspegel bei 3 V (2,1 V statt 2,3 V) und die Aufteilung der Portgruppen für den Summenstrom. Beides fiel erst beim Nachlesen auf. Jede Rechnung nennt deshalb die Datenblattstelle.
- **Bestellnummern automatisch prüfen.** LCSC-Produktseiten lassen sich per `curl` abrufen, der Seitentitel enthält die Herstellerteilenummer. Mehrere aus dem Gedächtnis vermutete Nummern existierten nicht oder gehörten zu anderen Teilen.
- **Verfügbarkeit früh prüfen.** Das geplante Pollin-DCF1 war nicht lieferbar. Das CANADUINO-Modul bei DigiKey erfüllt zudem H2 (per API bestellbar).
- **Lücken in der KiCad-Bibliothek** sind normal. Fehlende Symbole und Footprints entstehen per Skript aus der Datenblatt-Zeichnung (`hw/lib/`). Bei baugleichen Varianten das vorhandene Symbol nutzen und die Pingleichheit am Datenblatt belegen (DS3231SN ↔ DS3231M).

### Prüfen

- **Rechnungen als ausführbare Prüfungen.** `assert` im Schaltungscode bricht den Build ab, sobald eine Grenze verletzt ist. Das hat Rechenfehler sofort sichtbar gemacht.
- **Mehrere unabhängige Prüfungen:** SKiDL-ERC, KiCad-ERC, KiCad-MCP und eine Platinendatei als Gegenprobe (alle Footprints gefunden, Pads am richtigen Netz). Jede Prüfung sieht andere Dinge.
- **Erzeugte Dokumente statt Handarbeit:** Stückliste und Pintabellen entstehen aus dem Code und können nicht veralten. Für die Prüfung am Gate sind sie lesbarer als der automatisch gezeichnete Schaltplan.
- **Wiederholbarkeit prüfen:** zwei Läufe, gleiche Netzliste. Erst dann ist ein Diff in git aussagekräftig.

### Simulation

- **Einfache Modelle aus Datenblattwerten** (SPICE Level 1, Standarddiode) mit eigener Modellprüfung sind nachvollziehbarer als fremde Modelle unklarer Herkunft. Toleranzen dürfen einseitig sein: pessimistisch zulässig, optimistisch nur knapp.
- **Ecken statt Nennwerte:** Bauteiltoleranzen, Temperatur bzw. Schwellspannung, Versorgungsbereich und Lastfall kombinieren und das Minimum bzw. Maximum bewerten.
- **Sicherheitsfragen simulieren:** Bei jeder Kombination von Akku, USB und Programmer musste der Ladestrom ≤ 0 sein. Die Tabelle beantwortet das eindeutig.

### Firmware-Tests am PC

- **Signalgenerator plus Störmodelle** (Taktfehler, Jitter, Störimpulse, Ausfälle, Bitfehler, Sonderfälle) und ein Monte-Carlo-Lauf über viele Minuten haben drei echte Fehler gefunden, die ein einzelner sauberer Test nie gezeigt hätte.
- **Nicht nur den Inhalt prüfen, auch den Zeitpunkt.** Ein Fehler (Uhr 0,2 s zu früh gestellt) wurde erst sichtbar, als der Test auch den Zeitpunkt der Meldung bewertete.
- **Sicherheitskriterium vor Trefferquote:** „nie eine falsche Zeit“ ist hart, die Synchronisationsrate wird optimiert. Parameter per Variantenvergleich wählen, nicht per Gefühl.
- **Für das Zielsystem mit übersetzen** (`make avr`, `-Wconversion`), damit Typfehler auf dem 8-Bit-AVR früh auffallen.

### Prozess

- **Gates haben gewirkt.** Jede Phase endete mit einer Prüfliste. Änderungswünsche wie die externe 5-V-Versorgung kamen genau dort an und flossen als neue Lastenheft-Version und Entscheidung ein.
- **Anforderungsänderung = neue Lastenheft-Version** mit Änderungstabelle, dann neue Freigabe.
- **Entscheidungslog** mit Optionen, Begründung und Konsequenzen. Er macht spätere Fragen („warum nicht atopile?“) in einer Minute beantwortbar.
- **Eigene Entwurfsfehler offen benennen:** D1 war zuerst als optional markiert, obwohl die Programmierstecker sie brauchen. Gefunden wurde das beim Durchdenken der Programmer-Fälle.

## 3. Technische Erkenntnisse (wiederverwendbar)

- **LED-Anzeigen am Li-Ion-Akku:** nur Typen mit *einem* LED-Chip pro Segment (U_F ca. 1,8–2 V). Große Ziffern (ab ca. 1 Zoll) haben oft zwei Chips in Reihe und leuchten bei 3,0 V nicht mehr.
- **Helligkeit bei schwankender Akkuspannung:** Vorwiderstand plus PWM-Ausgleich in der Firmware (VCC gegen die interne 1,1-V-Referenz messen, kein Pin nötig).
- **P-MOSFET als Verpolschutz *und* Akkutrennung:** Gate über einen Widerstand an GND und zusätzlich an der externen 5-V-Leitung. Sperrstrom der Einspeisediode × Gatewiderstand nachrechnen.
- **Programmier-/Debugstecker bei Li-Ion-Geräten:** VCC des Programmers *nicht* an die Systemspannung. Ein durchgeschalteter MOSFET leitet in beide Richtungen und würde den Akku laden. Stattdessen an die externe Einspeisung hinter der Trenndiode (Entscheidung 008).
- **Pegel zwischen Spannungsdomänen bei *jeder* möglichen Versorgung prüfen,** nicht nur bei Akkubetrieb. Die 5-V-Option machte aus dem 3,0-V-Regler einen 3,3-V-Regler (High-Schwelle 0,6 × VCC).
- **Multiplexfrequenz bei Funkempfang:** kein ganzzahliger Teiler der Empfangsfrequenz wählen. Bei 1 kHz liegen die Oberwellen 500 Hz neben 77,5 kHz.
- **Taster an ISP-Pins:** Serienwiderstand (1 kΩ), sonst schließt ein gedrückter Taster den Programmerausgang kurz.
- **Gate-Pull-downs an Stellentreibern** halten die Anzeige während Reset und Programmieren dunkel.
- **DCF77-Dekodierung:** Mehrheitsentscheidung in Abtastfenstern statt Flankenmessung. Die Minutenmarke wird gegen das gemessene Sekundenraster geprüft, Meldung erst nach dem bestätigten Bit 0 in Sekunde 0, zwei aufeinanderfolgende Minuten müssen passen.
- **Interner RC-Oszillator des ATmega328PB:** ±2 % bzw. ±3,5 % ab Werk. Für die DCF77-Fenster reicht das. Für die Uhrzeit nicht, dafür ist der DS3231 da.

## 4. Eigenheiten von SKiDL 2.3 (Stand 2026-10)

| Thema | Erkenntnis | Lösung im Projekt |
|---|---|---|
| `NC`, `default_circuit` | nicht importierbar, werden beim Import global bereitgestellt | direkt benutzen, Kommentar im Import |
| Bauteilkennungen | ohne `tag` bei jedem Lauf zufällig, das Layout verliert die Zuordnung | jede Bauteilfunktion verlangt ein `tag` |
| Schaltplanzeichner | scheitert bei großen Schaltungen | `generate_schematic(auto_stub=True)` |
| Schaltplanzeichner | gelegentlich interner `KeyError` | Wiederholung mit anderem `seed` |
| Wiederholbarkeit | Ergebnis hängt von der Hash-Reihenfolge ab | `PYTHONHASHSEED=0` im Makefile |
| PWR_FLAG | ohne Footprint, stört die Netzliste | erst nach `generate_netlist()` hinzufügen, nur für den Schaltplan |
| Bibliotheken | KiCad-ERC findet sie nur mit Projektdatei | `build/funkuhr.kicad_pro` und Bibliothekstabellen ins Build kopieren |
| Hilfsnetze | Ketten mit `&` erzeugen `N$1` … | Netze explizit benennen |
| `kinet2pcb` | übernimmt eigene Felder (LCSC) nicht in die Platine | Stückliste aus Netzliste/Code erzeugen |
| `pcbnew` | nur im System-Python 3.12 verfügbar | venv mit `--system-site-packages` |
| Lesbarkeit | automatischer Schaltplan elektrisch korrekt, aber gedrängt | Prüfung über Pintabellen und Blockdateien |
