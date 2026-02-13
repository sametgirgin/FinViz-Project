import re
from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview

st.set_page_config(page_title="Stock", layout="wide")

st.title("Stock")
st.caption("Fundamentals, description, ratings, news, and insider trades via finvizfinance.")

st.markdown(
    """
    <style>
    .metric-label { font-size: 0.8rem; color: #6b7280; }
    .section-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _is_probably_ticker(text: str) -> bool:
    t = text.strip().upper()
    if not t or " " in t:
        return False
    return bool(re.fullmatch(r"[A-Z0-9.\-]{1,6}", t))


def _call_first(obj: Any, candidates: list[str], *args: Any, **kwargs: Any) -> Any:
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)(*args, **kwargs)
    raise AttributeError(f"None of {candidates} exist on {type(obj)}")


@st.cache_data(show_spinner=False, ttl=60 * 60)
def _load_all_tickers() -> pd.DataFrame:
    foverview = Overview()
    try:
        df = foverview.screener_view(order="Ticker", limit=100000, verbose=0)
    except TypeError:
        df = foverview.ScreenerView(order="ticker", limit=-1, verbose=0)
    return df


def _find_matches(df: pd.DataFrame, company: str) -> pd.DataFrame:
    company_col = None
    ticker_col = None
    for col in df.columns:
        cl = str(col).lower()
        if cl in {"company", "company name"}:
            company_col = col
        if cl == "ticker":
            ticker_col = col

    if company_col is None or ticker_col is None:
        return pd.DataFrame()

    mask = df[company_col].astype(str).str.contains(company, case=False, na=False)
    matches = df.loc[mask, [ticker_col, company_col]].drop_duplicates()
    matches.columns = ["Ticker", "Company"]
    return matches


@st.cache_data(show_spinner=False, ttl=15 * 60)
def _load_stock_data(ticker: str) -> dict:
    stock = finvizfinance(ticker)

    fundament = _call_first(stock, ["ticker_fundament", "TickerFundament"])
    description = _call_first(stock, ["ticker_description", "TickerDescription"])
    outer_ratings = _call_first(stock, ["ticker_outer_ratings", "TickerOuterRatings"])
    news = _call_first(stock, ["ticker_news", "TickerNews"])
    insider = _call_first(stock, ["ticker_inside_trader", "TickerInsideTrader"])

    return {
        "fundament": fundament,
        "description": description,
        "outer_ratings": outer_ratings,
        "news": news,
        "insider": insider,
    }


def _chart_url(stock: Any, timeframe: str) -> Optional[str]:
    for name in ["ticker_charts", "TickerCharts"]:
        if hasattr(stock, name):
            fn: Callable[..., Any] = getattr(stock, name)
            try:
                return fn(timeframe=timeframe, charttype="advanced", urlonly=True)
            except TypeError:
                try:
                    return fn(timeframe, "advanced", "", True)
                except Exception:
                    return fn()
    return None


st.subheader("Search")
with st.form("search_form"):
    company_name = st.text_input("Company name", placeholder="Apple Inc.")
    ticker_override = st.text_input("Ticker (optional)", placeholder="AAPL")
    submitted = st.form_submit_button("Stock")

st.divider()
st.caption("Tip: Enter a ticker directly to skip lookup.")

if "matches" in st.session_state:
    matches = st.session_state["matches"]
    if not matches.empty:
        options = matches.apply(lambda r: f"{r['Ticker']} — {r['Company']}", axis=1).tolist()
        selected = st.selectbox("Ticker / Company", options, key="ticker_choice")
        button_label = "Use selected ticker" if "ticker" not in st.session_state else "Switch ticker"
        if st.button(button_label):
            st.session_state["ticker"] = selected.split(" — ")[0]

if submitted:
    st.session_state.pop("matches", None)
    st.session_state.pop("ticker", None)

    if ticker_override.strip():
        st.session_state["ticker"] = ticker_override.strip().upper()
    elif _is_probably_ticker(company_name):
        st.session_state["ticker"] = company_name.strip().upper()
    else:
        with st.spinner("Searching FinViz screener for matching companies..."):
            df = _load_all_tickers()
            matches = _find_matches(df, company_name)
            st.session_state["matches"] = matches
            if len(matches) == 1:
                st.session_state["ticker"] = matches.iloc[0]["Ticker"]

if "matches" in st.session_state and "ticker" not in st.session_state:
    matches = st.session_state["matches"]
    if matches.empty:
        st.error("No company matches found. Try a different name or enter a ticker.")

if "ticker" in st.session_state:
    ticker = st.session_state["ticker"]
    st.markdown(f"**Selected ticker:** `{ticker}`")
    if st.button("Load data"):
        with st.spinner("Fetching data from FinViz..."):
            data = _load_stock_data(ticker)
            stock = finvizfinance(ticker)
            chart_daily = _chart_url(stock, "daily")
            chart_weekly = _chart_url(stock, "weekly")
            chart_monthly = _chart_url(stock, "monthly")

        top_metrics = {}
        for k in ["Price", "Market Cap", "P/E", "EPS (ttm)", "Dividend %", "52W Range"]:
            if k in data["fundament"]:
                top_metrics[k] = data["fundament"][k]

        if top_metrics:
            cols = st.columns(min(6, len(top_metrics)))
            for col, (label, value) in zip(cols, top_metrics.items()):
                with col:
                    st.metric(label, value)

        tabs = st.tabs(["Overview", "Fundamentals", "Charts", "Ratings", "News", "Insider"])

        with tabs[0]:
            st.markdown('<div class="section-title">Description</div>', unsafe_allow_html=True)
            st.write(data["description"])

        with tabs[1]:
            st.markdown('<div class="section-title">Fundamentals</div>', unsafe_allow_html=True)
            fund_df = pd.DataFrame(list(data["fundament"].items()), columns=["Metric", "Value"])
            st.dataframe(fund_df, use_container_width=True, height=520)

        with tabs[2]:
            st.markdown('<div class="section-title">Charts</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for col, url, label in zip(cols, [chart_daily, chart_weekly, chart_monthly], ["Daily", "Weekly", "Monthly"]):
                with col:
                    if url:
                        st.image(url, caption=label, use_container_width=True)
                    else:
                        st.info(f"{label} chart unavailable")

        with tabs[3]:
            st.markdown('<div class="section-title">Outer Ratings</div>', unsafe_allow_html=True)
            st.dataframe(data["outer_ratings"], use_container_width=True, height=520)

        with tabs[4]:
            st.markdown('<div class="section-title">News</div>', unsafe_allow_html=True)
            st.dataframe(data["news"], use_container_width=True, height=520)

        with tabs[5]:
            st.markdown('<div class="section-title">Insider Trades</div>', unsafe_allow_html=True)
            st.dataframe(data["insider"], use_container_width=True, height=520)
