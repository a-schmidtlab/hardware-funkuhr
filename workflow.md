# Entwicklungsworkflow Elektronik – Claude Code + atopile + KiCad

Bezugsprojekt: DCF77-Funkuhr. Der Workflow ist projektunabhängig gedacht.

## Grundsätze

- **Schaltung als Code.** Die Schaltung wird in atopile (`.ato`) beschrieben, nicht im Schaltplan-Editor gezeichnet. Sie liegt in git und ist diffbar und reviewbar.
- **Rollen:**
  - **Du:** Anforderungen, Randbedingungen, Review, Freigaben.
  - **Claude Code:** Entwurf, Berechnung, Simulation, Firmware, Exporte.
  - **KiCad-MCP:** Prüfwerkzeug (Netze, ERC/DRC, BOM), kein Zeichenwerkzeug.
- **Gates:** Jede Phase endet mit einer expliziten Freigabe durch dich. Ohne Freigabe geht es nicht in die nächste Phase.
- **Entscheidungslog:** Jede relevante Designentscheidung wird mit Alternativen und Begründung festgehalten (siehe Vorlage unten).
- **Bezahlen bleibt manuell.** Automatisierung reicht bis zum Warenkorb bzw. Upload.

## Fertigungsrandbedingungen

Diese Vorgaben gehören in jedes Lastenheft.

| Variante | Bauteile | Bestückung |
|---|---|---|
| **Handlötbar** | THT oder SMD ≥ 0805, ICs in SOIC/SOT-23/TSSOP mit max. 0,65 mm Pitch; kein QFN, BGA oder Pads unter dem Gehäuse | selbst |
| **Fertigungsbestückt** (PCBA) | beliebig, bevorzugt aus dem Standard-Teilekatalog des Bestückers (z. B. JLC „Basic Parts“) | Fertiger |

Empfehlung: Rev. A handlötbar, aber bereits mit Teilen, die der Bestücker führt. Dann ist der Wechsel auf PCBA bei Rev. B nur noch ein Export.

## Werkzeuge

| Zweck | Werkzeug |
|---|---|
| Schaltung | atopile (VS-Code-/Cursor-Extension + CLI `ato`) |
| Layout, ERC/DRC, Export | KiCad 10 |
| Routing | Freerouting (KiCad-Plugin) |
| Prüfung durch Claude | KiCad-MCP-Server (z. B. Seeed-Studio `kicad-mcp-server`) |
| Analogsimulation | ngspice (in KiCad integriert oder standalone) |
| Firmware | PlatformIO oder avr-gcc/Makefile; Host-Unit-Tests |
| Versionierung | git (Mac und Linux Mint gleichermaßen) |
| Automatische Dokumentationsprüfung | GitHub Actions mit markdownlint-cli2 bei Pushes und Pull Requests |

## Repo-Struktur

```text
projekt/
├── docs/
│   ├── workflow.md          # dieses Dokument
│   ├── lastenheft.md
│   └── decisions/           # Entscheidungslog, eine Datei pro Entscheidung
├── hw/                      # atopile-Projekt (ato.yaml, *.ato, layouts/)
├── sim/                     # ngspice-Netzlisten und Ergebnisse
├── fw/                      # Firmware + tests/
└── fab/
    └── rev-a/               # Gerber, Bohrdaten, BOM, CPL, Bestellbelege
```

## Phasen

### 1. Lastenheft

- **Inhalt:** Funktion, Versorgung, Bedienung, Anzeige, Gehäuse/Maße, Fertigungsvariante, Budget, Nicht-Ziele.
- **Ergebnis:** `docs/lastenheft.md`
- **Gate:** Du gibst das Lastenheft frei.

### 2. Architektur

- **Inhalt:** Blockschaltbild, Wahl der Hauptkomponenten (MCU, Empfänger, Anzeige, Versorgung), Spannungsebenen, Pin-Budget.
- **Ergebnis:** Blockdiagramm und Einträge im Entscheidungslog.
- **Gate:** Du verstehst und akzeptierst jede Hauptkomponente einschließlich Datenblatt-Kernwerten.

