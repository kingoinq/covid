# ============================================================
#  COVID-19: Mexico in Comparative Perspective
#  Role:         Health Economist, UNDP Latin American Bureau
#  Stakeholders: Mexican Ministry of Health, PAHO
#  Argument:     Mexico's outcomes were not inevitable.
#                They were magnified by structural weaknesses
#                that existed before the pandemic began.
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

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="COVID-19: Mexico in Comparative Perspective",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color palette — dark theme ────────────────────────────────
BG        = "#0f1117"
CARD_BG   = "#1a1f2e"
CARD_BG2  = "#151b27"
PRIMARY   = "#e2e8f0"
SECONDARY = "#60a5fa"
ACCENT    = "#3b82f6"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
CRITICAL  = "#ef4444"
MUTED     = "#94a3b8"
BORDER    = "#2d3748"

# Different shades of blue for non-Mexico bars (dark → light)
BLUE_SHADES = [
    "#1e3a5f",  # very dark blue
    "#1d4ed8",  # dark blue
    "#2563eb",  # medium-dark blue
    "#3b82f6",  # medium blue
    "#60a5fa",  # light blue
    "#93c5fd",  # lighter blue
    "#bfdbfe",  # pale blue
]

# Country accent colors (used in line charts)
COUNTRY_COLORS = {
    "Mexico":        CRITICAL,
    "Chile":         SUCCESS,
    "United States": "#60a5fa",
    "Brazil":        "#2dd4bf",
    "Colombia":      "#818cf8",
    "Argentina":     "#a78bfa",
    "Peru":          WARNING,
    "Germany":       "#94a3b8",
    "Spain":         "#f9a8d4",
}
ALL_PEERS = [c for c in COUNTRY_COLORS if c != "Mexico"]

