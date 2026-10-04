# 005 – Versorgung und Verpolschutz

- Datum: 2026-10-04
- Status: akzeptiert, ergänzt durch [006](006-externe-5v-versorgung.md)

## Kontext

- Eine 18650-Zelle mit 3,0–4,2 V, wechselbar (E1). Kein Laden im Gerät (E2: nein).
- Verpolschutz ist Pflicht (S2), weil die Zelle sich verkehrt einlegen lässt.
- Zellschutz gegen Tiefentladung und Kurzschluss ist laut Lastenheft keine Anforderung (S1: nein).
- Der DCF-Empfänger braucht eine saubere Versorgung (siehe [003](003-dcf77-empfaenger.md)).

## Optionen

Verpolschutz:

1. **Schottky-Diode in Reihe:** einfach, verliert aber ca. 0,3 V. Das sind fast 10 % der Akkuspannung und spürbar weniger LED-Helligkeit bei leerem Akku.
2. **P-MOSFET als „ideale Diode“:** Bei richtiger Polung schaltet der MOSFET durch (Spannungsverlust im mV-Bereich). Bei falscher Polung sperrt er. Ein Bauteil im SOT-23-Gehäuse.
3. **Mechanisch:** ein Halter, der nur eine Richtung zulässt. Für 18650 kaum erhältlich.

Versorgung des Empfängers:

1. Direkt aus VSYS über ein RC-Filter (Widerstand und Kondensator als Tiefpass).
2. **LDO mit sehr kleinem Eigenverbrauch**, z. B. XC6206 (ca. 1 µA Ruhestrom, SOT-23).

## Entscheidung

Gewählt: **P-MOSFET AO3401A als Verpolschutz** und **LDO 3,3 V (XC6206P332MR, JLC Basic) nur für das DCF-Modul**. Alle anderen Verbraucher hängen direkt an der Hauptversorgung VSYS.

Ursprünglich waren 3,0 V vorgesehen. Wegen der optionalen 5-V-Versorgung sind es jetzt 3,3 V, die Begründung steht in [006](006-externe-5v-versorgung.md). Dort übernimmt der AO3401A auch das Abtrennen des Akkus, sobald 5 V anliegen. Dafür hängt sein Gate über einen Widerstand an Masse und zusätzlich an der 5-V-Leitung.

- AO3401A: P-Kanal, −30 V, SOT-23, JLC Basic. Er schaltet schon bei −2,5 V Gate-Source-Spannung gut durch (R_DS(on) im Bereich 50–70 mΩ). Bei 3,0 V Akkuspannung und ca. 100 mA Spitzenstrom verliert er nur ca. 7 mV.
- LDO statt RC-Filter, weil er Störungen auf VSYS deutlich besser unterdrückt. Oberhalb von ca. 3,4 V Akkuspannung sieht der Empfänger konstant 3,3 V, darunter etwas weniger. Das Modul läuft ab 2 V.

Genaue Typen und Werte (Gatewiderstand, Kondensatoren) legt Phase 3 fest.

## Konsequenzen

- **Tiefentladung:** Ohne Zellschutz kann eine ungeschützte Zelle unter 2,5 V fallen und Schaden nehmen. Festgelegt (2026-10-04):
  1. Eine **geschützte 18650** verwenden (mit eingebauter Schutzplatine). Sie ist ca. 2–3 mm länger. Der Halter muss sie aufnehmen (in Phase 3 prüfen).
  2. Zusätzlich schaltet die Firmware unter ca. 3,1 V die Anzeige ab, legt das DCF-Modul still und schläft. Rest-Verbrauch ca. 0,1–0,2 mA (DS3231).
- Ein Akkustand wird nicht angezeigt (E4: nein). Die dunkler werdende bzw. abgeschaltete Anzeige ist der Hinweis zum Wechseln.
- Testpunkte (H6): VSYS, 3V3_DCF, DCF-Signal, GND.
- Die Versorgung des Empfängers ist von der Anzeige entkoppelt. Die Massefläche bleibt durchgehend, ein „sternförmiger“ Masseanschluss für den Empfänger folgt in Phase 6.
