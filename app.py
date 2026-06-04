# ============================================================
#  COVID-19: Mexico in Comparative Perspective
#  Role:         Health Economist, UNDP Latin American Bureau
#  Stakeholders: Mexican Ministry of Health, PAHO
#  Dataset:      Our World in Data COVID-19 Dataset (OWID)
#  Libraries:    Plotly · Seaborn · Matplotlib
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="COVID-19: Mexico in Comparative Perspective",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Color map ────────────────────────────────────────────────
# Mexico is always red (focal point).
# Peers are muted blues and neutrals to stay subordinate.
COLORS = {
    "Mexico":        "#e63946",
    "United States": "#457b9d",
    "Brazil":        "#2a9d8f",
    "Chile":         "#e9c46a",
    "Colombia":      "#8ecae6",
    "Argentina":     "#a8dadc",
    "Peru":          "#f4a261",
    "Germany":       "#6d6875",
    "Spain":         "#b5838d",
}

ALL_PEERS = [c for c in COLORS if c != "Mexico"]

# ── Data loading — reads directly from OWID URL ──────────────
# Using a URL means no CSV file is needed in the repo.
# st.cache_data ensures it only downloads once per session.
@st.cache_data
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

    needed = [
        "iso_code", "continent", "location", "date",
        "total_cases", "total_deaths",
        "total_cases_per_million", "total_deaths_per_million",
        "new_deaths_smoothed_per_million",
        "people_fully_vaccinated_per_hundred",
        "population", "gdp_per_capita",
        "hospital_beds_per_thousand",
        "diabetes_prevalence",
        "cardiovasc_death_rate",
    ]

    df = pd.read_csv(
        url,
        usecols=lambda c: c in needed,
        parse_dates=["date"],
        low_memory=False
    )

    # Keep country-level rows only (OWID prefixes aggregates with "OWID_")
    df = df[
        ~df["iso_code"].str.startswith("OWID", na=True) &
        df["continent"].notna()
    ].copy()

    return df

with st.spinner("Loading data from Our World in Data..."):
    df_all = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### COVID-19 Analysis")
    st.markdown("**Role:** Health Economist, UNDP")
    st.divider()

    peers = st.multiselect(
        "Compare Mexico against:",
        options=ALL_PEERS,
        default=["United States", "Brazil", "Chile", "Colombia", "Peru"]
    )
    selected = ["Mexico"] + peers

    st.divider()

    min_d = df_all["date"].min().date()
    max_d = df_all["date"].max().date()
    date_range = st.date_input(
        "Date range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d
    )

    st.divider()
    st.caption("Source: Our World in Data\nCC BY 4.0")

# ── Apply filters ────────────────────────────────────────────
if len(date_range) == 2:
    d0 = pd.Timestamp(date_range[0])
    d1 = pd.Timestamp(date_range[1])
else:
    d0 = pd.Timestamp(df_all["date"].min())
    d1 = pd.Timestamp(df_all["date"].max())

df = df_all[
    df_all["location"].isin(selected) &
    (df_all["date"] >= d0) &
    (df_all["date"] <= d1)
].copy()