# ── CSS — dark UN report ──────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BG}; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; }}

  .act-pill {{
    display: inline-block;
    background: {ACCENT};
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
    background: #172033;
    border-left: 4px solid {ACCENT};
    padding: 13px 18px;
    border-radius: 0 8px 8px 0;
    color: {SECONDARY};
    font-size: 1rem;
    font-weight: 600;
    margin: 14px 0 20px 0;
  }}
  .finding-box {{
    background: #2d1515;
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
    line-height: 1.55;
    margin: 0;
  }}
  .implication-box {{
    background: #0f2d1f;
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
    line-height: 1.55;
    margin: 0;
  }}
  .exec-card {{
    background: {CARD_BG};
    border-radius: 10px;
    padding: 22px 20px;
    border-top: 4px solid {CRITICAL};
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
    font-weight: 400;
    line-height: 1.55;
    margin: 0;
  }}
  .conclusion-banner {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 5px solid {ACCENT};
    padding: 24px 32px;
    border-radius: 0 12px 12px 0;
    margin: 16px 0;
  }}
  .conclusion-text {{
    color: {PRIMARY};
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
    line-height: 1.55;
    margin: 0;
  }}
  #MainMenu {{ visibility: hidden; }}
  footer     {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Reusable HTML components ─────────────────────────────────
def act_header(number, title):
    st.markdown(
        f'<div class="act-pill">Act {number}</div>'
        f'<div class="act-title">{title}</div>',
        unsafe_allow_html=True
    )

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

# ── Shared chart styles ───────────────────────────────────────
def style_plotly(fig, title=""):
    fig.update_layout(
        title=title, title_font_size=14,
        title_font_color=PRIMARY,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=PRIMARY,
        margin=dict(t=50, b=10, l=10, r=10),
        yaxis=dict(gridcolor=BORDER, color=MUTED, linecolor=BORDER),
        xaxis=dict(gridcolor=BORDER, color=MUTED, linecolor=BORDER),
        legend=dict(orientation="h", y=-0.3, font_size=11, font_color=PRIMARY),
        hovermode="x unified"
    )
    return fig

def dark_ax(ax, fig, horizontal=False):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(BORDER)
    if horizontal:
        ax.xaxis.grid(True, color=BORDER, linewidth=0.7)
    else:
        ax.yaxis.grid(True, color=BORDER, linewidth=0.7)
    ax.set_axisbelow(True)
    return ax

def bar_color_list(locations, highlight="Mexico"):
    """
    Assign a distinct blue shade to each non-Mexico bar.
    Mexico always gets CRITICAL red.
    """
    non_mexico = [l for l in locations if l != highlight]
    shade_map  = {loc: BLUE_SHADES[i % len(BLUE_SHADES)]
                  for i, loc in enumerate(non_mexico)}
    return [CRITICAL if loc == highlight else shade_map[loc]
            for loc in locations]

# ── Data loading ──────────────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    response.raise_for_status()

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
        io.StringIO(response.text),
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
    st.markdown(f"<p style='color:{PRIMARY};font-weight:700;font-size:1rem;margin-bottom:2px;'>COVID-19 Analysis</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};font-size:0.82rem;margin-top:0;'>UNDP Health Economist Report</p>", unsafe_allow_html=True)
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

# ── Apply filters ─────────────────────────────────────────────
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
            text-transform:uppercase;letter-spacing:1.2px;margin:0;">
    United Nations Development Programme · Latin American Bureau
  </p>
  <h1 style="color:{PRIMARY};font-size:2rem;font-weight:900;
             margin:6px 0 4px 0;line-height:1.2;">
    Mexico's COVID-19 Outcomes Were Not Inevitable
  </h1>
  <p style="color:{MUTED};font-size:0.95rem;margin:0;">
    A comparative analysis of how structural vulnerabilities amplified the human cost of the pandemic
  </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.caption(f"**Role:** Health Economist, UNDP")
c2.caption(f"**Stakeholders:** Mexican Ministry of Health · PAHO")
c3.caption(f"**Data:** Our World in Data · 240+ countries · through 2023")

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:16px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════
st.markdown(f"<p style='color:{MUTED};font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;'>Executive Summary — Key Findings</p>", unsafe_allow_html=True)

e1, e2, e3, e4 = st.columns(4)
findings = [
    ("Key Finding 1", "Mexico entered the pandemic with one of the highest diabetes rates among comparable countries — a condition that significantly increases the risk of severe illness and death from COVID-19."),
    ("Key Finding 2", "Mexico's death rate was among the highest in Latin America. More people died per million residents here than in Brazil, Colombia, and Argentina — countries at similar income levels."),
    ("Key Finding 3", "Vaccination expanded significantly only after the two deadliest waves had already passed. The protection arrived too late to prevent the worst outcomes."),
    ("Key Finding 4", "Chile — with a similar economy — achieved far better outcomes. This shows the losses were not inevitable. Stronger preparation and faster action could have saved lives."),
]
for col, (num, text) in zip([e1, e2, e3, e4], findings):
    with col:
        st.markdown(
            f'<div class="exec-card">'
            f'<div class="exec-number">{num}</div>'
            f'<p class="exec-text">{text}</p>'
            f'</div>', unsafe_allow_html=True)

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:28px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 1 — Pre-pandemic vulnerability
# Libraries: Seaborn (diabetes) + Matplotlib (hospital beds)
# ════════════════════════════════════════════════════════════
act_header(1, "Mexico Was Already at a Disadvantage Before COVID Arrived")
question_box("Was Mexico's population more exposed to serious illness than comparable countries — even before the pandemic began?")

col_chart, col_right = st.columns([2, 1])

with col_chart:
    # ── Seaborn: Diabetes prevalence ─────────────────────────
    diab = (
        df_all[df_all["location"].isin(selected)]
        .groupby("location")["diabetes_prevalence"]
        .first().reset_index().dropna()
        .sort_values("diabetes_prevalence", ascending=True)
    )
    colors_diab = bar_color_list(list(diab["location"]))

    fig_a, ax_a = plt.subplots(figsize=(9, max(3, len(diab) * 0.6)))
    dark_ax(ax_a, fig_a, horizontal=True)

    bars = ax_a.barh(diab["location"], diab["diabetes_prevalence"],
                     color=colors_diab, height=0.55, edgecolor="none")

    for bar in bars:
        w = bar.get_width()
        ax_a.text(w + 0.12, bar.get_y() + bar.get_height() / 2,
                  f"{w:.1f}%", va="center", ha="left",
                  color=PRIMARY, fontsize=9)

    mean_val = diab["diabetes_prevalence"].mean()
    ax_a.axvline(x=mean_val, color=WARNING, linewidth=1.5, linestyle="--")
    ax_a.text(mean_val + 0.15, 0.4, "Group average",
              color=WARNING, fontsize=8)

    ax_a.set_xlabel("Adult Population with Diabetes (%)", color=MUTED, fontsize=9)
    ax_a.set_title("Diabetes Rate Before the Pandemic (%)",
                   color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    ax_a.tick_params(colors=MUTED)
    plt.tight_layout()
    st.pyplot(fig_a)
    plt.close()

with col_right:
    finding_box(
        "Mexico had the highest diabetes rate among all comparison countries — "
        "nearly 1 in 7 adults. Diabetes was identified within the first weeks of "
        "the pandemic as a major risk factor for severe illness, hospitalization, "
        "and death from COVID-19."
    )
    implication_box(
        "A country with a high-risk population needs a stronger health system to protect it. "
        "Mexico entered the pandemic with the opposite: high vulnerability and limited capacity."
    )

st.markdown("<br>", unsafe_allow_html=True)
col_chart2, col_right2 = st.columns([2, 1])

with col_chart2:
    # ── Matplotlib: Hospital beds ─────────────────────────────
    beds = (
        df_all[df_all["location"].isin(selected)]
        .groupby("location")["hospital_beds_per_thousand"]
        .first().reset_index().dropna()
        .sort_values("hospital_beds_per_thousand", ascending=True)
    )
    colors_beds = bar_color_list(list(beds["location"]))

    fig_b, ax_b = plt.subplots(figsize=(9, max(3, len(beds) * 0.6)))
    dark_ax(ax_b, fig_b, horizontal=True)

    ax_b.barh(beds["location"], beds["hospital_beds_per_thousand"],
              color=colors_beds, height=0.55, edgecolor="none")

    for i, (_, row) in enumerate(beds.iterrows()):
        ax_b.text(row["hospital_beds_per_thousand"] + 0.04, i,
                  f"{row['hospital_beds_per_thousand']:.1f}",
                  va="center", ha="left", color=PRIMARY, fontsize=9)

    ax_b.set_xlabel("Hospital Beds per 1,000 People", color=MUTED, fontsize=9)
    ax_b.set_title("Hospital Bed Availability Before the Pandemic",
                   color=PRIMARY, fontsize=13, fontweight="bold", pad=10)
    ax_b.tick_params(colors=MUTED)
    plt.tight_layout()
    st.pyplot(fig_b)
    plt.close()

with col_right2:
    finding_box(
        "Mexico had fewer hospital beds per person than every other country in this comparison. "
        "When large numbers of people became severely ill at the same time, "
        "the system had very little room to absorb the pressure."
    )
    implication_box(
        "Low hospital capacity is not a surprise during a crisis — it is a predictable result "
        "of years of underinvestment. The pandemic did not create this problem. It exposed it."
    )

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 2 — The pandemic exposed those weaknesses
# Libraries: Plotly (death waves) + Matplotlib (CFR)
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
            x=cdata["date"],
            y=cdata["new_deaths_smoothed_per_million"],
            name=country,
            line=dict(
                color=COUNTRY_COLORS.get(country, MUTED),
                width=3 if is_mexico else 1.5,
                dash="solid" if is_mexico else "dot"
            ),
            opacity=1.0 if is_mexico else 0.7,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(239,68,68,0.07)" if is_mexico else None
        ))

    fig_waves = style_plotly(
        fig_waves,
        "Mexico Experienced One of the Largest Mortality Waves in the Region"
    )
    fig_waves.update_layout(yaxis_title="Daily Deaths per Million People")
    st.plotly_chart(fig_waves, use_container_width=True)

