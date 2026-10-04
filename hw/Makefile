# Schaltung als Code: SKiDL -> Netzliste, KiCad-Schaltplan, Prüfberichte
#
#   make          Netzliste + Schaltplan erzeugen, ERC (SKiDL und KiCad)
#   make pcb      neue Platinendatei aus der Netzliste (nur für den Start von Phase 6)
#   make clean    erzeugte Dateien löschen

PY      := .venv/bin/python
TOP     := funkuhr
OUT     := build

export KICAD10_SYMBOL_DIR    := /usr/share/kicad/symbols
export KICAD10_FOOTPRINT_DIR := /usr/share/kicad/footprints

.PHONY: all pcb clean

all: $(OUT)/$(TOP).net

$(OUT)/$(TOP).net: $(wildcard *.py)
	mkdir -p $(OUT)
	$(PY) $(TOP).py
	kicad-cli sch erc -o $(OUT)/$(TOP)-kicad-erc.rpt $(OUT)/$(TOP).kicad_sch
	kicad-cli sch export pdf -o $(OUT)/$(TOP).pdf $(OUT)/$(TOP).kicad_sch

pcb: $(OUT)/$(TOP).net
	.venv/bin/kinet2pcb -i $< -o $(OUT)/$(TOP).kicad_pcb -l $(KICAD10_FOOTPRINT_DIR)

clean:
	rm -rf $(OUT)
