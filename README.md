# Interactive WIW visualization

This provides a browser app for visualizing the WIW network of 
[BREATH](https://github.com/rbouckaert/BREATH) trees.

---
## Installation

Requires a python installation.
The instructions below should be up to date when downloading the latest release source code and 
unzipping it.
Open a terminal and `cd` into the downloaded (and unzipped) directory.

When cloning the repository instead, some requirements and new features might not be fully 
functioning without additional tinkering and package installation.

Create a python virtual environment named `appenv` with
```bash
python -m venv appenv
```
Activate this environment
```bash
source appenv/bin/activate
```
Now we have to install the required packages inside of this environment with: 
```bash
pip install -r requirements.txt
```
Then you can execute the app with
```bash
python run.py
```
This will host the app in your browser of choice at
[http://127.0.0.1:8050/](http://127.0.0.1:8050/).

You can find an example input file at
[the first release](https://github.com/Lars-B/interactive-wiw/releases/download/v1.0.0/Filter-roetzer40.trees)
, download this file and upload it within the app.
