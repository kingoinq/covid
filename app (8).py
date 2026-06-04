# ============================================================
#  COVID-19: Mexico in Comparative Perspective
#  Role:         Health Economist, UNDP Latin American Bureau
#  Stakeholders: Mexican Ministry of Health, PAHO
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import requests, io, warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="COVID-19: Mexico in Comparative Perspective",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color palette — light theme ───────────────────────────────
BG        = "#F8FAFC"
CARD_BG   = "#FFFFFF"
PRIMARY   = "#0F172A"
SECONDARY = "#1E40AF"
ACCENT    = "#3B82F6"
SUCCESS   = "#059669"
WARNING   = "#D97706"
CRITICAL  = "#DC2626"
MUTED     = "#64748B"
BORDER    = "#E2E8F0"

# Different green shades for non-Mexico bars (Mexico themed)
BLUE_SHADES = [
    "#14532d",
    "#166534",
    "#15803d",
    "#16a34a",
    "#22c55e",
    "#4ade80",
    "#86efac",
]

COUNTRY_COLORS = {
    "Mexico":        CRITICAL,
    "Chile":         SUCCESS,
    "United States": "#2563eb",
    "Brazil":        "#0891b2",
    "Colombia":      "#4f46e5",
    "Argentina":     "#7c3aed",
    "Peru":          WARNING,
    "Germany":       "#64748b",
    "Spain":         "#db2777",
}
ALL_PEERS = [c for c in COUNTRY_COLORS if c != "Mexico"]