# ── Shared Plotly layout ─────────────────────────────────────
def style_plotly(fig, title=""):
    fig.update_layout(
        title=title,
        title_font_size=15,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        margin=dict(t=50, b=10, l=10, r=10),
        yaxis=dict(gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        legend=dict(orientation="h", y=-0.3, font_size=11),
        hovermode="x unified"
    )
    return fig

# ── Shared Matplotlib base ───────────────────────────────────
def dark_ax(ax, fig):
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    ax.tick_params(colors="#94a3b8")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#334155")
    ax.yaxis.grid(True, color="#1e293b", linewidth=0.6)
    ax.set_axisbelow(True)
    return ax

# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
st.title("COVID-19: Mexico in Comparative Perspective")
st.markdown(
    "**Role:** Health Economist, United Nations Development Programme (UNDP) — Latin American Bureau  \n"
    "**Stakeholders:** Mexican Ministry of Health · PAHO Regional Office · Latin American Finance Ministers  \n"
    "**Dataset:** Our World in Data COVID-19 Dataset — 240+ countries, daily granularity, "
    "cases, deaths, vaccinations, and socioeconomic indicators through 2023."
)

with st.expander("Analytical context and guiding questions"):
    st.markdown("""
    Mexico entered the COVID-19 pandemic with a distinct set of structural vulnerabilities:
    one of the highest diabetes and obesity rates in the world, a public health system
    chronically underfunded relative to peer economies, limited testing infrastructure,
    and a government that initially prioritized economic continuity over aggressive containment.

    This dashboard benchmarks Mexico's pandemic outcomes against:
    - Its **northern neighbor** (United States)
    - The **largest Latin American economy** (Brazil)
    - A **regional success story** (Chile — fastest vaccine rollout in LATAM)
    - A **regional cautionary tale** (Peru — highest deaths per million globally)
    - **Similar-income comparators** (Colombia, Argentina)
    - **High-income references** (Germany, Spain)

    **Four questions guide this analysis:**
    1. How did Mexico's death toll evolve compared to peers — and how severe were each wave?
    2. Does national wealth predict better pandemic survival — and where does Mexico fall?
    3. How fast did Mexico vaccinate relative to neighbors — and did timing matter?
    4. Was Mexico structurally more vulnerable before the first case was even confirmed?
    """)

st.divider()

# ── KPI CARDS ────────────────────────────────────────────────
mex_rows = df[df["location"] == "Mexico"].sort_values("date")
mex_last = mex_rows.dropna(subset=["total_deaths"]).iloc[-1] if not mex_rows.dropna(subset=["total_deaths"]).empty else None

c1, c2, c3, c4 = st.columns(4)
if mex_last is not None:
    tc  = mex_last.get("total_cases",  0) or 0
    td  = mex_last.get("total_deaths", 0) or 0
    cfr = (td / tc * 100) if tc > 0 else 0
    vx  = mex_rows.dropna(subset=["people_fully_vaccinated_per_hundred"])
    vx_val = vx.iloc[-1]["people_fully_vaccinated_per_hundred"] if not vx.empty else 0
    c1.metric("Mexico — Total Cases",  f"{tc/1e6:.2f} M")
    c2.metric("Mexico — Total Deaths", f"{td/1e3:.0f} K")
    c3.metric("Case Fatality Rate",    f"{cfr:.2f}%")
    c4.metric("Fully Vaccinated",      f"{vx_val:.1f}%")

st.divider()

# ════════════════════════════════════════════════════════════
# CHART 1 — Death waves over time  [PLOTLY]
# ════════════════════════════════════════════════════════════
st.subheader("How did the death toll evolve? Mexico vs peers")
st.caption("7-day smoothed daily deaths per million population")

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    wave_df = df.dropna(subset=["new_deaths_smoothed_per_million"])
    fig1 = go.Figure()

    for country in selected:
        cdata     = wave_df[wave_df["location"] == country]
        is_mexico = country == "Mexico"
        fig1.add_trace(go.Scatter(
            x=cdata["date"],
            y=cdata["new_deaths_smoothed_per_million"],
            name=country,
            line=dict(
                color=COLORS.get(country, "#94a3b8"),
                width=3 if is_mexico else 1.5,
                dash="solid" if is_mexico else "dot"
            ),
            opacity=1.0 if is_mexico else 0.7,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(230,57,70,0.07)" if is_mexico else None
        ))

    fig1 = style_plotly(fig1, "Daily Deaths per Million — 7-day Average")
    fig1.update_layout(yaxis_title="Deaths per Million")
    st.plotly_chart(fig1, use_container_width=True)

with col_insight:
    st.markdown("#### What this reveals")
    st.markdown("""
    Mexico's death curve shows a pattern distinct from its neighbors.

    The **first wave (mid-2020)** hit Mexico earlier and harder than most
    Latin American peers, with deaths per million surpassing Colombia and
    Argentina at peak.

    Mexico never achieved the sharp post-wave declines visible in Chile —
    suggesting insufficient suppression between waves rather than genuine
    containment.

    The **Omicron wave (late 2021–2022)** shows a sharp divergence: countries
    with high vaccination coverage saw cases spike but deaths remain flat.
    Mexico's pattern during this period reflects the timing gap in its
    vaccine rollout.
    """)

st.divider()

# ════════════════════════════════════════════════════════════
# CHART 2 — GDP vs Deaths  [SEABORN]
# ════════════════════════════════════════════════════════════
st.subheader("Does a country's wealth determine its survival?")
st.caption("Total deaths per million vs GDP per capita — all countries, focus countries highlighted")

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    scatter_base = (
        df_all[
            (df_all["date"] >= d0) &
            (df_all["date"] <= d1)
        ]
        .groupby("location")
        .agg(
            gdp    = ("gdp_per_capita",          "first"),
            deaths = ("total_deaths_per_million", "max"),
        )
        .reset_index()
        .dropna(subset=["gdp", "deaths"])
    )

    is_focus = scatter_base["location"].isin(selected)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    dark_ax(ax2, fig2)
    ax2.xaxis.grid(True, color="#1e293b", linewidth=0.6)

    # Background: all other countries in gray
    bg = scatter_base[~is_focus]
    sns.scatterplot(
        data=bg, x="gdp", y="deaths",
        color="#334155", alpha=0.45, s=22, ax=ax2, zorder=1, legend=False
    )

    # Regression line across all countries
    log_gdp = np.log1p(scatter_base["gdp"])
    slope, intercept, r_val, *_ = stats.linregress(log_gdp, scatter_base["deaths"])
    x_fit = np.linspace(scatter_base["gdp"].min(), scatter_base["gdp"].max(), 300)
    y_fit = slope * np.log1p(x_fit) + intercept
    ax2.plot(x_fit, y_fit, color="#475569", linewidth=1.5, linestyle="--",
             label=f"Global trend  (r = {r_val:.2f})", zorder=2)

    # Focus countries: colored and labeled
    for _, row in scatter_base[is_focus].iterrows():
        col  = COLORS.get(row["location"], "#94a3b8")
        size = 160 if row["location"] == "Mexico" else 85
        ax2.scatter(row["gdp"], row["deaths"], color=col, s=size,
                    zorder=4, edgecolors="white", linewidths=0.6)
        ax2.annotate(
            row["location"],
            (row["gdp"], row["deaths"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=8.5, color=col, fontweight="bold"
        )

    ax2.set_xlabel("GDP per Capita (USD)",     color="#94a3b8", fontsize=10)
    ax2.set_ylabel("Total Deaths per Million",  color="#94a3b8", fontsize=10)
    ax2.set_title(
        "GDP per Capita vs Total Deaths per Million",
        color="#e2e8f0", fontsize=13, pad=10
    )
    ax2.legend(fontsize=9, facecolor="#1e293b",
               edgecolor="#334155", labelcolor="#e2e8f0")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

with col_insight:
    st.markdown("#### What this reveals")
    st.markdown("""
    The relationship between wealth and COVID mortality is weaker than
    expected — and in some cases inverted.

    **Mexico** sits below the global trend line, meaning it reported fewer
    deaths than its GDP level would predict. This likely reflects
    undertesting rather than effective containment.

    **Peru** is the most dramatic outlier globally: middle-income, yet
    the highest deaths per million in the world.

    **Chile** demonstrates what good pandemic management looks like within
    the region — comparable GDP to peers, yet significantly lower mortality.

    The weak positive trend (r ~ 0.3) reflects a reporting paradox: wealthier
    countries tested more, counted more, and appear worse on paper.
    """)

st.divider()

# ════════════════════════════════════════════════════════════
# CHART 3 — Vaccination race  [PLOTLY]
# ════════════════════════════════════════════════════════════
st.subheader("Who vaccinated fastest — and did timing matter?")
st.caption("Population fully vaccinated over time (%)")

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    vacc_df = df.dropna(subset=["people_fully_vaccinated_per_hundred"])
    fig3 = go.Figure()

    for country in selected:
        cdata     = vacc_df[vacc_df["location"] == country]
        is_mexico = country == "Mexico"
        if cdata.empty:
            continue
        fig3.add_trace(go.Scatter(
            x=cdata["date"],
            y=cdata["people_fully_vaccinated_per_hundred"],
            name=country,
            line=dict(
                color=COLORS.get(country, "#94a3b8"),
                width=3 if is_mexico else 1.5,
                dash="solid" if is_mexico else "dot"
            ),
            opacity=1.0 if is_mexico else 0.75,
            fill="tozeroy" if is_mexico else "none",
            fillcolor="rgba(230,57,70,0.07)" if is_mexico else None
        ))

    fig3.add_hline(
        y=70, line_dash="dash", line_color="#64748b",
        annotation_text="70% threshold",
        annotation_font_color="#94a3b8"
    )

    fig3 = style_plotly(fig3, "Population Fully Vaccinated Over Time (%)")
    fig3.update_layout(yaxis_title="% Fully Vaccinated", yaxis_range=[0, 100])
    st.plotly_chart(fig3, use_container_width=True)

with col_insight:
    st.markdown("#### What this reveals")
    st.markdown("""
    The vaccination race reveals a decisive regional divide.

    **Chile** (gold) deployed one of the fastest campaigns in the world,
    reaching 70% coverage well ahead of any Latin American peer.
    Its lower mortality in later waves is directly linked to this lead.

    **Mexico** (red) accelerated its rollout after its deadly second wave
    in early 2021 had already peaked. Coverage ultimately reached moderate
    levels, but the critical window had passed.

    **Timing mattered more than total coverage.** Countries that vaccinated
    early — before major variant waves — saw the strongest mortality
    reductions. Late vaccination, even at high rates, provided diminishing
    returns as population immunity from prior infection had already spread.
    """)

st.divider()

# ════════════════════════════════════════════════════════════
# CHART 4 — Case Fatality Rate  [MATPLOTLIB]
# ════════════════════════════════════════════════════════════
st.subheader("Which countries had the highest case fatality rates?")
st.caption("CFR = total confirmed deaths / total confirmed cases")

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    cfr_df = (
        df.sort_values("date")
        .groupby("location")
        .last()
        .reset_index()
        [["location", "total_cases", "total_deaths"]]
        .dropna()
        .copy()
    )
    cfr_df["CFR"] = cfr_df["total_deaths"] / cfr_df["total_cases"] * 100
    cfr_df = cfr_df.sort_values("CFR", ascending=True)

    bar_colors = [COLORS.get(loc, "#475569") for loc in cfr_df["location"]]

    fig4, ax4 = plt.subplots(figsize=(10, max(3.5, len(cfr_df) * 0.55)))
    dark_ax(ax4, fig4)

    bars = ax4.barh(
        cfr_df["location"], cfr_df["CFR"],
        color=bar_colors, height=0.55, edgecolor="none"
    )

    for bar in bars:
        w = bar.get_width()
        ax4.text(
            w + 0.04, bar.get_y() + bar.get_height() / 2,
            f"{w:.2f}%", va="center", ha="left",
            color="#94a3b8", fontsize=9
        )

    ax4.set_xlabel("Case Fatality Rate (%)", color="#94a3b8", fontsize=10)
    ax4.set_title(
        "Case Fatality Rate by Country",
        color="#e2e8f0", fontsize=13, pad=10
    )
    ax4.spines[["left", "bottom"]].set_color("#334155")
    ax4.xaxis.grid(True, color="#1e293b", linewidth=0.6)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

with col_insight:
    st.markdown("#### What this reveals")
    st.markdown("""
    Mexico consistently records one of the highest case fatality rates
    among all comparison countries — significantly above Chile and Colombia,
    and far above the United States.

    Two factors compound to produce this result:

    **Undertesting.** Mexico conducted far fewer tests per capita than the
    US or Germany, meaning millions of mild infections went uncounted.
    This shrinks the denominator and inflates the CFR.

    **Late hospital arrivals.** Studies from Mexican public hospitals
    documented that patients consistently arrived in more critical condition
    than peers in wealthier nations — a reflection of barriers to early
    healthcare access.

    Together, these point to a systemic failure in early detection and
    community-level care, not simply a more deadly variant.
    """)

st.divider()

# ════════════════════════════════════════════════════════════
# CHART 5 — Structural vulnerability heatmap  [SEABORN]
# ════════════════════════════════════════════════════════════
st.subheader("Was Mexico structurally more vulnerable before the pandemic?")
st.caption("Normalized health indicators across selected countries — actual values shown in cells")

col_chart, col_insight = st.columns([2, 1])

with col_chart:
    agg_map = {
        "diabetes_prevalence":                "first",
        "cardiovasc_death_rate":              "first",
        "hospital_beds_per_thousand":         "first",
        "total_deaths_per_million":           "max",
        "people_fully_vaccinated_per_hundred":"max",
    }
    rename_map = {
        "diabetes_prevalence":                "Diabetes (%)",
        "cardiovasc_death_rate":              "Cardiovasc. Deaths",
        "hospital_beds_per_thousand":         "Hospital Beds /1k",
        "total_deaths_per_million":           "COVID Deaths /M",
        "people_fully_vaccinated_per_hundred":"Vaccinated (%)",
    }

    comorb_df = (
        df_all[df_all["location"].isin(selected)]
        .groupby("location")
        .agg(agg_map)
        .rename(columns=rename_map)
        .dropna(thresh=3)
    )

    norm_df = (comorb_df - comorb_df.min()) / (
        (comorb_df.max() - comorb_df.min()).replace(0, 1)
    )

    annot_df = comorb_df.round(1).map(
        lambda x: f"{x:.1f}" if pd.notna(x) else ""
    )

    fig5, ax5 = plt.subplots(figsize=(11, max(3.5, len(comorb_df) * 0.65)))
    fig5.patch.set_facecolor("#0f1117")
    ax5.set_facecolor("#0f1117")

    sns.heatmap(
        norm_df,
        ax=ax5,
        cmap="Blues",
        linewidths=0.5,
        linecolor="#1e293b",
        annot=annot_df,
        fmt="",
        annot_kws={"size": 9, "color": "#0f172a"},
        cbar_kws={"label": "Relative scale  (0 = lowest, 1 = highest)"},
        vmin=0, vmax=1
    )

    ax5.set_title(
        "Structural Health Indicators by Country",
        color="#e2e8f0", fontsize=13, pad=12
    )
    ax5.set_xlabel("")
    ax5.set_ylabel("")
    ax5.tick_params(colors="#94a3b8", labelsize=9)
    plt.xticks(rotation=25, ha="right")

    cbar5 = ax5.collections[0].colorbar
    plt.setp(cbar5.ax.yaxis.get_ticklabels(), color="#94a3b8", fontsize=8)
    cbar5.set_label(
        "Relative scale  (0 = lowest, 1 = highest)",
        color="#94a3b8", fontsize=8
    )

    plt.tight_layout()
    st.pyplot(fig5)
    plt.close()

with col_insight:
    st.markdown("#### What this reveals")
    st.markdown("""
    This heatmap profiles each country on the structural health factors
    that shaped pandemic vulnerability — before COVID-19 arrived.

    **Mexico** stands out clearly for its high diabetes prevalence —
    among the highest of any comparison country. Diabetes was identified
    within the first weeks of the pandemic as a major independent risk
    factor for severe illness and death.

    Combined with lower hospital bed density than Germany or the US,
    Mexico entered the pandemic with a high-risk population and limited
    capacity to treat severe cases.

    **Chile's** comparatively lower comorbidity burden and higher hospital
    capacity help explain its better outcomes — its success was not purely
    policy, but also a stronger health baseline going in.
    """)

st.divider()

# ════════════════════════════════════════════════════════════
# LIMITATIONS & RECOMMENDATIONS
# ════════════════════════════════════════════════════════════
st.subheader("Limitations and Recommendations")

col_lim, col_rec = st.columns(2)

with col_lim:
    st.markdown("#### Data Limitations")
    st.markdown("""
    **Systematic undertesting in Mexico.** Mexico conducted significantly
    fewer tests per capita than the United States or European peers.
    Confirmed case counts substantially understate true infection rates,
    inflating CFR figures and understating the true death toll.

    **Excess mortality gap.** Independent estimates place Mexico's true
    pandemic death toll at two to three times the official figures once
    excess mortality is accounted for. This analysis uses only confirmed deaths.

    **Vaccination reporting gaps.** Some early periods of Mexico's
    state-level rollout show inconsistent daily reporting, creating
    artificial flat periods in the vaccination curve.

    **Comorbidity data is pre-pandemic.** Diabetes and cardiovascular
    figures reflect pre-2020 baselines and do not capture changes
    during the crisis itself.
    """)

with col_rec:
    st.markdown("#### Policy Recommendations")
    st.markdown("""
    **1. Build a permanent national sentinel surveillance system.**
    Mexico's core structural gap was the inability to detect and count
    cases accurately. A decentralized, always-on testing network would
    fundamentally change early-warning capacity in future outbreaks.

    **2. Treat chronic disease reduction as pandemic preparedness.**
    Mexico's diabetes burden was a pre-existing vulnerability that
    requires decade-long investment beginning now.

    **3. Adopt Chile's vaccine procurement model.**
    Chile's speed advantage came from pre-negotiated multi-supplier
    contracts and military-assisted distribution. Mexico should formalize
    equivalent mechanisms before the next health emergency.

    **4. Expand ICU capacity in public hospitals.**
    The high CFR reflects late-stage hospital arrivals and insufficient
    critical care. Investment in public ICU capacity has the highest
    marginal return on survival rates for low-income patients.
    """)

st.divider()
st.caption(
    "Data: Our World in Data COVID-19 Dataset — ourworldindata.org/covid  |  "
    "License: CC BY 4.0  |  "
    "Built with Streamlit, Plotly, Seaborn, Matplotlib"
)
