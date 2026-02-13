# FinViz Stock Snapshot (Streamlit)

A Streamlit app that fetches fundamentals, description, outer ratings, news, and insider trades for a stock using `finvizfinance`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Notes

- Search by company name. If multiple matches are found, select the correct ticker.
- You can always input the ticker directly to skip the lookup.