with col_right3:
    finding_box(
        "Mexico's death curve rose faster and stayed higher than most comparable countries "
        "during the first and second waves. Chile and Colombia — "
        "which share similar income levels — recorded significantly fewer deaths per million "
        "during the same periods."
    )
    implication_box(
        "If the difference were only about the virus, all countries would have suffered equally. "
        "The fact that outcomes differed this much points to factors within human control: "
        "health system capacity, early detection, and speed of response."
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
    dark_ax(ax_cfr, fig_cfr, horizontal=True)

    ax_cfr.barh(cfr_df["location"], cfr_df["CFR"],
                color=colors_cfr, height=0.55, edgecolor="none")

    for i, (_, row) in enumerate(cfr_df.iterrows()):
        ax_cfr.text(row["CFR"] + 0.03, i, f"{row['CFR']:.2f}%",
                    va="center", ha="left", color=PRIMARY, fontsize=9)

    ax_cfr.set_xlabel(
        "Out of every 100 confirmed COVID cases, this many people died",
        color=MUTED, fontsize=9
    )
    ax_cfr.set_title(
        "A Higher Share of Confirmed Cases Resulted in Death in Mexico",
        color=PRIMARY, fontsize=13, fontweight="bold", pad=10
    )
    ax_cfr.tick_params(colors=MUTED)
    plt.tight_layout()
    st.pyplot(fig_cfr)
    plt.close()

with col_right4:
    finding_box(
        "For every 100 people confirmed with COVID in Mexico, more died than in most "
        "comparable countries. This reflects two problems at once: far fewer people "
        "were tested — so only the most serious cases were counted — and many patients "
        "arrived at hospitals too late to be saved."
    )
    implication_box(
        "A high death rate among confirmed cases signals that the healthcare system "
        "is not catching the disease early enough. People are only being counted "
        "when they are already critically ill."
    )

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

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
            x=cdata["date"],
            y=cdata["people_fully_vaccinated_per_hundred"],
            name=country,
            line=dict(
                color=COUNTRY_COLORS.get(country, MUTED),
                width=3 if (is_mexico or is_chile) else 1.5,
                dash="solid" if (is_mexico or is_chile) else "dot"
            ),
            opacity=1.0 if (is_mexico or is_chile) else 0.65,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(239,68,68,0.06)" if is_mexico else None
        ))

    fig_vacc.add_hline(y=70, line_dash="dash", line_color=MUTED,
                       annotation_text="70% coverage threshold",
                       annotation_font_color=MUTED,
                       annotation_font_size=10)

    fig_vacc = style_plotly(
        fig_vacc,
        "Vaccination Campaigns Accelerated Only After Major Damage Had Occurred"
    )
    fig_vacc.update_layout(
        yaxis_title="Population Fully Vaccinated (%)",
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig_vacc, use_container_width=True)

