# Hardware-Funkuhr

Akku-betriebene Nachttischuhr mit DCF77-Zeitsynchronisation und LED-7-Segment-Anzeige im Retro-Stil (HH:MM:SS).

Das Projekt dient außerdem als Lernprojekt für einen halbautomatischen Konstruktionsworkflow: Die Schaltung wird als Code mit atopile geschrieben, Layout und Prüfung laufen in KiCad, Claude Code unterstützt bei Entwurf, Berechnung und Prüfung.

## Eckdaten

- Versorgung: eine 18650-Li-Ion-Zelle, wechselbar
- Anzeige: LED-7-Segment, dauerhaft an, Ziffernhöhe 20–30 mm
- Zeit: DCF77, freilaufend ≤ 1 s/Tag Abweichung
- Fertigung: handlötbar, zweilagige Platine, Bauteile möglichst aus dem JLC-Basic-Katalog
- Budget: ≤ 50 € Elektronik ohne Platine

Details stehen im [Lastenheft](docs/lastenheft.md).

## Stand

| Phase | Status |
|---|---|
| 1. Lastenheft | freigegeben (v1.0, 2026-10-04) |
| 2. Architektur | als Nächstes |
| 3. Schaltung (atopile) | – |
| 4. Simulation | – |
| 5. Prototyp | – |
| 6. Layout | – |
| 7. Fertigung | – |
| 8. Inbetriebnahme | – |

## Verzeichnisse

```text
docs/            Lastenheft, Workflow, Setup, Entscheidungslog (decisions/)
hw/              atopile-Projekt (Schaltung, Layout)
sim/             ngspice-Simulationen und Ergebnisse
fw/              Firmware und Host-Tests (tests/)
fab/rev-a/       Fertigungsdaten und Bestellunterlagen Rev. A
```

## Dokumente

- [Lastenheft](docs/lastenheft.md): Was die Uhr können muss
- [Workflow](docs/workflow.md): Phasen, Gates, Rollen, Werkzeuge
- [Setup](docs/setup.md): Installation der Werkzeuge unter Linux Mint

## Werkzeuge

atopile 0.15, KiCad 10, Freerouting 2.4, ngspice 42, KiCad-MCP-Server, git.
