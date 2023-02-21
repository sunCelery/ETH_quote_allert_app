<h1>ETH_quote_allert_app</h1>

<h2>Table of content</h2>

- [Description](#description)
- [Install](#install)
- [Usage](#usage)
- [To Do](#to-do)

## Description ##

** Program **

- **calculates in real time own ETH price (ETHUSDT futures price with substracting influence of BTC movement)**

- **alert if the own price has changed more than at 1%**

## Install ##
**Linux**
**To install the app run one of these blocks in terminal:**

- if poetry:
```
git clone https://github.com/sunCelery/ETH_quote_allert_app.git && \
cd ETH_quote_allert_app && \
poetry install
```

- elif pip:
```
git clone https://github.com/sunCelery/ETH_quote_allert_app.git && \
cd ETH_quote_allert_app && \
python -m venv .venv && source .venv/bin/activate && \
python -m pip install --upgrade pip && pip install .
```

**Windows:**
**after you clone repository go to the folder and run command in Your terminal:**

```
py -m venv venv && venv\Scripts\activate ^
py -m pip install --upgrade pip && pip install .
```
<em>probably instead of 'py' You should type 'python' or 'python3' depends of Your envirement variable settings</em>

## Usage ##
**To launch the app run one of these blocks in terminal**

**Linux**
- if poetry:
```
poetry run python main.py
```
- else:
```
python main.py
```
**Windows**
```
python main.py
```

## To Do ##

- [await] get rid off god-object
- [await] add doc-string to the class
- [await] split out to more functions and methods and probably classes to follow up SOLID principles
- [await] probably make pure functions and methods from these ones
