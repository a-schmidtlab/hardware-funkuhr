/*
 * Host-Tests für den DCF77-Dekoder (Phase 4).
 *
 * Ein Generator erzeugt das Empfängersignal Tick für Tick (10 ms) aus einer
 * vorgegebenen Uhrzeit, wahlweise mit Störungen. Der Dekoder darf nie eine
 * falsche Zeit melden und soll bei brauchbarem Signal synchronisieren.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../src/dcf77.h"

static int fehler = 0;
static int pruefungen = 0;

#define PRUEFE(bed, ...)                                    \
    do {                                                    \
        pruefungen++;                                       \
        if (!(bed)) {                                       \
            fehler++;                                       \
            printf("  FEHLER %s:%d: ", __FILE__, __LINE__); \
            printf(__VA_ARGS__);                            \
            printf("\n");                                   \
        }                                                   \
    } while (0)

/* --- deterministischer Zufall (xorshift32) -------------------------------- */
static uint32_t zufall_zustand = 1;
static uint32_t zufall(void)
{
    uint32_t x = zufall_zustand;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return zufall_zustand = x;
}
static double zufall01(void) { return (zufall() & 0xFFFFFF) / (double)0x1000000; }

/* --- Kodierung: Uhrzeit -> 59 Bits ---------------------------------------- */
static void setze(uint8_t bits[8], int n, int w)
{
    if (w) bits[n >> 3] |= (uint8_t)(1u << (n & 7));
    else bits[n >> 3] &= (uint8_t)~(1u << (n & 7));
}
static int hole(const uint8_t bits[8], int n) { return (bits[n >> 3] >> (n & 7)) & 1; }

static void bcd_schreiben(uint8_t bits[8], int start, int anzahl, int wert)
{
    static const int gewicht[8] = {1, 2, 4, 8, 10, 20, 40, 80};
    int einer = wert % 10, zehner = wert / 10 * 10;
    for (int i = anzahl - 1; i >= 0; i--) {
        int g = gewicht[i];
        if (i >= 4 && zehner >= g) { setze(bits, start + i, 1); zehner -= g; }
        else if (i < 4 && einer >= g) { setze(bits, start + i, 1); einer -= g; }
        else setze(bits, start + i, 0);
    }
}

static void paritaet(uint8_t bits[8], int von, int bis, int pbit)
{
    int s = 0;
    for (int n = von; n < bis; n++) s ^= hole(bits, n);
    setze(bits, pbit, s);
}

static void kodiere(const dcf77_zeit_t *z, uint8_t bits[8])
{
    memset(bits, 0, 8);
    for (int n = 1; n <= 14; n++) setze(bits, n, (int)(zufall() & 1)); /* Wetterdaten: beliebig */
    setze(bits, 17, z->mesz);
    setze(bits, 18, !z->mesz);
    setze(bits, 20, 1);
    bcd_schreiben(bits, 21, 7, z->minute);
    paritaet(bits, 21, 28, 28);
    bcd_schreiben(bits, 29, 6, z->stunde);
    paritaet(bits, 29, 35, 35);
    bcd_schreiben(bits, 36, 6, z->tag);
    bcd_schreiben(bits, 42, 3, z->wochentag);
    bcd_schreiben(bits, 45, 5, z->monat);
    bcd_schreiben(bits, 50, 8, z->jahr);
    paritaet(bits, 36, 58, 58);
}

/* --- Signalgenerator ------------------------------------------------------- */
typedef struct {
    double takt;          /* Faktor MCU-Takt: 1,05 = MCU-Ticks 5 % zu schnell */
    double jitter_ms;     /* ± zufällige Verschiebung jeder Flanke */
    double glitch_rate;   /* Wahrscheinlichkeit je Tick für einen Störimpuls */
    int glitch_max_ticks; /* Länge eines Störimpulses 1 … max Ticks */
    double ausfall_rate;  /* Wahrscheinlichkeit, dass ein Sekundenpuls fehlt */
    double bitfehler_rate;/* Wahrscheinlichkeit, dass ein Puls die falsche Länge hat */
    int schaltsekunde;    /* 1 = diese Minute hat 61 Sekunden */
} stoerung_t;

