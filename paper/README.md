# Manuscript

This directory contains the manuscript source for the paper associated with this software project.

The manuscrip is written in Quarto Markdown and rendered to DOCX for journal submission.
A PDF version can also be generated.

## Requirements

- [Quarto](https://quarto.org/)
- Python dependencies for manuscript post-processing (this is for adding line numbers)
    - The lxml package needs to be installed for the processing script

## Building

Build both DOCX and PDF:

```bash
make
```

Other make targets exist:

- `docx` just docx without postprocessing
- `pdf` just pdf
- `open` will build and open the docx file with line numbers
- `clean` removes build directory

## Files

- .qmd is the manuscrip
- references.bib is the bibliography
- journal-template.docx is a word template
- `add_line_numbers.py` is a script for postprocessing of docx files
- figures/ for images
- build/ is ignored by git and contains the output paper files

