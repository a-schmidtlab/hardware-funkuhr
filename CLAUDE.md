# CLAUDE.md – Hardware-Funkuhr

## Zusammenarbeit

- Sprache: Deutsch.
- Axel lernt mit diesem Projekt den Workflow. KiCad und die übliche Schaltplandarstellung sind ihm noch nicht geläufig. Deshalb Schritt für Schritt erklären, Fachbegriffe beim ersten Auftreten kurz erläutern, Fragen ausdrücklich willkommen heißen.
- Braucht etwas `sudo`: den fertigen Befehl vorlegen und warten. Nicht mit lokalen Downloads oder Ähnlichem umgehen.
- Nur dieses Linux-Mint-System zählt. Den Mac nicht berücksichtigen.
- Commit und Push (GitHub `origin/main`) nur auf Aufforderung oder nach Freigabe. Commit-Nachrichten auf Deutsch.

## Vor jeder Arbeit lesen

1. [docs/workflow.md](docs/workflow.md): Phasen, Gates, Rollen, Entscheidungslog-Vorlage
2. [docs/lastenheft.md](docs/lastenheft.md): Anforderungen (v1.0 freigegeben)
3. [README.md](README.md): **aktueller Phasenstand**. Die Tabelle dort wird am Ende jeder Phase aktualisiert.

## Arbeitsregeln aus dem Workflow

- Nur die aktuelle Phase bearbeiten und am Gate mit einer Prüfliste für Axel stoppen. Ohne seine Freigabe nicht weitermachen.
- Jede relevante Designentscheidung kommt nach `docs/decisions/NNN-titel.md`, nach der Vorlage in `workflow.md`.
- Die Schaltung entsteht als atopile-Code in `hw/`, nicht im Schaltplan-Editor. KiCad dient zu Layout, Prüfung und Export.
- KiCad-MCP-Server (`kicad`) nur als Prüfwerkzeug nutzen (Netze, ERC/DRC, BOM), nicht zum Zeichnen.
- Bezahlen bleibt manuell.

## Werkzeuge

Installation und Pfade: [docs/setup.md](docs/setup.md). Kurz:

- `ato`: atopile 0.15 (Python 3.14 über uv)
- `kicad-cli`: KiCad 10
- `freerouting --gui.enabled=false -de x.dsn -do x.ses`: ohne `--gui.enabled=false` öffnet sich die Oberfläche
- `ngspice`: Version 42
- Firmware-Werkzeuge sind noch nicht installiert. Sie kommen nach der Wahl des Mikrocontrollers (Phase 2).