static const stoerung_t SAUBER = {1.0, 0, 0, 0, 0, 0, 0};

typedef struct {
    dcf77_t dek;
    int meldungen;
    int falsch;
    dcf77_zeit_t letzte;
    double zeit_ms;   /* echte Zeit seit Simulationsbeginn */
    double tick_ms;   /* nächster MCU-Tick in echter Zeit */
    int glitch_rest;
} sim_t;

static dcf77_zeit_t erwartet_bei_marke; /* Wahrheit für die nächste Minutenmarke */
static double marke_ms = -1e9;          /* echte Zeit dieser Minutenmarke */

/* Erzeugt Ticks für ein Intervall [von, bis) echter Zeit mit Pegel puls */
static void abschnitt(sim_t *s, double bis_ms, int puls, const stoerung_t *st)
{
    while (s->tick_ms < bis_ms) {
        int p = puls;
        if (s->glitch_rest > 0) { p = !p; s->glitch_rest--; }
        else if (st->glitch_rate > 0 && zufall01() < st->glitch_rate) {
            s->glitch_rest = (int)(zufall() % (unsigned)st->glitch_max_ticks);
            p = !p;
        }
        dcf77_zeit_t z;
        if (dcf77_tick(&s->dek, p != 0, &z)) {
            s->meldungen++;
            s->letzte = z;
            /* Zeitpunkt: Sekundenbeginn laut Dekoder gegen echte Minutenmarke.
             * Erlaubt: Entprellung (30 ms) + Jitter + Taktfehler über ca. 140 ms */
            double beginn = s->tick_ms - (dcf77_ticks_seit_sekundenbeginn(&s->dek) + DCF77_ENTPRELL) *
                                             DCF77_TICK_MS * st->takt;
            double versatz = beginn - marke_ms;
            if (versatz < -60 || versatz > 60) {
                s->falsch++;
                printf("  Meldung zur falschen Zeit: %.0f ms neben der Minutenmarke\n", versatz);
            }
            if (!dcf77_gleich(&z, &erwartet_bei_marke)) {
                s->falsch++;
                printf("  falsche Zeit gemeldet: %02u:%02u %02u.%02u.%02u, erwartet %02u:%02u\n",
                       z.stunde, z.minute, z.tag, z.monat, z.jahr,
                       erwartet_bei_marke.stunde, erwartet_bei_marke.minute);
            }
        }
        s->tick_ms += DCF77_TICK_MS * st->takt;
    }
}

static double flanke(double t, const stoerung_t *st)
{
    return t + (st->jitter_ms > 0 ? (zufall01() * 2 - 1) * st->jitter_ms : 0);
}

/* Sendet eine Minute, deren Bits die Zeit „z“ beschreiben (gültig ab der
 * Minutenmarke am Ende dieser Minute). */
static void sende_minute(sim_t *s, const dcf77_zeit_t *z, const stoerung_t *st)
{
    uint8_t bits[8];
    kodiere(z, bits);
    int sekunden = st->schaltsekunde ? 60 : 59;
    for (int sek = 0; sek < sekunden; sek++) {
        int b = sek < 59 ? hole(bits, sek) : 0;
        double dauer = b ? 200 : 100;
        if (st->bitfehler_rate > 0 && zufall01() < st->bitfehler_rate) {
            dauer = (zufall() & 1) ? 300 - dauer : 150; /* vertauscht oder mehrdeutig */
        }
        double start = s->zeit_ms;
        if (st->ausfall_rate > 0 && zufall01() < st->ausfall_rate) {
            abschnitt(s, start + 1000, 0, st);
        } else {
            double a = flanke(start, st), e = flanke(start + dauer, st);
            abschnitt(s, a, 0, st);
            abschnitt(s, e, 1, st);
            abschnitt(s, start + 1000, 0, st);
        }
        s->zeit_ms = start + 1000;
    }
    /* Sekunde 59 (bzw. 60): keine Absenkung */
    abschnitt(s, s->zeit_ms + 1000, 0, st);
    s->zeit_ms += 1000;
    erwartet_bei_marke = *z;
    marke_ms = s->zeit_ms;
}

