# Developer Guide

This page contains information for developers working on Interactive WIW Visualization.

## Running from Source

Create and activate a virtual environment:

```bash
python -m venv appenv
source appenv/bin/activate
```

Install the application and dependencies:

```bash
pip install -r requirements.txt
pip install .
```

Launch the application in debug mode:

```bash
python run.py
```

or alternatively, launch the packaging version: 

```bash
python spread_viz.py
```

The application will be available at:

```text
http://127.0.0.1:8050/
```

or at

```text
http://127.0.0.1:12712/
```

---

## Building Executables

Standalone executables are built with PyInstaller.

The build process collects the Dash application and all required assets into a single executable.

### Local Build

Install build dependencies:

```bash
pip install pyinstaller
```

Build the executable:

```bash
pyinstaller \
  --onefile \
  spread_viz.py \
  --collect-all dash_cytoscape \
  --collect-all dash_iconify \
  --collect-all dash_bootstrap_templates \
  --collect-all wiw_app \
  --hidden-import=dash.backends._flask
```

The resulting executable will be placed in:

```text
dist/
```

---

## GitHub Release Builds

Executables for all supported platforms are generated through GitHub Actions.

The workflow builds on:

* Ubuntu
* Windows
* Intel macOS
* Apple Silicon macOS

### Current Build Workflow

```yaml
name: Build Executable all

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
          - macos-latest
          - macos-15-large

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install .
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --onefile spread_viz.py \
            --collect-all dash_cytoscape \
            --collect-all dash_iconify \
            --collect-all dash_bootstrap_templates \
            --collect-all wiw_app \
            --hidden-import=dash.backends._flask

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: SpreadViz-${{ runner.os }}-${{ runner.arch }}
          path: |
            dist/spread_viz
            dist/spread_viz.exe
```

---