with col_right5:
    finding_box(
        "Chile rolled out its vaccination campaign far ahead of every other country in the region. "
        "By the time Mexico reached 30% coverage, Chile had already passed 70%. "
        "Mexico's vaccination rate accelerated only after its two deadliest waves — "
        "in mid-2020 and early 2021 — had already ended. The protection came after the damage."
    )
    implication_box(
        "Vaccination timing is as important as vaccination coverage. "
        "Reaching people quickly — before major waves — is what determines how many lives are saved. "
        "Chile proved this was achievable in Latin America."
    )

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

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
        .reset_index()
        .dropna(subset=["gdp","deaths"])
    )
    is_focus = scatter_base["location"].isin(selected)

    fig_sc, ax_sc = plt.subplots(figsize=(10, 5.5))
    dark_ax(ax_sc, fig_sc)
    ax_sc.xaxis.grid(True, color=BORDER, linewidth=0.7)

    sns.scatterplot(
        data=scatter_base[~is_focus],
        x="gdp", y="deaths",
        color="#2d3748", alpha=0.5, s=22,
        ax=ax_sc, zorder=1, legend=False
    )

    log_gdp = np.log1p(scatter_base["gdp"])
    slope, intercept, r_val, *_ = stats.linregress(log_gdp, scatter_base["deaths"])
    x_fit = np.linspace(scatter_base["gdp"].min(), scatter_base["gdp"].max(), 300)
    ax_sc.plot(x_fit, slope * np.log1p(x_fit) + intercept,
               color=BORDER, linewidth=1.8, linestyle="--",
               label=f"Expected outcome based on income level (r={r_val:.2f})", zorder=2)

    for _, row in scatter_base[is_focus].iterrows():
        color = COUNTRY_COLORS.get(row["location"], ACCENT)
        size  = 200 if row["location"] in ["Mexico","Chile"] else 90
        ax_sc.scatter(row["gdp"], row["deaths"], color=color, s=size,
                      zorder=4, edgecolors="white", linewidths=0.7)
        ax_sc.annotate(
            row["location"], (row["gdp"], row["deaths"]),
            xytext=(8, 5), textcoords="offset points",
            fontsize=9, color=color, fontweight="bold"
        )

    ax_sc.set_xlabel("Income per Person (GDP per Capita, USD)", color=MUTED, fontsize=10)
    ax_sc.set_ylabel("Total Deaths per Million People", color=MUTED, fontsize=10)
    ax_sc.set_title(
        "Chile and Mexico Have Similar Incomes — But Very Different Outcomes",
        color=PRIMARY, fontsize=13, fontweight="bold", pad=10
    )
    ax_sc.legend(fontsize=9, facecolor=CARD_BG,
                 edgecolor=BORDER, labelcolor=MUTED)
    plt.tight_layout()
    st.pyplot(fig_sc)
    plt.close()

