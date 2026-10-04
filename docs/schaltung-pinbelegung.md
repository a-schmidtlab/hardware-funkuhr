# Pinbelegung Funkuhr Rev. A

Automatisch erzeugt aus `hw/funkuhr.py` (`make` in `hw/`). Nicht von Hand ändern.

Für jeden IC, Transistor und Stecker: welcher Pin hängt an welchem Netz.

## D1 – BAT54

| Pin | Name | Netz |
|---|---|---|
| 1 | A | V5_EXT |
| 2 | NC | nicht angeschlossen |
| 3 | K | VSYS |

## D2 – rot 3mm

| Pin | Name | Netz |
|---|---|---|
| 1 | K | KATHODE_7 |
| 2 | A | SEG_A |

## D3 – rot 3mm

| Pin | Name | Netz |
|---|---|---|
| 1 | K | KATHODE_7 |
| 2 | A | SEG_B |

## D4 – rot 3mm

| Pin | Name | Netz |
|---|---|---|
| 1 | K | KATHODE_7 |
| 2 | A | SEG_C |

## D5 – rot 3mm

| Pin | Name | Netz |
|---|---|---|
| 1 | K | KATHODE_7 |
| 2 | A | SEG_D |

## D6 – rot 3mm

| Pin | Name | Netz |
|---|---|---|
| 1 | K | KATHODE_7 |
| 2 | A | SEG_E |

## DS1 – SC08-11SURKWA

Stellvertretend für alle sechs Ziffern; die anderen unterscheiden sich nur im Kathodennetz (KATHODE_1 … KATHODE_6).

| Pin | Name | Netz |
|---|---|---|
| 1 | a | SEG_A |
| 2 | f | SEG_F |
| 3 | K | KATHODE_1 |
| 4 | e | SEG_E |
| 5 | K | KATHODE_1 |
| 6 | NC | – |
| 9 | DP | SEG_DP |
| 10 | d | SEG_D |
| 11 | K | KATHODE_1 |
| 12 | c | SEG_C |
| 13 | g | SEG_G |
| 14 | b | SEG_B |
| 16 | K | KATHODE_1 |

## J1 – USB-C 5V

| Pin | Name | Netz |
|---|---|---|
| A5 | CC1 | USB_CC1 |
| A9 | VBUS | V5_EXT |
| B5 | CC2 | USB_CC2 |
| B9 | VBUS | V5_EXT |
| SH | SHIELD | GND |
| A12 | GND | GND |
| B12 | GND | GND |

## J2 – ISP

| Pin | Name | Netz |
|---|---|---|
| 1 | Pin_1 | TASTER_2 |
| 2 | Pin_2 | V5_EXT |
| 3 | Pin_3 | TASTER_3 |
| 4 | Pin_4 | TASTER_1 |
| 5 | Pin_5 | RESET |
| 6 | Pin_6 | GND |

## J3 – UART

| Pin | Name | Netz |
|---|---|---|
| 1 | Pin_1 | GND |
| 2 | Pin_2 | nicht angeschlossen |
| 3 | Pin_3 | V5_EXT |
| 4 | Pin_4 | UART_TXD |
| 5 | Pin_5 | UART_RXD |
| 6 | Pin_6 | UART_DTR |

## J4 – DCF77-Modul

| Pin | Name | Netz |
|---|---|---|
| 1 | Pin_1 | 3V3_DCF |
| 2 | Pin_2 | GND |
| 3 | Pin_3 | MODUL_OUT |
| 4 | Pin_4 | MODUL_EN |

## Q1 – AO3401A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | V5_EXT |
| 2 | S | VSYS |
| 3 | D | VBAT_RAW |

## Q2 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_1 |
| 2 | S | GND |
| 3 | D | KATHODE_1 |

## Q3 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_2 |
| 2 | S | GND |
| 3 | D | KATHODE_2 |

## Q4 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_3 |
| 2 | S | GND |
| 3 | D | KATHODE_3 |

## Q5 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_4 |
| 2 | S | GND |
| 3 | D | KATHODE_4 |

## Q6 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_5 |
| 2 | S | GND |
| 3 | D | KATHODE_5 |

## Q7 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_6 |
| 2 | S | GND |
| 3 | D | KATHODE_6 |

## Q8 – AO3400A

| Pin | Name | Netz |
|---|---|---|
| 1 | G | STELLE_7 |
| 2 | S | GND |
| 3 | D | KATHODE_7 |

## U1 – XC6206P332MR

| Pin | Name | Netz |
|---|---|---|
| 1 | GND | GND |
| 2 | VO | 3V3_DCF |
| 3 | VI | VSYS |

## U2 – ATmega328PB-A

| Pin | Name | Netz |
|---|---|---|
| 1 | PD3 | DCF_OUT |
| 2 | PD4 | MCU_SEG_A |
| 3 | PE0 | STELLE_6 |
| 4 | VCC | VSYS |
| 5 | GND | GND |
| 6 | PE1 | STELLE_7 |
| 7 | XTAL1/PB6 | STELLE_4 |
| 8 | XTAL2/PB7 | STELLE_5 |
| 9 | PD5 | MCU_SEG_B |
| 10 | PD6 | MCU_SEG_C |
| 11 | PD7 | MCU_SEG_D |
| 12 | PB0 | STELLE_1 |
| 13 | PB1 | STELLE_2 |
| 14 | PB2 | STELLE_3 |
| 15 | PB3 | TASTER_1 |
| 16 | PB4 | TASTER_2 |
| 17 | PB5 | TASTER_3 |
| 18 | AVCC | VSYS |
| 19 | PE2 | DCF_EN |
| 20 | AREF | AREF |
| 21 | GND | GND |
| 22 | PE3 | RESERVE |
| 23 | PC0 | MCU_SEG_E |
| 24 | PC1 | MCU_SEG_F |
| 25 | PC2 | MCU_SEG_G |
| 26 | PC3 | MCU_SEG_DP |
| 27 | PC4 | SDA |
| 28 | PC5 | SCL |
| 29 | ~{RESET}/PC6 | RESET |
| 30 | PD0 | MCU_RXD |
| 31 | PD1 | MCU_TXD |
| 32 | PD2 | RTC_SQW |

## U3 – DS3231SN

| Pin | Name | Netz |
|---|---|---|
| 1 | 32KHZ | nicht angeschlossen |
| 2 | VCC | VSYS |
| 3 | ~{INT}/SQW | RTC_SQW |
| 4 | ~{RST} | nicht angeschlossen |
| 5 | GND | GND |
| 6 | GND | GND |
| 7 | GND | GND |
| 8 | GND | GND |
| 9 | GND | GND |
| 10 | GND | GND |
| 11 | GND | GND |
| 12 | GND | GND |
| 13 | GND | GND |
| 14 | VBAT | V_BACKUP |
| 15 | SDA | SDA |
| 16 | SCL | SCL |
