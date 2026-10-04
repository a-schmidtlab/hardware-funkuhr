# 003 – DCF77-Empfänger

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

Ein DCF77-Empfänger besteht aus einer abgestimmten Ferritantenne, einem Empfänger-IC und einem 77,5-kHz-Filterquarz. Antenne und Quarz selbst abzustimmen ist aufwendig. Die Empfänger-ICs gibt es zudem kaum handlötbar einzeln zu kaufen. Deshalb kommt ein fertiges Modul in Frage.

H2 verlangt Bestellbarkeit per API (LCSC, Mouser oder DigiKey). Das Lastenheft (9.2) rechnet bereits damit, dass dafür eine Ausnahme nötig werden könnte.

## Optionen

1. **Pollin DCF1** (Best.-Nr. 810054, 5,60 €): klein (15 × 11 mm), 1,2–3,3 V, < 90 µA, Ein/Aus-Pin (PON). Stand 2026-10-04 bei Pollin „nicht in ausreichender Stückzahl verfügbar“. Nicht per API bestellbar, also eine Ausnahme von H2.
2. **Reichelt „DCF77 MODUL“:** 1,2–5 V. Der Ausgang liefert nur ca. 5 µA, laut Foren reagiert das Modul empfindlich auf Versorgungsstörungen. Nicht per API, also ebenfalls eine Ausnahme von H2.
3. **CANADUINO Atomic Clock Receiver V4** (Universal Solder, DigiKey 26019/26020, ca. 18 €): Empfänger-IC MAS6180C, 60-mm-Ferritantenne, 2–5,5 V. Push-Pull-Ausgänge OUT und /OUT mit bis zu 20 mA, Status-LEDs abschaltbar. Bei DigiKey lagernd, erfüllt H2.

## Entscheidung

Gewählt: **CANADUINO V4 mit 77,5-kHz-Quarz**, weil:

- es als einziges Modul H2 ohne Ausnahme erfüllt (DigiKey).
- sein Ausgang kräftig genug ist, um den Mikrocontroller-Eingang direkt zu treiben. Ein zusätzlicher Pull-up-Widerstand entfällt.
- es mit 2–5,5 V den ganzen Bereich unseres 3,3-V-Reglers abdeckt.
- das Datenblatt brauchbare Hinweise zur Platzierung der Antenne gibt.

Datenblatt-Kernwerte (CANADUINO V4 / MAS6180C):

| Wert | |
|---|---|
| Versorgung | 2–5,5 V, „muss sauber und stabil sein“ |
| Ausgänge | OUT und /OUT, Pegel = Versorgung, max. ±20 mA |
| Status-LEDs | aus, wenn der LED-Pin offen bleibt (Pflicht, sonst zusätzlicher Strom) |
| AGC (automatische Verstärkungsregelung) | an, solange AON offen bleibt |
| Antenne | 60-mm-Ferritstab, waagerecht, quer zur Richtung Frankfurt |
| Lieferform | Bausatz: Der Quarz (77,5 kHz) wird selbst eingelötet |

Rückfalloption: Pollin DCF1, mit dokumentierter Ausnahme von H2, falls das CANADUINO-Modul im Prototyp schlecht empfängt.

## Konsequenzen

- Teuerster Einzelposten (ca. 18 €, dazu DigiKey-Versand, frei ab ca. 50 € Bestellwert).
- Versorgung über einen eigenen LDO mit 3,3 V (siehe [005](005-versorgung.md) und [006](006-externe-5v-versorgung.md)), zur Entkopplung vom Multiplex-Rauschen der Anzeige.
- Der genaue Ruhestrom (MAS6180C ca. 100 µA) und der Abschaltpin des Moduls werden in Phase 3 am IC-Datenblatt verifiziert.
- Platzierung (M3): an der Platinenkante gegenüber der Anzeige, die Antenne nicht auf die Anzeige gerichtet. Keine Massefläche unter der Antenne.
- Größtes Projektrisiko: Störung durch die gemultiplexte Anzeige. Der Prototyp prüft das zuerst.
