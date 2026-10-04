# Hardware-Funkuhr

Akku-betriebene Nachttischuhr mit DCF77-Zeitsynchronisation und LED-7-Segment-Anzeige im Retro-Stil (HH:MM:SS).

Das Projekt dient außerdem als Lernprojekt für einen halbautomatischen Konstruktionsworkflow: Die Schaltung wird als Python-Code mit SKiDL geschrieben, Layout und Prüfung laufen in KiCad, Claude Code unterstützt bei Entwurf, Berechnung und Prüfung.

## Eckdaten

- Versorgung: eine 18650-Li-Ion-Zelle, wechselbar; optional externe 5 V über USB-C (ohne Laden)
- Anzeige: LED-7-Segment, dauerhaft an, Ziffernhöhe 20–30 mm
- Zeit: DCF77, freilaufend ≤ 1 s/Tag Abweichung
- Fertigung: handlötbar, zweilagige Platine, Bauteile möglichst aus dem JLC-Basic-Katalog
- Budget: ≤ 50 € Elektronik ohne Platine

Details stehen im [Lastenheft](docs/lastenheft.md).

## Stand

| Phase | Status |
|---|---|
| 1. Lastenheft | freigegeben (v1.1, 2026-10-04) |
| 2. Architektur | freigegeben (2026-10-04, [Architektur](docs/architektur.md)) |
| 3. Schaltung (SKiDL) | freigegeben (2026-10-04, [Schaltung](docs/schaltung.md)) |
| 4. Simulation | freigegeben (2026-10-04, [Simulation](sim/README.md)) |
| 5. Prototyp | als Nächstes |
| 6. Layout | – |
| 7. Fertigung | – |
| 8. Inbetriebnahme | – |

## Verzeichnisse

```text
docs/            Lastenheft, Workflow, Setup, Entscheidungslog (decisions/)
hw/              Schaltung als Code (SKiDL), KiCad-Projekt, Layout
sim/             ngspice-Simulationen und Ergebnisse
fw/              Firmware und Host-Tests (tests/)
fab/rev-a/       Fertigungsdaten und Bestellunterlagen Rev. A
```

## Dokumente

- [Lastenheft](docs/lastenheft.md): Was die Uhr können muss
- [Workflow](docs/workflow.md): Phasen, Gates, Rollen, Werkzeuge
- [Architektur](docs/architektur.md): Blockschaltbild, Spannungen, Pin- und Strombudget
- [Schaltung](docs/schaltung.md): Blöcke, Rechnungen, Prüfergebnisse; dazu [Stückliste](docs/stueckliste.md) und [Pinbelegung](docs/schaltung-pinbelegung.md)
- [Setup](docs/setup.md): Installation der Werkzeuge unter Linux Mint

## Werkzeuge

SKiDL 2.3, KiCad 10, Freerouting 2.4, ngspice 42, avr-gcc/avrdude, KiCad-MCP-Server, git.
