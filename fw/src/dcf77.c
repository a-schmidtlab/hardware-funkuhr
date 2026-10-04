/*
 * DCF77-Dekoder, siehe dcf77.h.
 *
 * Bitbelegung einer Minute (PTB):
 *   0       Minutenbeginn, immer 0
 *   1–14    Wetter-/Katastrophenschutzdaten (nicht ausgewertet)
 *   15      Rufbit, 16 Ankündigung Zeitumstellung
 *   17, 18  Z1 = MESZ, Z2 = MEZ (genau eines gesetzt)
 *   19      Ankündigung Schaltsekunde
 *   20      Beginn der Zeitinformation, immer 1
 *   21–27   Minute BCD (1, 2, 4, 8, 10, 20, 40), 28 Parität P1 (21–28 gerade)
 *   29–34   Stunde BCD (1, 2, 4, 8, 10, 20),     35 Parität P2 (29–35 gerade)
 *   36–41   Tag BCD (1, 2, 4, 8, 10, 20)
 *   42–44   Wochentag (1, 2, 4)
 *   45–49   Monat BCD (1, 2, 4, 8, 10)
 *   50–57   Jahr BCD (1, 2, 4, 8, 10, 20, 40, 80), 58 Parität P3 (36–58 gerade)
 */
#include "dcf77.h"

/* Zeiten in Ticks (10 ms), gemessen ab dem entprellten Sekundenbeginn.
 * Der echte Beginn liegt DCF77_ENTPRELL (3) Ticks davor.
 *
 * Bitwert per Mehrheitsentscheidung statt Flankenmessung: Ein Störimpuls
 * kippt nur 1–2 Abtastwerte, eine verschobene Flanke ebenso.
 *   Anfangsfenster: Ticks 0–4  (real ca. 30–80 ms)   → Puls muss da sein
 *   Bitfenster:     Ticks 8–15 (real ca. 110–190 ms) → aktiv nur bei Bit 1
 * Die Fenster halten Abstand zu den Flanken bei 100 und 200 ms, auch bei
 * ±5 % Taktfehler und ±20 ms Jitter. Fensterlage und Schwellen sind per
 * Variantenvergleich in den Host-Tests gewählt (sim/ergebnisse-firmware.md). */
#define FENSTER_ANFANG_ENDE 5u
#define FENSTER_BIT_BEGINN 8u
#define FENSTER_BIT_ENDE 16u   /* Auswertung in diesem Tick */
#define ANFANG_MIN 3u          /* von 5 */
#define BIT_NULL_MAX 3u        /* von 8: höchstens 3 aktiv → Bit 0 */
#define BIT_EINS_MIN 5u        /* von 8: mindestens 5 aktiv → Bit 1; 4 = mehrdeutig */

#define SEKUNDE_MIN 90u  /* 0,9 s */
#define SEKUNDE_MAX 110u /* 1,1 s */
#define MINUTE_MIN 180u  /* 1,8 s: Lücke in Sekunde 59 */
#define MINUTE_MAX 220u  /* 2,2 s */
#define ZEITUEBERSCHREITUNG 250u /* 2,5 s ohne Puls = Signal weg */
#define MARKE_TOLERANZ 5u /* ±50 ms um die aus dem Sekundenraster erwartete Marke */

static bool bit(const uint8_t bits[8], uint8_t n)
{
    return ((unsigned)bits[n >> 3] >> (n & 7u)) & 1u;
}

static void setze_bit(uint8_t bits[8], uint8_t n, bool wert)
{
    if (wert) {
        bits[n >> 3] |= (uint8_t)(1u << (n & 7u));
    } else {
        bits[n >> 3] &= (uint8_t)~(1u << (n & 7u));
    }
}

/* Liest ein BCD-Feld; liefert 0xFF, wenn eine Ziffer > 9 ist. */
static uint8_t bcd(const uint8_t bits[8], uint8_t start, uint8_t anzahl)
{
    static const uint8_t gewicht[8] = {1, 2, 4, 8, 10, 20, 40, 80};
    uint8_t einer = 0, zehner = 0;
    for (uint8_t i = 0; i < anzahl; i++) {
        if (bit(bits, (uint8_t)(start + i))) {
            if (i < 4) {
                einer = (uint8_t)(einer + gewicht[i]);
            } else {
                zehner = (uint8_t)(zehner + gewicht[i]);
            }
        }
    }
    if (einer > 9 || zehner > 90) {
        return 0xFF;
    }
    return (uint8_t)(einer + zehner);
}

static bool paritaet_gerade(const uint8_t bits[8], uint8_t von, uint8_t bis)
{
    uint8_t summe = 0;
    for (uint8_t n = von; n <= bis; n++) {
        summe ^= (uint8_t)bit(bits, n);
    }
    return summe == 0;
}

