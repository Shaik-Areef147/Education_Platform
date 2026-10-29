"""Styling helpers."""
import streamlit as st

CSS = """
<style>
  .block-container {padding-top: 1.4rem; max-width: 1280px;}
  [data-testid="stSidebar"] {background: #0f2a4a;}
  [data-testid="stSidebar"] * {color: #e8eef7;}
  [data-testid="stSidebar"] [data-baseweb="select"] * {color: #10233d;}
  [data-testid="stSidebar"] [data-baseweb="tag"] * {color: #ffffff;}
  .hero {background: linear-gradient(120deg,#0f2a4a 0%,#2a78d6 100%); color:#fff; padding: 26px 30px;
         border-radius: 16px; margin-bottom: 18px;}
  .hero h1 {margin:0; font-size: 1.9rem; color:#fff;}
  .hero p {margin:6px 0 0; opacity:.9; font-size: 1rem;}
  .kpi {background:#fff; border:1px solid #e3e8f0; border-left:5px solid #2a78d6; border-radius:12px;
        padding:14px 16px; box-shadow:0 1px 3px rgba(16,35,61,.06); height:100%;}
  .kpi .l {color:#5b6b82; font-size:.78rem; text-transform:uppercase; letter-spacing:.04em;}
  .kpi .v {color:#10233d; font-size:1.7rem; font-weight:700; line-height:1.25;}
  .kpi .s {color:#5b6b82; font-size:.8rem;}
  .insight {background:#fff; border:1px solid #e3e8f0; border-radius:12px; padding:14px 18px; margin-bottom:10px;}
  .insight b {color:#2a78d6;}
  h2, h3 {color:#10233d;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def kpi(col, label: str, value: str, sub: str = "", color: str = "#2a78d6") -> None:
    col.markdown(
        f'<div class="kpi" style="border-left-color:{color}"><div class="l">{label}</div>'
        f'<div class="v">{value}</div><div class="s">{sub}&nbsp;</div></div>', unsafe_allow_html=True)


def insight(text: str) -> None:
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)
