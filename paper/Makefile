NAME = interactiveWhoInfectedWhom

BUILD = build
QMD = $(NAME).qmd
DOCX = $(BUILD)/$(NAME).docx
FINAL = $(BUILD)/$(NAME)_final.docx
PDF = $(BUILD)/$(NAME).pdf

DOCX_TEMPLATE = journal-template.docx
BIB = references.bib

.PHONY: all docx pdf clean open

all: docx pdf

docx: $(FINAL)

pdf: $(PDF)

$(DOCX): $(QMD) $(BIB) $(DOCX_TEMPLATE)
	quarto render $(QMD) --to docx

$(FINAL): $(DOCX) add_line_numbers.py
	python add_line_numbers.py $(DOCX)

$(PDF): $(QMD) $(BIB)
	quarto render $(QMD) --to pdf

open: all
	open $(FINAL)

clean:
	rm -rf $(BUILD)