### 3. Schaltung (atopile)

- **Inhalt:** Module pro Block, Constraints (Spannungen, Toleranzen), Teileauswahl durch den Compiler, Bauteilberechnungen (Vorwiderstände, Basisströme, Verlustleistung) als Kommentar bzw. Constraint.
- **Prüfung:** `ato build`, ERC, Netz-Review per MCP.
- **Gate:** Du reviewst den Code und den generierten Schaltplan. Mindestens prüfst du: Polaritäten, Pinbelegungen gegen Datenblatt, Versorgung jedes ICs, Abblockkondensatoren.

### 4. Simulation

- **Analog (ngspice):** Treiberstufen, LED-Ströme, Versorgung, Eingangsfilter. Grenzwerte bei Bauteiltoleranzen prüfen.
- **Firmware (Host-Tests):** Protokolldekodierung mit aufgezeichneten bzw. synthetischen Signalen, inklusive gestörter Signale.
- **Nicht simulierbar:** Funkempfang und EMV. Das prüft Phase 5.
- **Gate:** Simulationsergebnisse liegen in `sim/` und erfüllen das Lastenheft.

### 5. Prototyp

- **Aufbau:** Steckbrett mit **Modulen/Breakouts** (z. B. Arduino Nano, fertiges Empfängermodul, Display) statt Einzel-SMD-Teilen.
- **Ziel:** Kritische Risiken real prüfen: Empfang neben der Anzeige, Stromaufnahme, Lesbarkeit.
- **Gate:** Erkenntnisse sind in Schaltung und Entscheidungslog zurückgeflossen.

### 6. Layout

- **Platzierung:** Du gibst Randbedingungen vor (Maße, Bedienelemente, Abstand Antenne ↔ Störquellen). Claude platziert, du prüfst visuell.
- **Routing:** Kritische Leitungen manuell bzw. vorgegeben, Rest per Freerouting. Massefläche.
- **Prüfung:** DRC mit den Designregeln des Herstellers, MCP-Review, 3D-Ansicht, Ausdruck 1:1 auf Papier mit aufgelegten Bauteilen.
- **Gate:** DRC fehlerfrei, Papierprobe passt.

### 7. Fertigung

- **Export:** Gerber, Bohrdaten, BOM; bei PCBA zusätzlich Bestückungsdaten (CPL).
- **Platine:** Upload per Plugin bzw. Website (Aisler, JLCPCB, PCBWay). Gerber-Vorschau des Herstellers kontrollieren.
- **Bauteile:** BOM → Warenkorb (Mouser/DigiKey/Reichelt/LCSC). Mengen mit Reserve für Kleinteile.
- **Gate:** Du prüfst Vorschau und Warenkorb und bezahlst selbst.
- Bestellunterlagen kommen nach `fab/rev-x/`.

### 8. Inbetriebnahme und Rückblick

- **Reihenfolge:** Sichtprüfung → Versorgung ohne ICs → Strombegrenzung am Labornetzteil → Firmware flashen → Funktionstest gegen Lastenheft.
- **Rückblick:** Fehler, Abweichungen, Änderungen für die nächste Revision. Das ergibt ein Issue pro Punkt.

## Vorlage Entscheidungslog

Datei `docs/decisions/NNN-titel.md`:

```markdown
# NNN – Titel

- Datum:
- Status: vorgeschlagen | akzeptiert | ersetzt durch NNN

## Kontext
Welches Problem, welche Randbedingungen?

## Optionen
1. …
2. …

## Entscheidung
Gewählt: …, weil …

## Konsequenzen
Was folgt daraus, welche Risiken bleiben?
```

## Auftrag an Claude Code (Startvorlage)

> Lies `docs/workflow.md` und `docs/lastenheft.md`. Wir sind in Phase N.
> Arbeite nur diese Phase ab, halte Entscheidungen im Entscheidungslog fest
> und stoppe am Gate mit einer Zusammenfassung dessen, was ich prüfen muss.


HUMAN REVISION 04.10.2026 11:10 AS