/* Startet mit zufälliger Phase mitten in einer Minute und sendet n Minuten */
static void sim_start(sim_t *s, uint32_t saat)
{
    memset(s, 0, sizeof(*s));
    dcf77_init(&s->dek);
    zufall_zustand = saat;
    s->zeit_ms = 0;
    s->tick_ms = zufall01() * DCF77_TICK_MS;
}

/* Der erste Puls nach der Marke (Sekunde 0) löst die Meldung aus; deshalb
 * nach der letzten Minute noch einen Sekundenbeginn senden. */
static void sende_abschluss(sim_t *s, const stoerung_t *st)
{
    double start = s->zeit_ms;
    abschnitt(s, start + 100, 1, st);
    abschnitt(s, start + 1000, 0, st);
    s->zeit_ms += 1000;
}

static dcf77_zeit_t zeit(int jahr, int monat, int tag, int wt, int std, int min, int mesz)
{
    dcf77_zeit_t z = {(uint8_t)min, (uint8_t)std, (uint8_t)tag, (uint8_t)wt,
                      (uint8_t)monat, (uint8_t)jahr, mesz != 0};
    return z;
}

/* --- Testfälle --------------------------------------------------------------- */

static void test_sauberes_signal(void)
{
    printf("Sauberes Signal, Start mitten in einer Minute\n");
    sim_t s;
    sim_start(&s, 7);
    /* Rest einer Minute ohne Puls-Sync: halbe Minute Pause wie nach dem Einschalten */
    abschnitt(&s, 30000, 0, &SAUBER);
    s.zeit_ms = 30000;
    dcf77_zeit_t z = zeit(26, 10, 4, 7, 21, 15, 1);
    for (int m = 0; m < 5; m++) {
        sende_minute(&s, &z, &SAUBER);
        dcf77_plus_minute(&z);
    }
    sende_abschluss(&s, &SAUBER);
    PRUEFE(s.falsch == 0, "%d falsche Meldungen", s.falsch);
    /* Minute 1 synchronisiert erst (Rahmenbeginn), Minute 2 ist die erste
     * vollständige, ab Minute 3 Plausibilität → Meldungen für 3, 4, 5 */
    PRUEFE(s.meldungen == 3, "%d Meldungen statt 3", s.meldungen);
    PRUEFE(s.letzte.stunde == 21 && s.letzte.minute == 19, "letzte Meldung %02u:%02u",
           s.letzte.stunde, s.letzte.minute);
}

static void test_takt(double takt)
{
    printf("Taktabweichung der MCU %+.0f %%\n", (takt - 1) * 100);
    sim_t s;
    sim_start(&s, 11);
    stoerung_t st = SAUBER;
    st.takt = takt;
    st.jitter_ms = 5;
    dcf77_zeit_t z = zeit(26, 12, 31, 4, 23, 57, 0);
    for (int m = 0; m < 5; m++) {
        sende_minute(&s, &z, &st);
        dcf77_plus_minute(&z);
    }
    sende_abschluss(&s, &st);
    PRUEFE(s.falsch == 0, "%d falsche Meldungen", s.falsch);
    PRUEFE(s.meldungen >= 3, "nur %d Meldungen", s.meldungen);
    /* über Mitternacht und Jahreswechsel: 23:57 31.12.26 + 4 = 00:01 01.01.27 */
    PRUEFE(s.letzte.jahr == 27 && s.letzte.monat == 1 && s.letzte.tag == 1 && s.letzte.minute == 1 &&
           s.letzte.wochentag == 5, "Jahreswechsel falsch: %02u.%02u.%02u wt %u %02u:%02u",
           s.letzte.tag, s.letzte.monat, s.letzte.jahr, s.letzte.wochentag, s.letzte.stunde, s.letzte.minute);
}