# ── CSS — white theme, Times New Roman ───────────────────────
st.markdown(f"""
<style>
  * {{ font-family: 'Times New Roman', Times, serif !important; }}

  .stApp {{ background-color: {BG}; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; }}

  .act-pill {{
    display: inline-block;
    background: {SECONDARY};
    color: white;
    padding: 3px 14px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 6px;
  }}
  .act-title {{
    color: {PRIMARY};
    font-size: 1.35rem;
    font-weight: 800;
    margin: 4px 0 0 0;
    line-height: 1.3;
  }}
  .section-question {{
    background: #EFF6FF;
    border-left: 4px solid {ACCENT};
    padding: 13px 18px;
    border-radius: 0 8px 8px 0;
    color: {SECONDARY};
    font-size: 1rem;
    font-weight: 600;
    margin: 14px 0 20px 0;
  }}
  .finding-box {{
    background: #FEF2F2;
    border-left: 4px solid {CRITICAL};
    padding: 13px 18px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0 10px 0;
  }}
  .finding-label {{
    color: {CRITICAL};
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin-bottom: 5px;
  }}
  .finding-text {{
    color: {PRIMARY};
    font-size: 0.93rem;
    line-height: 1.6;
    margin: 0;
  }}
  .implication-box {{
    background: #F0FDF4;
    border-left: 4px solid {SUCCESS};
    padding: 13px 18px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0 0 0;
  }}
  .implication-label {{
    color: {SUCCESS};
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin-bottom: 5px;
  }}
  .implication-text {{
    color: {PRIMARY};
    font-size: 0.93rem;
    line-height: 1.6;
    margin: 0;
  }}
  .exec-card {{
    background: {CARD_BG};
    border-radius: 10px;
    padding: 22px 20px;
    border-top: 4px solid {CRITICAL};
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    height: 100%;
  }}
  .exec-number {{
    color: {CRITICAL};
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin-bottom: 8px;
  }}
  .exec-text {{
    color: {PRIMARY};
    font-size: 0.92rem;
    line-height: 1.6;
    margin: 0;
  }}
  .conclusion-banner {{
    background: {PRIMARY};
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin: 16px 0;
  }}
  .conclusion-text {{
    color: white;
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.7;
    margin: 0;
    font-style: italic;
  }}
  .rec-card {{
    background: {CARD_BG};
    border-radius: 10px;
    padding: 20px;
    border-left: 4px solid {SECONDARY};
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 12px;
  }}
  .rec-title {{
    color: {SECONDARY};
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 6px;
  }}
  .rec-text {{
    color: {MUTED};
    font-size: 0.88rem;
    line-height: 1.6;
    margin: 0;
  }}
  #MainMenu {{ visibility: hidden; }}
  footer     {{ visibility: hidden; }}

  [data-testid="stSidebar"] {{
      background-color: white !important;
      border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] * {{
      color: {PRIMARY} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="tag"] {{
      background-color: {BORDER} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] [data-baseweb="input"] > div,
  [data-testid="stSidebar"] input {{
      background-color: white !important;
      border-color: {BORDER} !important;
      color: {PRIMARY} !important;
  }}
  [data-testid="stHeader"] {{
      background-color: {BG} !important;
  }}
  [data-testid="stToolbar"] {{
      background-color: {BG} !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Reusable HTML components ─────────────────────────────────
def act_header(number, title):
    st.markdown(
        f'<div class="act-pill">Act {number}</div>'
        f'<div class="act-title">{title}</div>',
        unsafe_allow_html=True)

def question_box(text):
    st.markdown(f'<div class="section-question">{text}</div>',
                unsafe_allow_html=True)

def finding_box(text):
    st.markdown(
        f'<div class="finding-box">'
        f'<div class="finding-label">What the data shows</div>'
        f'<p class="finding-text">{text}</p>'
        f'</div>', unsafe_allow_html=True)

def implication_box(text):
    st.markdown(
        f'<div class="implication-box">'
        f'<div class="implication-label">Why this matters</div>'
        f'<p class="implication-text">{text}</p>'
        f'</div>', unsafe_allow_html=True)

# ── Chart styles ──────────────────────────────────────────────
def style_plotly(fig, title=""):
    fig.update_layout(
        title=title, title_font_size=14,
        title_font_color=PRIMARY,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=PRIMARY,
        font_family="Times New Roman",
        margin=dict(t=50, b=10, l=10, r=10),
        yaxis=dict(gridcolor=BORDER, color=MUTED, linecolor=BORDER),
        xaxis=dict(gridcolor=BORDER, color=MUTED, linecolor=BORDER),
        legend=dict(orientation="h", y=-0.3, font_size=11, font_color=PRIMARY),
        hovermode="x unified"
    )
    return fig

def light_ax(ax, fig, horizontal=False):
    fig.patch.set_facecolor("white")
    ax.set_facecolor(BG)
    ax.tick_params(colors=PRIMARY, labelsize=9)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("serif")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(BORDER)
    if horizontal:
        ax.xaxis.grid(True, color=BORDER, linewidth=0.7)
    else:
        ax.yaxis.grid(True, color=BORDER, linewidth=0.7)
    ax.set_axisbelow(True)
    return ax

def bar_color_list(locations, highlight="Mexico"):
    non_mex   = [l for l in locations if l != highlight]
    shade_map = {loc: BLUE_SHADES[i % len(BLUE_SHADES)]
                 for i, loc in enumerate(non_mex)}
    return [CRITICAL if loc == highlight else shade_map[loc]
            for loc in locations]

# ── Data loading ──────────────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    r.raise_for_status()
    needed = [
        "iso_code","continent","location","date",
        "total_cases","total_deaths",
        "total_cases_per_million","total_deaths_per_million",
        "new_deaths_smoothed_per_million",
        "people_fully_vaccinated_per_hundred",
        "population","gdp_per_capita",
        "hospital_beds_per_thousand",
        "diabetes_prevalence",
        "cardiovasc_death_rate",
        "life_expectancy",
        "human_development_index",
    ]
    df = pd.read_csv(
        io.StringIO(r.text),
        usecols=lambda c: c in needed,
        parse_dates=["date"],
        low_memory=False
    )
    df = df[
        ~df["iso_code"].str.startswith("OWID", na=True) &
        df["continent"].notna()
    ].copy()
    return df

with st.spinner("Loading data..."):
    df_all = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<p style='color:{PRIMARY};font-weight:700;font-size:1rem;margin-bottom:2px;font-family:Times New Roman,serif;'>COVID-19 Analysis</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};font-size:0.82rem;margin-top:0;font-family:Times New Roman,serif;'>UNDP Health Economist Report</p>", unsafe_allow_html=True)
    st.divider()
    peers = st.multiselect(
        "Compare Mexico against:",
        options=ALL_PEERS,
        default=["United States","Brazil","Chile","Colombia","Peru"]
    )
    selected = ["Mexico"] + peers
    st.divider()
    min_d = df_all["date"].min().date()
    max_d = df_all["date"].max().date()
    date_range = st.date_input("Date range",
        value=(min_d, max_d), min_value=min_d, max_value=max_d)
    st.divider()
    st.caption("Source: Our World in Data  |  CC BY 4.0")

d0 = pd.Timestamp(date_range[0]) if len(date_range) == 2 else pd.Timestamp(min_d)
d1 = pd.Timestamp(date_range[1]) if len(date_range) == 2 else pd.Timestamp(max_d)

df = df_all[
    df_all["location"].isin(selected) &
    (df_all["date"] >= d0) & (df_all["date"] <= d1)
].copy()

# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="padding:8px 0 4px 0;">
  <p style="color:{MUTED};font-size:0.78rem;font-weight:600;
            text-transform:uppercase;letter-spacing:1.2px;margin:0;
            font-family:'Times New Roman',serif;">
    United Nations Development Programme · Latin American Bureau
  </p>
  <h1 style="color:{PRIMARY};font-size:2rem;font-weight:900;
             margin:6px 0 4px 0;line-height:1.2;
             font-family:'Times New Roman',serif;">
    Mexico's COVID-19 Outcomes Were Not Inevitable
  </h1>
  <p style="color:{MUTED};font-size:0.95rem;margin:0;
            font-family:'Times New Roman',serif;">
    A comparative analysis of how structural vulnerabilities amplified the human cost of the pandemic
  </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.caption("**Role:** Health Economist, UNDP")
c2.caption("**Stakeholders:** Mexican Ministry of Health · PAHO")
c3.caption("**Data:** Our World in Data · 240+ countries · through 2023")
st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:16px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════
st.markdown(f"<p style='color:{MUTED};font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;font-family:Times New Roman,serif;'>Executive Summary — Key Findings</p>", unsafe_allow_html=True)

e1, e2, e3, e4 = st.columns(4)

# Compute numbers dynamically from data
mex_diab = df_all[df_all["location"] == "Mexico"]["diabetes_prevalence"].dropna()
diab_val  = f"{mex_diab.iloc[0]:.1f}%" if not mex_diab.empty else "N/A"

mex_deaths_pm = df_all[df_all["location"] == "Mexico"]["total_deaths_per_million"].max()
deaths_val    = f"{int(mex_deaths_pm):,}" if not np.isnan(mex_deaths_pm) else "N/A"

mex_cfr_rows = df_all[df_all["location"] == "Mexico"].sort_values("date").dropna(subset=["total_cases","total_deaths"])
if not mex_cfr_rows.empty:
    last_mex = mex_cfr_rows.iloc[-1]
    mex_cfr  = last_mex["total_deaths"] / last_mex["total_cases"] * 100
    cfr_val  = f"{mex_cfr:.1f}%"
else:
    cfr_val = "N/A"

chile_deaths = df_all[df_all["location"] == "Chile"]["total_deaths_per_million"].max()
ratio_val = f"{mex_deaths_pm / chile_deaths:.1f}x" if (not np.isnan(mex_deaths_pm) and not np.isnan(chile_deaths) and chile_deaths > 0) else "N/A"

summary_cards = [
    (e1, "Key Finding 1", diab_val,   "Mexico's diabetes rate",
     "Highest among all comparison countries — before COVID even arrived."),
    (e2, "Key Finding 2", deaths_val, "Deaths per million in Mexico",
     "Higher than Chile, Colombia, and Argentina at comparable income levels."),
    (e3, "Key Finding 3", cfr_val,    "Case fatality rate",
     "More people died per confirmed case in Mexico than in most peer countries."),
    (e4, "Key Finding 4", ratio_val,  "Times more deaths than Chile",
     "Same income level. Very different preparation. Very different outcome."),
]
for col, label, big_num, sublabel, caption in summary_cards:
    with col:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:28px 20px 20px 20px;
                    border-top:4px solid {CRITICAL};
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);
                    text-align:center;height:100%;">
          <p style="color:{CRITICAL};font-size:0.68rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:1.1px;
                    margin:0 0 12px 0;font-family:'Times New Roman',serif;">{label}</p>
          <p style="color:{PRIMARY};font-size:3rem;font-weight:900;
                    margin:0 0 4px 0;line-height:1;
                    font-family:'Times New Roman',serif;">{big_num}</p>
          <p style="color:{SECONDARY};font-size:0.78rem;font-weight:700;
                    margin:6px 0 10px 0;font-family:'Times New Roman',serif;">{sublabel}</p>
          <p style="color:{MUTED};font-size:0.82rem;line-height:1.5;
                    margin:0;font-family:'Times New Roman',serif;">{caption}</p>
        </div>""", unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:28px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# COUNTRY SPOTLIGHT — Interactive large-number comparison
# ════════════════════════════════════════════════════════════
st.markdown(f"<p style='color:{MUTED};font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;font-family:Times New Roman,serif;'>Interactive — Country Spotlight</p>", unsafe_allow_html=True)

spotlight_country = st.selectbox(
    "Select a country to compare directly against Mexico:",
    options=[c for c in selected if c != "Mexico"],
    index=0
)

# ── Compute metrics for Mexico and selected country ──────────
def get_metrics(location, data):
    rows = data[data["location"] == location]
    if rows.empty:
        return {"deaths_pm": None, "cfr": None, "peak": None, "vacc": None}
    last   = rows.sort_values("date").dropna(subset=["total_deaths"]).iloc[-1] if not rows.dropna(subset=["total_deaths"]).empty else None
    tc     = last["total_cases"]  if last is not None else 0
    td     = last["total_deaths"] if last is not None else 0
    cfr    = (td / tc * 100) if tc and tc > 0 else None
    deaths_pm = rows["total_deaths_per_million"].max()
    peak      = rows["new_deaths_smoothed_per_million"].max()
    vacc_rows = rows.dropna(subset=["people_fully_vaccinated_per_hundred"])
    vacc      = vacc_rows["people_fully_vaccinated_per_hundred"].max() if not vacc_rows.empty else None
    return {"deaths_pm": deaths_pm, "cfr": cfr, "peak": peak, "vacc": vacc}

mex_m  = get_metrics("Mexico",          df)
comp_m = get_metrics(spotlight_country, df)

def spotlight_card(label, mex_val, comp_val, unit="", lower_is_better=True, fmt=".0f"):
    if mex_val is None or comp_val is None:
        return ""
    mex_str  = f"{mex_val:{fmt}}{unit}"
    comp_str = f"{comp_val:{fmt}}{unit}"
    # Mexico worse = red arrow up, Mexico better = green arrow down
    if lower_is_better:
        mex_color  = CRITICAL if mex_val > comp_val else SUCCESS
        comp_color = SUCCESS  if mex_val > comp_val else CRITICAL
        arrow      = "▲ Higher" if mex_val > comp_val else "▼ Lower"
        arrow_c    = CRITICAL  if mex_val > comp_val else SUCCESS
    else:
        mex_color  = SUCCESS  if mex_val > comp_val else CRITICAL
        comp_color = CRITICAL if mex_val > comp_val else SUCCESS
        arrow      = "▲ Higher" if mex_val > comp_val else "▼ Lower"
        arrow_c    = SUCCESS   if mex_val > comp_val else CRITICAL

    return f"""
    <div style="background:white;border-radius:12px;padding:24px 20px;
                box-shadow:0 2px 8px rgba(0,0,0,0.07);text-align:center;
                border-top:4px solid {BORDER};">
      <p style="color:{MUTED};font-size:0.72rem;font-weight:700;text-transform:uppercase;
                letter-spacing:1px;margin:0 0 12px 0;font-family:'Times New Roman',serif;">{label}</p>
      <div style="display:flex;justify-content:space-around;align-items:center;gap:8px;">
        <div>
          <p style="color:{MUTED};font-size:0.72rem;margin:0;font-family:'Times New Roman',serif;">Mexico</p>
          <p style="color:{mex_color};font-size:2.2rem;font-weight:900;margin:4px 0;
                    font-family:'Times New Roman',serif;">{mex_str}</p>
        </div>
        <div>
          <p style="color:{arrow_c};font-size:0.78rem;font-weight:700;
                    font-family:'Times New Roman',serif;">{arrow}</p>
        </div>
        <div>
          <p style="color:{MUTED};font-size:0.72rem;margin:0;font-family:'Times New Roman',serif;">{spotlight_country}</p>
          <p style="color:{comp_color};font-size:2.2rem;font-weight:900;margin:4px 0;
                    font-family:'Times New Roman',serif;">{comp_str}</p>
        </div>
      </div>
    </div>"""

s1, s2, s3, s4 = st.columns(4)

cards = [
    (s1, "Total Deaths per Million",    mex_m["deaths_pm"], comp_m["deaths_pm"], "",  True,  ".0f"),
    (s2, "Case Fatality Rate",          mex_m["cfr"],       comp_m["cfr"],       "%", True,  ".2f"),
    (s3, "Peak Daily Deaths / Million", mex_m["peak"],      comp_m["peak"],      "",  True,  ".1f"),
    (s4, "Population Vaccinated",       mex_m["vacc"],      comp_m["vacc"],      "%", False, ".1f"),
]

for col, label, mv, cv, unit, lib, fmt in cards:
    with col:
        st.markdown(spotlight_card(label, mv, cv, unit, lib, fmt), unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:28px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 1 — Pre-pandemic vulnerability
# Libraries: Seaborn + Matplotlib
# ════════════════════════════════════════════════════════════
act_header(1, "Mexico Was Already at a Disadvantage Before COVID Arrived")
question_box("Was Mexico's population more exposed to serious illness than comparable countries — even before the pandemic began?")

col_chart, col_right = st.columns([2, 1])

with col_chart:
    diab = (
        df_all[df_all["location"].isin(selected)]
        .groupby("location")["diabetes_prevalence"]
        .first().reset_index().dropna()
        .sort_values("diabetes_prevalence", ascending=True)
    )
    colors_diab = bar_color_list(list(diab["location"]))

    fig_a, ax_a = plt.subplots(figsize=(9, max(3, len(diab) * 0.6)))
    plt.rcParams["font.family"] = "serif"
    light_ax(ax_a, fig_a, horizontal=True)

    ax_a.barh(diab["location"], diab["diabetes_prevalence"],
              color=colors_diab, height=0.55, edgecolor="none")
    for bar in ax_a.patches:
        w = bar.get_width()
        ax_a.text(w + 0.12, bar.get_y() + bar.get_height() / 2,
                  f"{w:.1f}%", va="center", ha="left",
                  color=PRIMARY, fontsize=9, fontfamily="serif")

    mean_val = diab["diabetes_prevalence"].mean()
    ax_a.axvline(x=mean_val, color=WARNING, linewidth=1.5, linestyle="--")
    ax_a.text(mean_val + 0.15, 0.4, "Group average", color=WARNING, fontsize=8)
    ax_a.set_xlabel("Adult Population with Diabetes (%)", color=MUTED, fontsize=9)
    ax_a.set_title("Diabetes Rate Before the Pandemic (%)",
                   color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()
    st.pyplot(fig_a)
    plt.close()

with col_right:
    finding_box(
        "Mexico had the highest diabetes rate in this group — nearly 1 in 7 adults. "
        "When COVID arrived, a large share of the population was already living with "
        "a condition that makes the virus much more dangerous."
    )
    implication_box(
        "Think of it like going into a storm with a leaky roof. "
        "The storm did not cause the leak — it just made it impossible to ignore. "
        "Mexico's health vulnerabilities were there long before the pandemic."
    )

st.markdown("<br>", unsafe_allow_html=True)
col_chart2, col_right2 = st.columns([2, 1])

with col_chart2:
    beds = (
        df_all[df_all["location"].isin(selected)]
        .groupby("location")["hospital_beds_per_thousand"]
        .first().reset_index().dropna()
        .sort_values("hospital_beds_per_thousand", ascending=True)
    )
    colors_beds = bar_color_list(list(beds["location"]))

    fig_b, ax_b = plt.subplots(figsize=(9, max(3, len(beds) * 0.6)))
    plt.rcParams["font.family"] = "serif"
    light_ax(ax_b, fig_b, horizontal=True)

    ax_b.barh(beds["location"], beds["hospital_beds_per_thousand"],
              color=colors_beds, height=0.55, edgecolor="none")
    for i, (_, row) in enumerate(beds.iterrows()):
        ax_b.text(row["hospital_beds_per_thousand"] + 0.04, i,
                  f"{row['hospital_beds_per_thousand']:.1f}",
                  va="center", ha="left", color=PRIMARY, fontsize=9)
    ax_b.set_xlabel("Hospital Beds per 1,000 People", color=MUTED, fontsize=9)
    ax_b.set_title("Hospital Bed Availability Before the Pandemic",
                   color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()
    st.pyplot(fig_b)
    plt.close()

with col_right2:
    finding_box(
        "Mexico had the fewest hospital beds per person among all countries shown here. "
        "That means when large numbers of people got seriously ill at the same time, "
        "there simply was not enough room in the system to treat them all."
    )
    implication_box(
        "Hospitals do not appear overnight. "
        "The capacity that was missing during COVID had been missing for years. "
        "Underfunding healthcare before a crisis is a decision that costs lives during one."
    )

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 2 — The pandemic exposed those weaknesses
# Libraries: Plotly + Matplotlib
# ════════════════════════════════════════════════════════════
act_header(2, "Mexico Suffered More Severe Losses Than Comparable Countries")
question_box("Once COVID began spreading, did Mexico experience worse outcomes than countries at a similar level of development?")

col_chart3, col_right3 = st.columns([2, 1])

with col_chart3:
    wave_df = df.dropna(subset=["new_deaths_smoothed_per_million"])
    fig_waves = go.Figure()
    for country in selected:
        cdata     = wave_df[wave_df["location"] == country]
        is_mexico = country == "Mexico"
        fig_waves.add_trace(go.Scatter(
            x=cdata["date"], y=cdata["new_deaths_smoothed_per_million"],
            name=country,
            line=dict(color=COUNTRY_COLORS.get(country, MUTED),
                      width=3 if is_mexico else 1.5,
                      dash="solid" if is_mexico else "dot"),
            opacity=1.0 if is_mexico else 0.65,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(220,38,38,0.07)" if is_mexico else None
        ))
    fig_waves = style_plotly(fig_waves,
        "Mexico Experienced One of the Largest Mortality Waves in the Region")
    fig_waves.update_layout(yaxis_title="Daily Deaths per Million People")
    st.plotly_chart(fig_waves, use_container_width=True)

with col_right3:
    finding_box(
        "Mexico's death numbers climbed faster and stayed higher than most of the other countries "
        "during the first and second waves. Chile and Colombia — countries with similar economies — "
        "saw noticeably fewer deaths per million people during those same months."
    )
    implication_box(
        "If all countries had suffered equally, we could blame the virus. "
        "But they did not. The gap in outcomes tells us that some of what happened in Mexico "
        "was within human control — and could have gone differently."
    )

st.markdown("<br>", unsafe_allow_html=True)
col_chart4, col_right4 = st.columns([2, 1])

with col_chart4:
    cfr_df = (
        df.sort_values("date").groupby("location").last()
        .reset_index()[["location","total_cases","total_deaths"]]
        .dropna().copy()
    )
    cfr_df["CFR"] = cfr_df["total_deaths"] / cfr_df["total_cases"] * 100
    cfr_df = cfr_df.sort_values("CFR", ascending=True)
    colors_cfr = bar_color_list(list(cfr_df["location"]))

    fig_cfr, ax_cfr = plt.subplots(figsize=(9, max(3, len(cfr_df) * 0.6)))
    plt.rcParams["font.family"] = "serif"
    light_ax(ax_cfr, fig_cfr, horizontal=True)

    ax_cfr.barh(cfr_df["location"], cfr_df["CFR"],
                color=colors_cfr, height=0.55, edgecolor="none")
    for i, (_, row) in enumerate(cfr_df.iterrows()):
        ax_cfr.text(row["CFR"] + 0.03, i, f"{row['CFR']:.2f}%",
                    va="center", ha="left", color=PRIMARY, fontsize=9)
    ax_cfr.set_xlabel(
        "Out of every 100 confirmed COVID cases, this many people died",
        color=MUTED, fontsize=9)
    ax_cfr.set_title(
        "A Higher Share of Confirmed Cases Resulted in Death in Mexico",
        color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()
    st.pyplot(fig_cfr)
    plt.close()

with col_right4:
    finding_box(
        "In Mexico, more people died for every 100 confirmed COVID cases than in most peer countries. "
        "Part of this is because far fewer tests were done — so only the sickest people were "
        "ever officially counted. By the time many patients reached a hospital, it was already too late."
    )
    implication_box(
        "A high death rate among confirmed cases is a warning sign — it means the system "
        "is only seeing people when they are already in crisis. "
        "Earlier detection saves lives, and that requires more testing, earlier."
    )

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 3 — The response was not fast enough
# Library: Plotly
# ════════════════════════════════════════════════════════════
act_header(3, "Vaccination Expanded Only After the Worst Waves Had Already Passed")
question_box("Did protective measures reach people in time to prevent the most severe losses?")

col_chart5, col_right5 = st.columns([2, 1])

with col_chart5:
    vacc_df = df.dropna(subset=["people_fully_vaccinated_per_hundred"])
    fig_vacc = go.Figure()
    for country in selected:
        cdata     = vacc_df[vacc_df["location"] == country]
        is_mexico = country == "Mexico"
        is_chile  = country == "Chile"
        if cdata.empty:
            continue
        fig_vacc.add_trace(go.Scatter(
            x=cdata["date"], y=cdata["people_fully_vaccinated_per_hundred"],
            name=country,
            line=dict(color=COUNTRY_COLORS.get(country, MUTED),
                      width=3 if (is_mexico or is_chile) else 1.5,
                      dash="solid" if (is_mexico or is_chile) else "dot"),
            opacity=1.0 if (is_mexico or is_chile) else 0.6,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(220,38,38,0.06)" if is_mexico else None
        ))
    fig_vacc.add_hline(y=70, line_dash="dash", line_color=MUTED,
                       annotation_text="70% coverage threshold",
                       annotation_font_color=MUTED, annotation_font_size=10)
    fig_vacc = style_plotly(fig_vacc,
        "Vaccination Campaigns Accelerated Only After Major Damage Had Occurred")
    fig_vacc.update_layout(
        yaxis_title="Population Fully Vaccinated (%)", yaxis_range=[0, 100])
    st.plotly_chart(fig_vacc, use_container_width=True)

with col_right5:
    finding_box(
        "Look at how far ahead Chile is compared to Mexico on this chart. "
        "By the time Mexico reached 30% of people vaccinated, Chile had already protected "
        "more than 70% of its population. Mexico's campaign picked up speed only after "
        "its two deadliest waves had already ended."
    )
    implication_box(
        "Getting vaccinated early is what actually saves lives — not just getting vaccinated eventually. "
        "Chile showed that a Latin American country could move fast. "
        "Mexico had the same option and did not take it in time."
    )

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 4 — The costs were avoidable
# Library: Seaborn
# ════════════════════════════════════════════════════════════
act_header(4, "Countries With Similar Resources Achieved Far Better Outcomes")
question_box("Can the difference in outcomes be explained by wealth alone — or did preparation and response quality matter more?")

col_chart6, col_right6 = st.columns([2, 1])

with col_chart6:
    scatter_base = (
        df_all[(df_all["date"] >= d0) & (df_all["date"] <= d1)]
        .groupby("location")
        .agg(gdp=("gdp_per_capita","first"),
             deaths=("total_deaths_per_million","max"))
        .reset_index().dropna(subset=["gdp","deaths"])
    )
    is_focus = scatter_base["location"].isin(selected)

    fig_sc, ax_sc = plt.subplots(figsize=(10, 5.5))
    plt.rcParams["font.family"] = "serif"
    light_ax(ax_sc, fig_sc)
    ax_sc.xaxis.grid(True, color=BORDER, linewidth=0.7)

    sns.scatterplot(
        data=scatter_base[~is_focus], x="gdp", y="deaths",
        color="#CBD5E1", alpha=0.45, s=20, ax=ax_sc, zorder=1, legend=False)

    log_gdp = np.log1p(scatter_base["gdp"])
    slope, intercept, r_val, *_ = stats.linregress(log_gdp, scatter_base["deaths"])
    x_fit = np.linspace(scatter_base["gdp"].min(), scatter_base["gdp"].max(), 300)
    ax_sc.plot(x_fit, slope * np.log1p(x_fit) + intercept,
               color=BORDER, linewidth=1.8, linestyle="--",
               label="Expected outcome based on income level", zorder=2)

    for _, row in scatter_base[is_focus].iterrows():
        color = COUNTRY_COLORS.get(row["location"], ACCENT)
        size  = 200 if row["location"] in ["Mexico","Chile"] else 90
        ax_sc.scatter(row["gdp"], row["deaths"], color=color, s=size,
                      zorder=4, edgecolors="white", linewidths=0.7)
        ax_sc.annotate(row["location"], (row["gdp"], row["deaths"]),
                       xytext=(8, 5), textcoords="offset points",
                       fontsize=9, color=color, fontweight="bold")

    ax_sc.set_xlabel("Income per Person (GDP per Capita, USD)", color=MUTED, fontsize=10)
    ax_sc.set_ylabel("Total Deaths per Million People", color=MUTED, fontsize=10)
    ax_sc.set_title("Chile and Mexico Have Similar Incomes — But Very Different Outcomes",
                    color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    ax_sc.legend(fontsize=9, facecolor="white", edgecolor=BORDER, labelcolor=MUTED)
    plt.tight_layout()
    st.pyplot(fig_sc)
    plt.close()

with col_right6:
    finding_box(
        "Mexico and Chile sit at roughly the same income level on this chart. "
        "But look at where they land on deaths — Chile is significantly lower. "
        "Both countries faced the same virus with similar budgets. "
        "One was better prepared than the other."
    )
    implication_box(
        "This is the most important chart in the dashboard. "
        "It shows that money is not the deciding factor — preparation is. "
        "Mexico did not lose more people because it was poor. "
        "It lost more people because it was not ready."
    )

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 5 — Policy recommendations
# ════════════════════════════════════════════════════════════
act_header(5, "What Decision-Makers Should Do Now")
question_box("Given everything this data shows, where should governments invest to prevent this from happening again?")

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)

recs = [
    ("1. Reduce diabetes rates now — not during the next crisis",
     "Mexico's diabetes burden existed before COVID and will exist before the next outbreak. "
     "Investing in prevention today directly reduces the number of high-risk people tomorrow."),
    ("2. Expand hospital capacity outside major cities",
     "When cases surged, the system ran out of room. More beds in underserved regions "
     "means more lives saved when the next emergency hits."),
    ("3. Build a permanent testing network",
     "Mexico could not see the wave coming until it had already arrived. "
     "A nationwide testing system gives decision-makers time to act before hospitals are overwhelmed."),
    ("4. Pre-negotiate vaccine agreements before the next emergency",
     "Chile's advantage was preparation, not luck. "
     "Mexico needs supply agreements signed in advance — ready to activate the moment a new threat appears."),
]

for i, (title, text) in enumerate(recs):
    col = r1 if i % 2 == 0 else r2
    with col:
        st.markdown(
            f'<div class="rec-card">'
            f'<div class="rec-title">{title}</div>'
            f'<p class="rec-text">{text}</p>'
            f'</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f'<div class="conclusion-banner">'
    f'<p class="conclusion-text">'
    f'"Mexico\'s COVID losses were amplified by existing health and system vulnerabilities. '
    f'The evidence presented here supports one conclusion: '
    f'investment in healthcare resilience before a crisis is not a cost — it is insurance. '
    f'The question is not whether another health emergency will come. '
    f'It is whether Mexico will be ready."'
    f'</p></div>', unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:2px solid {BORDER};margin:28px 0;'>", unsafe_allow_html=True)

with st.expander("Data limitations and methodological notes"):
    st.markdown(f"""
    <div style="color:{MUTED};font-size:0.88rem;line-height:1.7;font-family:'Times New Roman',serif;">
    <p><strong style="color:{PRIMARY};">Mexico tested far fewer people than comparable countries.</strong>
    This means the actual number of infections was much higher than officially recorded,
    which makes the death rate look worse than it truly was.</p>
    <p><strong style="color:{PRIMARY};">The real death toll is likely much higher.</strong>
    Independent analyses estimate Mexico's true pandemic deaths at two to three times
    the official count, once all excess deaths are included.</p>
    <p><strong style="color:{PRIMARY};">Health indicator data is pre-pandemic.</strong>
    Figures for diabetes, hospital beds, and cardiovascular conditions reflect pre-2020 baselines.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f"<p style='color:{MUTED};font-size:0.78rem;text-align:center;margin-top:8px;"
    f"font-family:Times New Roman,serif;'>"
    f"Data: Our World in Data COVID-19 Dataset · ourworldindata.org · CC BY 4.0 · "
    f"Built with Streamlit, Plotly, Seaborn, and Matplotlib</p>",
    unsafe_allow_html=True)
