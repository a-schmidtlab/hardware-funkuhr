# 006 – Externe 5-V-Versorgung (Option)

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Lastenheft E6 (kann): Die Uhr soll optional mit externen 5 V laufen, z. B. dauerhaft am Nachttisch an einem vorhandenen USB-Ladegerät. Randbedingungen:

- Nur eine Bestückungsoption: Die Platine bekommt den Platz dafür, die Buchse wird nur bei Bedarf bestückt. Ohne Buchse muss alles funktionieren wie bisher.
- Kein Netzteil im Gerät (S4). Die 5 V kommen von außen.
- Der Akku wird **nicht** geladen (E2: nein). Eine Li-Ion-Zelle an 5 V ohne Laderegler ist gefährlich. Die 5 V dürfen also nie zur Zelle gelangen.
- Der Akku darf eingelegt bleiben, und wird er falsch herum eingelegt, muss der Verpolschutz (S2) weiter funktionieren.

## Optionen

Buchse:

1. **USB-C, nur Versorgung** (6-polige „power only“-Bauform, Pins mit großem Abstand, handlötbar): Jedes Handy-Ladegerät passt. Damit das Ladegerät 5 V liefert, braucht die Buchse zwei 5,1-kΩ-Widerstände an CC1/CC2.
2. **Hohlstecker 5,5/2,1 mm:** robust. Es passen aber auch 9- oder 12-V-Netzteile, und ein Verwechseln zerstört die Uhr.
3. **2-poliger Stiftstecker:** am billigsten, aber nichts für den Alltag.

Umschaltung zwischen Akku und 5 V:

1. **Zwei Dioden** („Dioden-ODER“): einfach, verliert aber auch im Akkubetrieb ca. 0,3 V an der Diode.
2. **Lastumschaltung mit dem vorhandenen P-MOSFET** (bekannte Schaltung, z. B. Microchip AN1149): Die 5 V speisen über eine Schottky-Diode ein. Das Gate des Verpol-MOSFET hängt nicht mehr fest an Masse, sondern über einen Widerstand an Masse **und** an der 5-V-Leitung.
   - Ohne 5 V liegt das Gate auf Masse. Der MOSFET leitet und der Akku versorgt die Uhr, ohne Diodenverlust.
   - Mit 5 V liegt das Gate auf 5 V. Der MOSFET sperrt und trennt den Akku ab. Seine interne Diode sperrt ebenfalls, weil die Uhrseite mit ca. 4,7 V höher liegt als der Akku mit höchstens 4,2 V.
   - Bei falsch eingelegtem Akku sperrt der MOSFET wie bisher.

## Entscheidung

Gewählt: **USB-C-Buchse (nur Versorgung) + Schottky-Diode + Lastumschaltung mit dem AO3401A** aus [005](005-versorgung.md), weil:

- der Akku im Akkubetrieb weiterhin keine Diodenverluste hat. Das ist wichtig für die Laufzeit (E3).
- dasselbe Bauteil Verpolschutz und Akkutrennung übernimmt. Zusätzlich kommen nur Diode, Gatewiderstand und Buchse hinzu.
- USB-Ladegeräte überall vorhanden sind und auf 5 V begrenzt bleiben, solange die Buchse kein Schnellladeprotokoll aushandelt. Mit reinen CC-Widerständen tut sie das nicht.
- ohne bestückte Buchse die Gate-Leitung über den Widerstand auf Masse liegt. Die Schaltung verhält sich dann exakt wie der reine Verpolschutz.

Folgeänderung: Der Regler für das DCF-Modul bekommt **3,3 V statt 3,0 V** (XC6206P332MR, JLC Basic). Grund ist die Pegelprüfung: Bei 5-V-Betrieb liegt der Mikrocontroller bei ca. 4,7 V und erkennt „High“ erst ab 0,6 × 4,7 V = 2,82 V. 3,0 V vom Modul wären nur 0,18 V Abstand, 3,3 V ergeben 0,48 V. Im Akkubetrieb unter 3,3 V gibt der Regler einfach fast die Akkuspannung durch. Das Modul läuft ab 2 V, das ist unkritisch.

## Konsequenzen

- Die Hauptversorgung heißt jetzt **VSYS** und liegt zwischen 3,0 und ca. 4,7 V. Alle Bauteile vertragen das: ATmega328PB bis 5,5 V, DS3231 bis 5,5 V, XC6206 bis 6 V.
- Die Vorwiderstände der Anzeige werden in Phase 3 für 4,7 V als ungünstigsten Fall ausgelegt. Die Firmware gleicht die Helligkeit wie bisher über die gemessene Betriebsspannung aus.
- Die Firmware erkennt den 5-V-Betrieb ohne zusätzlichen Pin: Liegt die gemessene Betriebsspannung über ca. 4,4 V, kann das nur die externe Versorgung sein. Dann gibt es keine Unterspannungsabschaltung, und die Anzeige darf heller sein.
- Detail für Phase 3: Im Akkubetrieb fließt ein kleiner Sperrstrom rückwärts durch die Schottky-Diode auf die 5-V-Leitung und damit aufs Gate. Der Gatewiderstand nach Masse muss so klein sein, dass das Gate trotzdem nahe 0 V bleibt. Schottky-Dioden haben je nach Typ und Temperatur viel Sperrstrom, deshalb einen Typ mit wenig Sperrstrom wählen und nachrechnen.
- **Risiko Empfang:** Billige USB-Ladegeräte sind Schaltnetzteile und können DCF77 stören, über die Leitung und als Abstrahlung. Die Buchse kommt deshalb ans Anzeigeende der Platine, weg von der Antenne. Der Prototyp testet mit einem typischen Ladegerät.
- Kosten bei Bestückung: ca. 1 € (Buchse, Diode, 2 Widerstände). Unbestückt kostet die Option nur Platinenfläche.
- Lastenheft auf v1.1 angehoben (E6). Die Freigabe der Änderung steht noch aus.
