# 008 – Versorgungspin von ISP- und UART-Stecker an V5_EXT

- Datum: 2026-10-04
- Status: akzeptiert

## Kontext

ISP-Programmer (z. B. USBasp) und USB-Seriell-Adapter haben einen VCC-Pin. Viele liefern dort 5 V oder 3,3 V, oft ohne Abschaltmöglichkeit.

Läge dieser Pin an VSYS, gäbe es ein Sicherheitsproblem: Q1 (AO3401A, siehe [005](005-versorgung.md)) ist im Akkubetrieb durchgeschaltet, und ein durchgeschalteter MOSFET leitet in beide Richtungen. Der Programmer würde den Li-Ion-Akku mit 5 V ungeregelt laden. Genau das schließt E2 aus.

## Optionen

1. **VCC-Pin an VSYS:** üblich, aber mit Akku gefährlich (siehe oben).
2. **VCC-Pin nicht anschließen:** Die Uhr läuft beim Programmieren aus dem Akku. Programmer, die die Zielspannung messen wollen, sehen dann 0 V.
3. **VCC-Pin an V5_EXT** (wie die USB-C-Buchse, siehe [006](006-externe-5v-versorgung.md)): Liefert der Programmer Strom, sperrt Q1 und trennt den Akku ab. Die Schaltung läuft dann über D1 (BAT54) aus dem Programmer.

## Entscheidung

Gewählt: **3, VCC von ISP (J2 Pin 2) und UART (J3 Pin 3) an V5_EXT.**

Dadurch sind D1 und C2 nicht mehr Teil der USB-C-Option, sondern werden immer bestückt. Ohne D1 würde ein Programmer den Akku abtrennen, ohne selbst VSYS zu versorgen.

## Konsequenzen

- Programmieren und Debuggen geht mit und ohne eingelegten Akku. Der Akku wird nie geladen.
- Liefert der Programmer 3,3 V statt 5 V: Q1 sperrt nicht vollständig. VSYS kommt dann über die interne Diode von Q1 aus dem Akku. Auch hier wird nichts geladen.
- Programmer, die die Zielspannung nur messen und selbst nichts liefern (z. B. Atmel-ICE), sehen am VCC-Pin 0 V. Für unsere Werkzeuge (USBasp, USB-Seriell-Adapter) spielt das keine Rolle. Wird später ein messender Programmer benutzt, muss ein Drahtbügel zu VSYS her.
- Pegel: Bei Versorgung aus dem Programmer liegt VSYS bei ca. 4,5 V, die Programmer-Signale bei 5 V. Das liegt innerhalb VCC + 0,5 V und ist zulässig.
