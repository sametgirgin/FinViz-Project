import pandas as pd
import streamlit as st
from finvizfinance.crypto import Crypto

st.set_page_config(page_title="Crypto", layout="wide")

st.title("Crypto")
st.caption("Live crypto performance data from FinViz.")


@st.cache_data(show_spinner=False, ttl=5 * 60)
def _load_crypto() -> pd.DataFrame:
    crypto = Crypto()
    df = crypto.performance()
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


with st.spinner("Loading crypto data from FinViz..."):
    crypto_df = _load_crypto()

if crypto_df.empty:
    st.info("Crypto data unavailable right now.")
else:
    lower_cols = {str(c).strip().lower(): c for c in crypto_df.columns}
    symbol_col = (
        lower_cols.get("ticker")
        or lower_cols.get("symbol")
        or lower_cols.get("crypto")
        or lower_cols.get("name")
        or list(crypto_df.columns)[0]
    )
    options = crypto_df[symbol_col].astype(str).dropna().unique().tolist()
    selected = st.selectbox("Crypto", options, key="crypto_choice_page")

    row = crypto_df[crypto_df[symbol_col].astype(str) == str(selected)]
    if not row.empty:
        st.dataframe(row, use_container_width=True, height=140)
    st.dataframe(crypto_df, use_container_width=True, height=520)
