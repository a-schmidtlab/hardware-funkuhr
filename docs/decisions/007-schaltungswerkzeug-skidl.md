# 007 – Schaltungswerkzeug: SKiDL statt atopile

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Der Workflow sah vor, die Schaltung als Code in atopile zu schreiben. Beim Start von Phase 3 zeigte sich:

- atopile 0.15.9 ist das letzte Release der Kommandozeile und steht nur noch im Wartungsmodus. Nachfolger ist atopile 0.16, eine Entwicklungsumgebung im Browser, die eine Anmeldung verlangt.
- Der Build in 0.15 bricht ohne Anmeldung ab: *„Part picking on atopile 0.15.8 requires sign-in. Run `ato auth login`, or migrate to app.atopile.io (0.16+).“*
- Laut Quellcode (`faebryk/libs/picker/api/api.py`) läuft jede Bauteilabfrage über den atopile-Server, auch bei fest vorgegebener Teilenummer. Lokal definierte Bauteile ohne Server bekommen keine Bezeichnungen wie R1 oder C1, und der Build scheitert.
- Die Firma hinter atopile ist ein Start-up (Y Combinator, Winter 2024) und zielt auf Firmenkunden. Preise und Bedingungen für die Cloud-Dienste sind nicht öffentlich.

Gewünscht ist ein Werkzeug, das lokal läuft, ohne Konto und ohne Abhängigkeit von einem Dienst, der eingestellt werden kann.

## Optionen

1. **atopile 0.15 mit Anmeldung** (`ato auth login`): Der Workflow bliebe unverändert. Wir hängen aber an einem Dienst, den der Hersteller nur noch „etwas länger“ anbietet.
2. **atopile 0.16 (Browser):** offizieller Nachfolger. Die Schaltung läge in der Cloud des Herstellers, die Bedingungen sind unklar.
3. **SKiDL:** Python-Bibliothek (MIT), seit 2016, Version 2.3.0 vom Juli 2026 mit Unterstützung für KiCad 10. Sie nutzt direkt die lokalen KiCad-Bibliotheken für Symbole und Footprints. Keine automatische Bauteilauswahl.
4. **Schaltplan direkt in KiCad zeichnen:** Damit wäre das Projektziel „Schaltung als Code“ aufgegeben.

## Entscheidung

Gewählt: **SKiDL**, weil:

- es komplett lokal läuft, ohne Konto, Server oder Cloud.
- es seit Jahren stabil ist (laut PyPI „Production/Stable“) und KiCad 10 ausdrücklich unterstützt.
- die Schaltung normaler Python-Code ist. Rechnungen wie Vorwiderstände oder Ströme stehen direkt daneben im selben Code.
- es neben der Netzliste auch einen editierbaren KiCad-Schaltplan erzeugt. Der ist für die Prüfung in Phase 3 hilfreich.

Der Test am 2026-10-04 mit ATmega328PB, Widerstand und Kondensator bestand alle Schritte:

| Schritt | Ergebnis |
|---|---|
| Symbole aus der KiCad-10-Bibliothek | ✓ einschließlich ATmega328PB-A |
| SKiDL-ERC (elektrische Regelprüfung) | ✓ |
| Netzliste mit Footprints und eigenem Feld „LCSC“ | ✓ |
| KiCad-Schaltplan erzeugen, KiCad-ERC, PDF-Export | ✓ |
| Platinendatei aus der Netzliste (`kinet2pcb`) | ✓ Footprints und Netze stimmen |

## Konsequenzen

- **Keine automatische Bauteilauswahl:** Jedes Bauteil wird im Code mit Symbol, Footprint, Wert und LCSC-Nummer festgelegt. Die Hauptbauteile stehen seit Phase 2 fest. Für die Kleinteile wähle ich bevorzugt JLC-Basic-Teile und dokumentiere die Auswahl im Code.
- **Kein Rechnen mit Wertebereichen** wie in atopile. Bauteilberechnungen stehen als Python-Rechnung mit Kommentar im Code, Prüfungen als `assert`.
- **Automatischer Schaltplan:** Er ist elektrisch korrekt, aber gedrängt gezeichnet, mit überlappenden Beschriftungen. Für die Prüfung am Gate gibt es deshalb zusätzlich eine Pin- und Netztabelle je IC. Den Schaltplan kann man in KiCad von Hand ordnen.
- **Feld „LCSC“:** `kinet2pcb` übernimmt es nicht in die Platine. Die Stückliste entsteht deshalb aus der Netzliste bzw. dem Schaltplan. Wie spätere Schaltungsänderungen in ein bestehendes Layout kommen, klärt Phase 6. Möglich sind „Platine aus Schaltplan aktualisieren“ oder der Netzlisten-Import in KiCad.
- **Einziger Hauptentwickler:** Fällt er weg, läuft die installierte Version trotzdem weiter. Die Versionen sind in `hw/requirements.txt` festgeschrieben.
- **Dokumente:** Workflow, CLAUDE.md, README und setup.md sind angepasst. atopile bleibt vorerst installiert, wird aber nicht mehr genutzt.
