# Developer Guide

This page contains information for developers working on Interactive WIW Visualization.

## Running from Source

Create and activate a virtual environment:

```bash
python -m venv appenv
source appenv/bin/activate
```

Install the application and dependencies (using `-e` to track local changes):

```bash
pip install -e /path/to/contagion
```

Launch the application in debug mode:

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:8050/
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

Build the executable form the `contagion.spec` file:

```bash
pyinstaller contagion.spec
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
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller
          pip install -e .

      - name: Build executable
        run: |
          pyinstaller contagion.spec
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: CONTAGION-${{ runner.os }}-${{ runner.arch }}
          path: |
            dist/CONTAGION
            dist/CONTAGION.exe
```

---
