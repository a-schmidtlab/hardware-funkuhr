# Lastenheft – Akku-Funkuhr (Nachttisch)

- Version: 1.0
- Status: freigegeben (2026-10-04)

## 1. Zweck

Batteriebetriebene Tischuhr für den Nachttisch, die sich per DCF77 selbst stellt und eine gut ablesbare Digitalanzeige im Retro-Stil hat. Nebenziel ist das Erlernen des Workflows nach `workflow.md`.

## 2. Funktionale Anforderungen

| ID | Anforderung | Priorität |
|---|---|---|
| F1 | Anzeige von Stunden, Minuten und Sekunden (HH:MM:SS, 24 h) | muss |
| F2 | Automatische Zeitsynchronisation per DCF77, inkl. Sommer-/Winterzeit | muss |
| F3 | Freilaufende Uhr ohne Empfang, Abweichung ≤ 1 s/Tag | muss |
| F4 | Synchronisation mindestens 1× täglich, bevorzugt nachts | muss |
| F5 | Anzeige des Synchronisationsstatus (z. B. Punkt/Symbol, wenn letzte Sync > 24 h) | soll |
| F6 | Manuelles Stellen der Uhr ohne Empfang | soll |
| F7 | Anzeige von Datum auf Tastendruck | nein |
| F8 | Weckfunktion | nein |

## 3. Anzeige

| ID | Anforderung | Priorität |
|---|---|---|
| A1 | Retro-Optik (7-Segment o. ä.), keine teure Spezialanzeige (kein Nixie, kein VFD) | muss |
| A2 | Ziffernhöhe 20–30 mm, ablesbar aus 2 m Entfernung | muss |
| A3 | Nachts nicht blendend: Helligkeit automatisch an Umgebungslicht angepasst | nein |
| A4 | LED-7-Segment-Anzeige, dauerhaft an (Option a, siehe 9.1) | muss |

## 4. Energie

| ID | Anforderung | Priorität |
|---|---|---|
| E1 | Versorgung aus einer 18650-Li-Ion-Zelle (3,7 V nominal, 3,0–4,2 V), wechselbar | muss |
| E2 | Laden über USB-C (5 V) im Gerät | nein |
| E3 | Akkulaufzeit pro Ladung ca. 1–4 Wochen (Schätzung für Option a, Verifikation in Phase 4) | muss |
| E4 | Anzeige niedriger Akkuladung | nein |
| E5 | Betrieb während des Ladens möglich | nein |

## 5. Sicherheit

| ID | Anforderung | Priorität |
|---|---|---|
| S1 | Schutz gegen Überladung, Tiefentladung, Überstrom und Kurzschluss der Zelle | nein |
| S2 | Verpolschutz des Zellenhalters (18650 lässt sich verkehrt einlegen) | muss |
| S3 | Ladestrom ≤ 0,5 C bzw. gemäß Zellendatenblatt | nein |
| S4 | Keine Netzspannung im Gerät | muss |

## 6. Bedienung

| ID | Anforderung | Priorität |
|---|---|---|
| B1 | Maximal 3 Taster | soll |
| B2 | Bedienelemente frontseitig erreichbar | soll |

## 7. Mechanik

| ID | Anforderung | Priorität |
|---|---|---|
| M1 | Nachttischformat, Richtwert ca. 120–160 × 60–80 × 40–60 mm (B × H × T) | kann |
| M2 | Platine passend für ein Gehäuse (3D-Druck), wird später designed | soll |
| M3 | DCF-Antenne mit Abstand zu Anzeige (EMV) | muss |

## 8. Herstellung und Beschaffung

| ID | Anforderung | Priorität |
|---|---|---|
| H1 | Handlötbar: THT oder SMD ≥ 0805, ICs mit Pitch ≥ 0,65 mm, kein QFN/BGA | muss |
| H2 | Alle Teile per API bestellbar (LCSC/Mouser/DigiKey) | muss |
| H3 | Bevorzugt Teile aus dem JLC-Basic-Katalog (PCBA-Option für spätere Revision) | soll |
| H4 | Zweilagige Platine, Standardregeln (≥ 0,2 mm Leiterbahn/Abstand) | muss |
| H5 | Programmierschnittstelle auf der Platine (ISP/SWD/UART) | muss |
| H6 | Testpunkte für Versorgung und DCF-Signal | soll |
| H7 | Materialkosten Elektronik ohne Platine ≤ 50 € | kann |

## 9. Offene Punkte und bekannte Konflikte

### 9.1 Anzeige vs. Akkulaufzeit (Hauptkonflikt)

Nutzbare Energie: 18650 mit ca. 2500–3000 mAh nutzbar.

| Option | Ø Strom (Schätzung) | Laufzeit | Retro | Nachts ablesbar ohne Taste |
|---|---|---|---|---|
| a) LED-7-Segment, dauerhaft an, auto-gedimmt | 3–15 mA | ca. 1–4 Wochen | ja | ja |
| b) LED-7-Segment, nur auf Tastendruck/Bewegung | < 0,3 mA | Monate | ja | nein |
| c) Segment-LCD (z. B. 80er-Stil), dauerhaft an, Hintergrundlicht auf Tastendruck | < 0,1 mA | > 1 Jahr | ja (anders) | nur mit Licht/Taste |

**Entschieden: a).** Die Werte sind vor der Architekturphase grob geschätzt. Phase 4 verifiziert sie.

### 9.2 Weitere offene Punkte

- **Beschaffung DCF77-Modul (H2):** Verfügbarkeit über API-Distributoren prüfen. Fertigmodule kommen häufig nur von Reichelt/Pollin/ELV. Eventuell wird eine dokumentierte Ausnahme von H2 nötig.
- **Gehäuse (M2):** 3D-Druck vorhanden? JA
- **Budget (H7):** ≤ 50 € ohne Platine – geklärt

## 10. Nicht-Ziele

- Kein WLAN/Bluetooth/NTP
- Kein Netzbetrieb
- Kein Gehäusedesign in Rev. A (nur Platinenmaße und Bohrungen)
