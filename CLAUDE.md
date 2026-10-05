# CLAUDE.md – Hardware-Funkuhr

## Zusammenarbeit

- Sprache: Deutsch.
- Axel lernt mit diesem Projekt den Workflow. KiCad und die übliche Schaltplandarstellung sind ihm noch nicht geläufig. Deshalb Schritt für Schritt erklären, Fachbegriffe beim ersten Auftreten kurz erläutern, Fragen ausdrücklich willkommen heißen.
- Braucht etwas `sudo`: den fertigen Befehl vorlegen und warten. Nicht mit lokalen Downloads oder Ähnlichem umgehen.
- Nur dieses Linux-Mint-System zählt. Den Mac nicht berücksichtigen.
- Commit und Push (GitHub `origin/main`) nur auf Aufforderung oder nach Freigabe. Commit-Nachrichten auf Deutsch.

## Vor jeder Arbeit lesen

1. [docs/electronics-workflow.md](docs/electronics-workflow.md): Phasen, Gates, Rollen, Vorlagen (gilt ab Wiederaufnahme; [docs/workflow.md](docs/workflow.md) ist die ursprüngliche Fassung)
2. [docs/lastenheft.md](docs/lastenheft.md): Anforderungen (v1.1 freigegeben)
3. [README.md](README.md): **aktueller Phasenstand**. Die Tabelle dort wird am Ende jeder Phase aktualisiert.
4. [docs/erkenntnisse.md](docs/erkenntnisse.md): Learnings und Schritte zur Wiederaufnahme. Das Projekt ist seit 2026-10-05 vor Phase 5 pausiert.

## Arbeitsregeln aus dem Workflow

- Nur die aktuelle Phase bearbeiten und am Gate mit einer Prüfliste für Axel stoppen. Ohne seine Freigabe nicht weitermachen.
- Jede relevante Designentscheidung kommt nach `docs/decisions/NNN-titel.md`, nach der Vorlage im Workflow.
- Die Schaltung entsteht als SKiDL-Code (Python) in `hw/`, nicht im Schaltplan-Editor. atopile wird nicht mehr genutzt (Entscheidung 007). KiCad dient zu Layout, Prüfung und Export.
- Kein Kennwert, keine Pinbelegung, keine Bestellnummer aus dem Gedächtnis: Datenblatt bzw. Händlerseite prüfen und Quelle im Code nennen.
- Erzeugte Dateien (`docs/stueckliste.md`, `docs/schaltung-pinbelegung.md`, `sim/ergebnisse.md`) nicht von Hand ändern, sondern per `make` neu erzeugen.
- KiCad-MCP-Server (`kicad`) nur als Prüfwerkzeug nutzen (Netze, ERC/DRC, BOM), nicht zum Zeichnen.
- Bezahlen bleibt manuell.

## Werkzeuge

Installation und Pfade: [docs/setup.md](docs/setup.md). Kurz:

- SKiDL 2.3 + kinet2pcb in `hw/.venv` (System-Python mit `pcbnew`); Bauen mit `make` in `hw/`
- `kicad-cli`: KiCad 10
- `freerouting --gui.enabled=false -de x.dsn -do x.ses`: ohne `--gui.enabled=false` öffnet sich die Oberfläche
- `ngspice`: Version 42
- `avr-gcc` 7.3, `avrdude` 7.1: für den ATmega328PB zusätzlich `-B $DFP/gcc/dev/atmega328pb -I $DFP/include` mit `DFP=~/.local/share/avr-dfp/ATmega_DFP-3.6.299` (Microchip Device Pack, siehe setup.md)
