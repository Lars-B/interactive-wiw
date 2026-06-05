# Interactive WIW Visualization

Interactive browser-based visualization tool for exploring who-infected-whom (WIW) transmission networks.
Supports input from BREATH MCMC runs, Outbreaker2, and Transphylo.
Furthermore, you can uplaod a custom `csv` file to generate a graph, more detail can be found in documentation.

## Features

- Interactive network visualization
- Upload and compare multiple datasets from different programs
- Edge filtering, thresholding by posterior support, and styling
- Maximum Spanning Tree computation (currently only available for BREATH)
- Indirect infection network (currently only available for BREATH)
- Export graphs
- Browser-based interactive interface 

## Installation

Download the latest executable from the Releases page:

https://github.com/Lars-B/interactive-wiw/releases/latest

Available for:
- macOS (Intel and M)
- Linux
- Windows

## Quick Start

1. Launch the application.
2. Open the browser interface.
3. Upload the output of one supported application.
4. Explore the network interactively.

## Documentation

Full guidance on how to use the App is available at [docs](https://lars-b.github.io/interactive-wiw/).

## For Developers

See the developer documentation for:
- Running from source
- Building executables
- Project structure
- Contributing

## Bugs/Problems

If you find a bug, please submit an issue here, ideally with a minimal reproducable example of the probelm.