static uint8_t tage_im_monat(uint8_t monat, uint8_t jahr)
{
    static const uint8_t tage[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (monat == 2 && (jahr % 4u) == 0) {
        return 29; /* 2000–2099: jedes durch 4 teilbare Jahr ist Schaltjahr */
    }
    return tage[monat - 1u];
}

bool dcf77_dekodiere(const uint8_t bits[8], dcf77_zeit_t *z)
{
    if (bit(bits, 0) || !bit(bits, 20)) {
        return false;
    }
    if (bit(bits, 17) == bit(bits, 18)) {
        return false;
    }
    if (!paritaet_gerade(bits, 21, 28) || !paritaet_gerade(bits, 29, 35) ||
        !paritaet_gerade(bits, 36, 58)) {
        return false;
    }
    dcf77_zeit_t t;
    t.minute = bcd(bits, 21, 7);
    t.stunde = bcd(bits, 29, 6);
    t.tag = bcd(bits, 36, 6);
    t.wochentag = bcd(bits, 42, 3);
    t.monat = bcd(bits, 45, 5);
    t.jahr = bcd(bits, 50, 8);
    t.mesz = bit(bits, 17);
    if (t.minute > 59 || t.stunde > 23 || t.monat < 1 || t.monat > 12 || t.jahr > 99 ||
        t.wochentag < 1 || t.wochentag > 7 || t.tag < 1 || t.tag > tage_im_monat(t.monat, t.jahr)) {
        return false;
    }
    *z = t;
    return true;
}

void dcf77_plus_minute(dcf77_zeit_t *z)
{
    if (++z->minute < 60) {
        return;
    }
    z->minute = 0;
    if (++z->stunde < 24) {
        return;
    }
    z->stunde = 0;
    z->wochentag = (uint8_t)(z->wochentag % 7u + 1u);
    if (++z->tag <= tage_im_monat(z->monat, z->jahr)) {
        return;
    }
    z->tag = 1;
    if (++z->monat <= 12) {
        return;
    }
    z->monat = 1;
    z->jahr = (uint8_t)((z->jahr + 1u) % 100u);
}

bool dcf77_gleich(const dcf77_zeit_t *a, const dcf77_zeit_t *b)
{
    return a->minute == b->minute && a->stunde == b->stunde && a->tag == b->tag &&
           a->wochentag == b->wochentag && a->monat == b->monat && a->jahr == b->jahr &&
           a->mesz == b->mesz;
}

void dcf77_init(dcf77_t *d)
{
    d->integrator = 0;
    d->pegel = false;
    d->seit_pulsbeginn = 0;
    d->pulsbeginn_bekannt = false;
    d->auswertung_laeuft = false;
    d->fenster_anfang = 0;
    d->fenster_bit = 0;
    d->rahmen_ticks = 0;
    d->letzte_sekunde = 0;
    d->bitnr = 0;
    for (uint8_t i = 0; i < 8; i++) {
        d->bits[i] = 0;
    }
    d->rahmen_ok = false; /* erst ab der ersten Minutenmarke */
    d->vorige_gueltig = false;
    d->kandidat_offen = false;
    d->kandidat_plausibel = false;
}

static void neuer_rahmen(dcf77_t *d)
{
    d->rahmen_ticks = 0;
    d->letzte_sekunde = 0;
    d->bitnr = 0;
    d->rahmen_ok = true;
}

/* Entprellter Beginn einer Absenkung */
static void pulsbeginn(dcf77_t *d)
{
    uint16_t abstand = d->seit_pulsbeginn;
    bool bekannt = d->pulsbeginn_bekannt;

    /* Zu früh nach dem letzten Sekundenbeginn: Störimpuls, ignorieren.
     * Weiter vom echten Sekundenbeginn aus zählen. */
    if (bekannt && abstand < SEKUNDE_MIN) {
        return;
    }
    d->seit_pulsbeginn = 0;
    d->pulsbeginn_bekannt = true;
    d->auswertung_laeuft = true;
    d->fenster_anfang = 0;
    d->fenster_bit = 0;
    d->kandidat_offen = false;

    if (!bekannt) {
        return;
    }
    if (abstand >= MINUTE_MIN && abstand <= MINUTE_MAX) {
        /* Minutenmarke: vorigen Rahmen auswerten; gemeldet wird erst, wenn
         * Sekunde 0 als Bit 0 erkannt ist (bit_auswerten). Die Marke muss
         * im Sekundenraster dieser Minute liegen: Sekunde 58 begann bei
         * letzte_sekunde, die mittlere Sekundenlänge ist letzte_sekunde / 58
         * (enthält den Taktfehler der MCU). */
        uint16_t erwartet_marke = (uint16_t)(d->letzte_sekunde + (2u * d->letzte_sekunde + 29u) / 58u);
        uint16_t ist = d->rahmen_ticks;
        bool im_raster = (ist + MARKE_TOLERANZ >= erwartet_marke) && (ist <= erwartet_marke + MARKE_TOLERANZ);
        dcf77_zeit_t neu;
        if (d->rahmen_ok && d->bitnr == 59 && im_raster && dcf77_dekodiere(d->bits, &neu)) {
            dcf77_zeit_t erwartet = d->vorige;
            dcf77_plus_minute(&erwartet);
            d->kandidat = neu;
            d->kandidat_plausibel = d->vorige_gueltig && dcf77_gleich(&erwartet, &neu);
            d->kandidat_offen = true;
        } else {
            d->vorige_gueltig = false;
        }
        neuer_rahmen(d);
    } else if (abstand > SEKUNDE_MAX) {
        d->rahmen_ok = false; /* fehlender Puls */
    } else {
        d->letzte_sekunde = d->rahmen_ticks;
    }
}

/* Ende des Bitfensters: Bitwert per Mehrheit. Liefert true, wenn damit eine
 * Minutenmarke bestätigt und eine geprüfte Zeit gemeldet wird. */
static bool bit_auswerten(dcf77_t *d, dcf77_zeit_t *zeit)
{
    bool gemeldet = false;
    bool gueltig = true;
    bool wert = false;

    if (d->fenster_anfang < ANFANG_MIN) {
        gueltig = false; /* kein echter Sekundenpuls */
    } else if (d->fenster_bit <= BIT_NULL_MAX) {
        wert = false;
    } else if (d->fenster_bit >= BIT_EINS_MIN) {
        wert = true;
    } else {
        gueltig = false; /* mehrdeutig */
    }

    if (d->kandidat_offen) {
        d->kandidat_offen = false;
        if (gueltig && !wert) {
            /* echte Minutenmarke: Sekunde 0 trägt immer Bit 0 */
            if (d->kandidat_plausibel) {
                *zeit = d->kandidat;
                gemeldet = true;
            }
            d->vorige = d->kandidat;
            d->vorige_gueltig = true;
        } else {
            d->vorige_gueltig = false;
        }
    }

    if (!gueltig || d->bitnr >= 59) {
        d->rahmen_ok = false; /* ungültiges Bit oder zu viele (Schaltsekunde) */
    } else if (d->rahmen_ok) {
        setze_bit(d->bits, d->bitnr, wert);
        d->bitnr++;
    }
    return gemeldet;
}

bool dcf77_tick(dcf77_t *d, bool puls, dcf77_zeit_t *zeit)
{
    bool gemeldet = false;

    if (d->seit_pulsbeginn < UINT16_MAX) {
        d->seit_pulsbeginn++;
    }
    if (d->rahmen_ticks < UINT16_MAX) {
        d->rahmen_ticks++;
    }
    if (d->pulsbeginn_bekannt && d->seit_pulsbeginn > ZEITUEBERSCHREITUNG) {
        /* Signal ausgefallen: alles verwerfen */
        d->pulsbeginn_bekannt = false;
        d->auswertung_laeuft = false;
        d->rahmen_ok = false;
        d->vorige_gueltig = false;
        d->kandidat_offen = false;
    }

    /* Entprellung per Integrator: Pegelwechsel erst nach DCF77_ENTPRELL
     * Ticks in die neue Richtung; Störungen bis 20 ms lösen keinen
     * Sekundenbeginn aus. */
    if (puls && d->integrator < DCF77_ENTPRELL) {
        d->integrator++;
    } else if (!puls && d->integrator > 0) {
        d->integrator--;
    }
    if (!d->pegel && d->integrator == DCF77_ENTPRELL) {
        d->pegel = true;
        pulsbeginn(d);
    } else if (d->pegel && d->integrator == 0) {
        d->pegel = false;
    }

    /* Abtastfenster nach dem Sekundenbeginn (Rohwerte, nicht entprellt) */
    if (d->auswertung_laeuft) {
        uint16_t i = d->seit_pulsbeginn;
        if (i < FENSTER_ANFANG_ENDE) {
            d->fenster_anfang = (uint8_t)(d->fenster_anfang + puls);
        } else if (i >= FENSTER_BIT_BEGINN && i < FENSTER_BIT_ENDE) {
            d->fenster_bit = (uint8_t)(d->fenster_bit + puls);
        }
        if (i + 1u >= FENSTER_BIT_ENDE) {
            d->auswertung_laeuft = false;
            gemeldet = bit_auswerten(d, zeit);
        }
    }
    return gemeldet;
}