static void test_glitches(void)
{
    const int laeufe = 100;
    printf("Kurze Störimpulse (10–20 ms, 1 je Sekunde) + ±10 ms Jitter, %d Läufe à 6 Minuten\n", laeufe);
    int erfolgreich = 0, falsch = 0, schalttag_ok = 1;
    for (int saat = 1; saat <= laeufe; saat++) {
        sim_t s;
        sim_start(&s, (uint32_t)saat);
        stoerung_t st = SAUBER;
        st.glitch_rate = 0.01;
        st.glitch_max_ticks = 2;
        st.jitter_ms = 10;
        dcf77_zeit_t z = zeit(28, 2, 28, 1, 23, 58, 0);
        for (int m = 0; m < 6; m++) {
            sende_minute(&s, &z, &st);
            dcf77_plus_minute(&z);
        }
        sende_abschluss(&s, &st);
        falsch += s.falsch;
        if (s.meldungen >= 1) {
            erfolgreich++;
            /* Schaltjahr: letzte Meldung liegt am 29.02.28 */
            if (!(s.letzte.tag == 29 && s.letzte.monat == 2)) schalttag_ok = 0;
        }
    }
    printf("  %d von %d Läufen synchronisiert, %d falsche Meldungen\n", erfolgreich, laeufe, falsch);
    PRUEFE(falsch == 0, "%d falsche Meldungen", falsch);
    PRUEFE(erfolgreich >= laeufe * 8 / 10, "nur %d von %d Läufen synchronisiert", erfolgreich, laeufe);
    PRUEFE(schalttag_ok, "Schalttag falsch");
}

static void test_einzelner_bitfehler(void)
{
    printf("Ein vertauschtes Bit in einer Minute: diese Minute wird verworfen\n");
    for (int bitnr = 21; bitnr <= 58; bitnr++) {
        dcf77_zeit_t z = zeit(26, 6, 15, 1, 12, 0, 1);
        uint8_t bits[8];
        kodiere(&z, bits);
        setze(bits, bitnr, !hole(bits, bitnr));
        dcf77_zeit_t aus;
        PRUEFE(!dcf77_dekodiere(bits, &aus), "Bitfehler in Bit %d nicht erkannt", bitnr);
    }
}

static void test_zeitumstellung(void)
{
    printf("Umstellung MEZ -> MESZ (01:59 MEZ -> 03:00 MESZ)\n");
    sim_t s;
    sim_start(&s, 31);
    dcf77_zeit_t z = zeit(27, 3, 28, 7, 1, 56, 0);
    for (int m = 0; m < 4; m++) {
        sende_minute(&s, &z, &SAUBER);
        dcf77_plus_minute(&z);
    } /* gesendet: 01:56 … 01:59 MEZ */
    z = zeit(27, 3, 28, 7, 3, 0, 1);
    for (int m = 0; m < 4; m++) {
        sende_minute(&s, &z, &SAUBER);
        dcf77_plus_minute(&z);
    }
    sende_abschluss(&s, &SAUBER);
    PRUEFE(s.falsch == 0, "%d falsche Meldungen", s.falsch);
    PRUEFE(s.letzte.mesz && s.letzte.stunde == 3 && s.letzte.minute == 3, "nach Umstellung %02u:%02u mesz=%d",
           s.letzte.stunde, s.letzte.minute, s.letzte.mesz);
}

static void test_schaltsekunde(void)
{
    printf("Minute mit Schaltsekunde wird verworfen, danach normal weiter\n");
    sim_t s;
    sim_start(&s, 41);
    dcf77_zeit_t z = zeit(26, 12, 31, 4, 0, 57, 0);
    for (int m = 0; m < 6; m++) {
        stoerung_t st = SAUBER;
        st.schaltsekunde = (m == 3);
        sende_minute(&s, &z, &st);
        dcf77_plus_minute(&z);
    }
    sende_abschluss(&s, &SAUBER);
    PRUEFE(s.falsch == 0, "%d falsche Meldungen", s.falsch);
    PRUEFE(s.meldungen >= 1, "keine Meldung nach der Schaltsekunde");
}

