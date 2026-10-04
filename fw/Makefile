# Firmware Funkuhr
#   make test   Host-Tests (gcc, mit Sanitizern)
#   make avr    Testübersetzung der Module für den ATmega328PB (Größe prüfen)

CC_HOST := gcc
CFLAGS_HOST := -std=c99 -Wall -Wextra -Werror -O1 -g -fsanitize=address,undefined
# Firmware-Quellen zusätzlich streng (Typumwandlungen zählen auf dem 8-Bit-AVR)
CFLAGS_SRC := $(CFLAGS_HOST) -Wconversion

DFP := $(HOME)/.local/share/avr-dfp/ATmega_DFP-3.6.299
CC_AVR := avr-gcc
CFLAGS_AVR := -mmcu=atmega328pb -B $(DFP)/gcc/dev/atmega328pb -I $(DFP)/include \
              -std=c99 -Wall -Wextra -Werror -Wconversion -Os

QUELLEN := src/dcf77.c
BUILD := build

.PHONY: test avr clean

test: $(BUILD)/test_dcf77
	./$(BUILD)/test_dcf77

$(BUILD)/test_dcf77: tests/test_dcf77.c $(QUELLEN) src/dcf77.h
	mkdir -p $(BUILD)
	$(CC_HOST) $(CFLAGS_SRC) -c -o $(BUILD)/dcf77_host.o src/dcf77.c
	$(CC_HOST) $(CFLAGS_HOST) -o $@ tests/test_dcf77.c $(BUILD)/dcf77_host.o

avr: $(QUELLEN) src/dcf77.h
	mkdir -p $(BUILD)
	$(CC_AVR) $(CFLAGS_AVR) -c -o $(BUILD)/dcf77.o src/dcf77.c
	avr-size $(BUILD)/dcf77.o

clean:
	rm -rf $(BUILD)