with col_right6:
    finding_box(
        "Mexico and Chile have comparable income levels — yet outcomes are very different. "
        "Chile recorded significantly fewer deaths per million people. "
        "Both countries sit near the same point on the income scale, "
        "but Chile managed to limit the human cost far more effectively."
    )
    implication_box(
        "When two countries with similar resources produce different results, "
        "the variable is not wealth — it is preparation, speed, and the strength "
        "of the health system. Mexico's losses were not predetermined by its income. "
        "They were determined by decisions."
    )

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:32px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACT 5 — Policy recommendations
# ════════════════════════════════════════════════════════════
act_header(5, "What Decision-Makers Should Do Now")
question_box("Given everything this data shows, where should governments invest to prevent this from happening again?")

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)

recs = [
    ("1. Reduce diabetes and chronic disease rates now — not during the next crisis",
     "Mexico's diabetes burden existed long before COVID-19 arrived. It will still be there "
     "before the next outbreak. Every year of investment in nutrition programs, preventive care, "
     "and early screening reduces the number of people at high risk when the next pathogen emerges."),
    ("2. Expand public hospital capacity, particularly outside major cities",
     "Mexico had fewer hospital beds than most peers going into the pandemic. "
     "When cases surged, the system ran out of room. Expanding capacity in public hospitals — "
     "especially in lower-income regions — directly determines how many severe cases can be treated."),
    ("3. Build a permanent early detection and testing network",
     "Mexico tested far fewer people than comparable countries. This meant the country "
     "could not see the wave coming until it had already arrived. "
     "A permanent, nationwide testing infrastructure would give decision-makers weeks of "
     "advance warning — enough time to act before hospitals are overwhelmed."),
    ("4. Pre-negotiate vaccine supply agreements before the next emergency",
     "Chile's advantage was not just speed — it was preparation. "
     "Chile had agreements with multiple vaccine manufacturers signed in advance. "
     "Mexico should formalize equivalent agreements now, "
     "so they are ready to activate the moment a new threat is confirmed."),
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

st.markdown(f"<hr style='border:none;border-top:1px solid {BORDER};margin:28px 0;'>", unsafe_allow_html=True)

# ── Limitations ───────────────────────────────────────────────
with st.expander("Data limitations and methodological notes"):
    st.markdown(f"""
    <div style="color:{MUTED};font-size:0.88rem;line-height:1.7;">
    <p><strong style="color:{PRIMARY};">Undertesting in Mexico.</strong>
    Mexico tested far fewer people per capita than the United States or European countries.
    This means the actual number of COVID cases was much higher than officially recorded.
    As a result, the case fatality rate appears higher than it truly was.</p>
    <p><strong style="color:{PRIMARY};">Unofficial death toll.</strong>
    Independent analyses estimate Mexico's true pandemic death toll at two to three times
    the official figures, once excess deaths are included.</p>
    <p><strong style="color:{PRIMARY};">Pre-pandemic health data.</strong>
    Diabetes rates, hospital beds, and cardiovascular figures reflect pre-2020 baselines.</p>
    <p><strong style="color:{PRIMARY};">Vaccination reporting.</strong>
    Some early periods of Mexico's regional rollout show inconsistent daily reporting,
    creating flat sections in the vaccination curve.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f"<p style='color:{MUTED};font-size:0.78rem;text-align:center;margin-top:8px;'>"
    f"Data: Our World in Data COVID-19 Dataset · ourworldindata.org · CC BY 4.0 · "
    f"Built with Streamlit, Plotly, Seaborn, and Matplotlib</p>",
    unsafe_allow_html=True)
