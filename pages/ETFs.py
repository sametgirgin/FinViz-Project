import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETFs", layout="wide")

st.title("ETFs")


@st.cache_data(show_spinner=False)
def _load_etfs() -> pd.DataFrame:
    try:
        df = pd.read_csv("etf_list.csv")
    except FileNotFoundError:
        return pd.DataFrame()
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


with st.spinner("Loading ETF list..."):
    etf_df = _load_etfs()

ticker_col = "Ticker" if "Ticker" in etf_df.columns else None
company_col = None
for col in etf_df.columns:
    if str(col).lower() in {"company", "company name"}:
        company_col = col
        break

if etf_df.empty or ticker_col is None:
    st.info("ETF list unavailable right now.")
else:
    if company_col:
        options = etf_df.apply(lambda r: f"{r[ticker_col]} — {r[company_col]}", axis=1).tolist()
    else:
        options = etf_df[ticker_col].astype(str).tolist()

    selected = st.selectbox("ETF Ticker", options, key="etf_choice_page")
    st.markdown(f"**Selected ETF:** `{selected.split(' — ')[0]}`")
