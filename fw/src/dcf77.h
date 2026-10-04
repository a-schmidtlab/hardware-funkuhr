/*
 * DCF77-Dekoder (plattformunabhängig, ohne Hardwarezugriff).
 *
 * Die Firmware ruft dcf77_tick() alle 10 ms mit dem aktuellen Pegel des
 * Empfängers auf. „puls = true“ bedeutet: Träger abgesenkt (Sekundenmarke
 * aktiv). Welcher Pegel am Modulausgang dem entspricht, legt die Firmware
 * fest (Phase 5, am echten Modul).
 *
 * Protokoll (PTB): Jede Sekunde beginnt mit einer Absenkung von 100 ms
 * (Bit 0) oder 200 ms (Bit 1). In Sekunde 59 fehlt die Absenkung; der
 * nächste Sekundenbeginn ist die Minutenmarke. Die 59 Bits einer Minute
 * beschreiben die Uhrzeit, die ab der folgenden Minutenmarke gilt.
 *
 * Sicherheit gegen falsche Zeiten: Eine Zeit wird nur gemeldet, wenn
 *   1. alle 59 Bits sauber empfangen wurden (Pulslängen und Abstände),
 *   2. feste Bits, drei Paritäten und alle Wertebereiche stimmen und
 *   3. sie genau eine Minute nach der vorigen gültigen Minute liegt.
 */
#ifndef DCF77_H
#define DCF77_H

#include <stdbool.h>
#include <stdint.h>

#define DCF77_TICK_MS 10u
#define DCF77_ENTPRELL 3u /* Ticks: Störungen bis 20 ms werden ignoriert */

typedef struct {
    uint8_t minute;  /* 0–59 */
    uint8_t stunde;  /* 0–23 */
    uint8_t tag;     /* 1–31 */
    uint8_t wochentag; /* 1 = Montag … 7 = Sonntag */
    uint8_t monat;   /* 1–12 */
    uint8_t jahr;    /* 0–99 (= 2000–2099) */
    bool mesz;       /* true = Sommerzeit (MESZ), false = MEZ */
} dcf77_zeit_t;

typedef struct {
    /* Entprellung (nur für die Erkennung des Sekundenbeginns) */
    uint8_t integrator;
    bool pegel;
    /* Zeitmessung in Ticks */
    uint16_t seit_pulsbeginn;   /* seit dem letzten anerkannten Sekundenbeginn */
    bool pulsbeginn_bekannt;
    /* Bitauswertung per Abtastfenster nach dem Sekundenbeginn */
    bool auswertung_laeuft;
    uint8_t fenster_anfang;     /* aktive Abtastwerte am Pulsanfang */
    uint8_t fenster_bit;        /* aktive Abtastwerte im Bitfenster */
    /* aktueller Minutenrahmen */
    uint16_t rahmen_ticks;      /* seit Beginn von Sekunde 0 */
    uint16_t letzte_sekunde;    /* rahmen_ticks beim letzten Sekundenbeginn */
    uint8_t bitnr;
    uint8_t bits[8];
    bool rahmen_ok;
    /* zuletzt dekodierte Minute für die Plausibilitätsprüfung */
    bool vorige_gueltig;
    dcf77_zeit_t vorige;
    /* an der Minutenmarke dekodiert, wartet auf Bestätigung durch Bit 0
     * in Sekunde 0 */
    bool kandidat_offen;
    bool kandidat_plausibel;
    dcf77_zeit_t kandidat;
} dcf77_t;

void dcf77_init(dcf77_t *d);

/*
 * Alle 10 ms aufrufen. Gibt true zurück, wenn eine geprüfte Zeit vorliegt.
 * Das geschieht am Ende des Bitfensters von Sekunde 0, denn erst dessen
 * Bitwert 0 bestätigt, dass die Minutenmarke echt war.
 * *zeit ist die Uhrzeit hh:mm:00 am (entprellten) Beginn dieser Sekunde;
 * seitdem sind dcf77_ticks_seit_sekundenbeginn() Ticks vergangen. Der
 * echte Sekundenbeginn liegt weitere DCF77_ENTPRELL Ticks davor.
 */
bool dcf77_tick(dcf77_t *d, bool puls, dcf77_zeit_t *zeit);

static inline uint16_t dcf77_ticks_seit_sekundenbeginn(const dcf77_t *d)
{
    return d->seit_pulsbeginn;
}

/* Hilfsfunktionen, auch für Tests */
bool dcf77_dekodiere(const uint8_t bits[8], dcf77_zeit_t *zeit);
void dcf77_plus_minute(dcf77_zeit_t *z);
bool dcf77_gleich(const dcf77_zeit_t *a, const dcf77_zeit_t *b);

#endif