static void test_kein_signal(void)
{
    printf("Kein Signal (Dauerpegel) und Dauerrauschen: keine Meldung\n");
    sim_t s;
    sim_start(&s, 53);
    abschnitt(&s, 600000, 0, &SAUBER);
    abschnitt(&s, 1200000, 1, &SAUBER);
    stoerung_t rauschen = SAUBER;
    rauschen.glitch_rate = 0.5;
    rauschen.glitch_max_ticks = 30;
    abschnitt(&s, 4800000, 0, &rauschen);
    PRUEFE(s.meldungen == 0, "%d Meldungen ohne Signal", s.meldungen);
}

static void test_monte_carlo(void)
{
    const int minuten = 20000;
    printf("Monte-Carlo: %d Minuten mit zufälligen Störungen aller Art\n", minuten);
    sim_t s;
    sim_start(&s, 12345);
    dcf77_zeit_t z = zeit(26, 1, 1, 4, 0, 0, 0);
    int gesendet_sauber = 0;
    for (int m = 0; m < minuten; m++) {
        stoerung_t st = SAUBER;
        /* jede Minute andere Bedingungen, von sauber bis schwer gestört */
        double stufe = zufall01();
        st.takt = 0.93 + 0.14 * zufall01();
        st.jitter_ms = 20 * stufe;
        st.glitch_rate = 0.02 * stufe * stufe;
        st.glitch_max_ticks = 1 + (int)(5 * stufe);
        st.ausfall_rate = 0.02 * stufe;
        st.bitfehler_rate = 0.02 * stufe;
        if (stufe < 0.3) gesendet_sauber++;
        sende_minute(&s, &z, &st);
        dcf77_plus_minute(&z);
    }
    sende_abschluss(&s, &SAUBER);
    printf("  %d Meldungen, %d falsch (%d der Minuten nur leicht gestört)\n", s.meldungen, s.falsch,
           gesendet_sauber);
    PRUEFE(s.falsch == 0, "%d falsche Zeiten gemeldet", s.falsch);
    PRUEFE(s.meldungen > minuten / 20, "zu wenige Meldungen: %d", s.meldungen);
}

static void test_plus_minute(void)
{
    printf("Minutenrechnung über Monats- und Jahresgrenzen\n");
    struct { dcf77_zeit_t a, b; } faelle[] = {
        {zeit(26, 4, 30, 4, 23, 59, 1), zeit(26, 5, 1, 5, 0, 0, 1)},
        {zeit(27, 2, 28, 7, 23, 59, 0), zeit(27, 3, 1, 1, 0, 0, 0)},
        {zeit(28, 2, 28, 1, 23, 59, 0), zeit(28, 2, 29, 2, 0, 0, 0)},
        {zeit(99, 12, 31, 4, 23, 59, 0), zeit(0, 1, 1, 5, 0, 0, 0)},
    };
    for (unsigned i = 0; i < sizeof(faelle) / sizeof(faelle[0]); i++) {
        dcf77_zeit_t t = faelle[i].a;
        dcf77_plus_minute(&t);
        PRUEFE(dcf77_gleich(&t, &faelle[i].b), "Fall %u: %02u.%02u.%02u %02u:%02u", i, t.tag, t.monat, t.jahr,
               t.stunde, t.minute);
    }
}

int main(void)
{
    test_plus_minute();
    test_einzelner_bitfehler();
    test_sauberes_signal();
    /* Datenblatt Tabelle 33-4: ±3,5 % (1,8–5,5 V, 0–70 °C); Test mit ±5 % */
    test_takt(0.95);
    test_takt(1.05);
    test_glitches();
    test_zeitumstellung();
    test_schaltsekunde();
    test_kein_signal();
    test_monte_carlo();
    printf("\n%d Prüfungen, %d Fehler\n", pruefungen, fehler);
    return fehler ? 1 : 0;
}
