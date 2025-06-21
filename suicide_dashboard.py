import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import statsmodels.api as sm  # ✅ ARIMA

# -------------------------------
# ✅ 1️⃣ Password Gate
# -------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "123456":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔒 Enter password:", type="password",
            on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Enter password:", type="password",
            on_change=password_entered, key="password"
        )
        st.error("❌ Wrong password")
        return False
    else:
        return True

# -------------------------------
# ✅ 2️⃣ Main App
# -------------------------------
if check_password():
    st.set_page_config(layout="wide")

    # ✅ CSS for compact filters
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0rem !important;
            }
            .left-column {
                max-width: 250px;
                padding-right: 10px;
                margin-top: 0 !important;
            }
            div[data-baseweb="select"] {
                min-height: 36px !important;
                font-size: 12px !important;
            }
            div[data-baseweb="select"] > div:first-child {
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                white-space: nowrap;
            }
            span[data-baseweb="tag"] {
                font-size: 11px !important;
                height: 22px !important;
                margin: 1px !important;
                padding: 2px 4px !important;
            }
            div[data-testid="stCheckbox"] {
                margin: 0 0 0.2rem 0;
            }
            div.stButton > button {
                font-size: 12px !important;
                padding: 0.25rem 0.7rem;
                margin-bottom: 0.3rem;
            }
            label {
                font-size: 12px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ✅ MAIN 2 COLUMN LAYOUT:
    col_left, col_right = st.columns([0.7, 3.3])

    # ✅ LEFT COLUMN — Filters only
    with col_left:
        st.markdown('<div class="left-column" style="margin-top: 0;">', unsafe_allow_html=True)

        @st.cache_data
        def load_data():
            return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

        df = load_data()

        all_locations = sorted(df['location_name'].unique())
        all_sexes = sorted(df['sex_name'].unique())
        all_years = sorted(df['year_id'].unique())

        if "global_view_checkbox" not in st.session_state:
            st.session_state.global_view_checkbox = False
            st.session_state.locations_filter = []
            st.session_state.sexes_filter = all_sexes
            st.session_state.years_filter = all_years

        if st.button("Reset All Filters"):
            st.session_state.global_view_checkbox = False
            st.session_state.locations_filter = []
            st.session_state.sexes_filter = all_sexes
            st.session_state.years_filter = all_years
            st.rerun()

        st.checkbox(
            "Show top 12 locations globally",
            key="global_view_checkbox",
            help="Ignores the 'Location(s)' filter to find the top 12 globally."
        )
        st.multiselect(
            "Location(s)", all_locations,
            key="locations_filter",
            disabled=st.session_state.global_view_checkbox
        )
        st.multiselect("Sex(es)", all_sexes, key="sexes_filter")
        st.multiselect("Year(s)", all_years, key="years_filter")

        if st.session_state.global_view_checkbox:
            filtered_df = df[
                df['sex_name'].isin(st.session_state.sexes_filter) &
                df['year_id'].isin(st.session_state.years_filter)
            ]
        else:
            filtered_df = df[
                df['location_name'].isin(st.session_state.locations_filter) &
                df['sex_name'].isin(st.session_state.sexes_filter) &
                df['year_id'].isin(st.session_state.years_filter)
            ]

        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ RIGHT COLUMN — TITLE + PLOTS
    with col_right:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 0.5rem;'>
                <h2>Exploring the Mean Age of Suicide Mortality</h2>
                <p style='font-size: 14px; font-style: italic; margin: 0;'>Data Source: IHME GBD 2021</p>
            </div>
        """, unsafe_allow_html=True)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.write("**Top 12 Ranked Mean Age by Location**")
            if not filtered_df.empty:
                avg_loc = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .sort_values("val", ascending=False)
                    .head(12)
                )
                fig_ranked = px.bar(
                    avg_loc, x="val", y="location_name", orientation="h",
                    color="val", color_continuous_scale="Viridis",
                    labels={"val": "Mean Age", "location_name": "Location"},
                )
                fig_ranked.update_yaxes(automargin=True, categoryorder="total ascending")
                fig_ranked.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5))
                st.plotly_chart(fig_ranked, use_container_width=True)
            else:
                st.warning("No data for bar chart.")

        with row1_col2:
            st.write("**Mean Age by Location (Map)**")
            if not filtered_df.empty:
                avg_map = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .rename(columns={"location_name": "Country", "val": "Mean Age"})
                )
                fig_map = px.choropleth(
                    avg_map, locations="Country", locationmode="country names",
                    color="Mean Age", color_continuous_scale="Viridis",
                    labels={"Mean Age": "Mean Age"},
                )
                fig_map.update_layout(height=250, margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No data for map.")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.write("**Mean Age Distribution (Histogram)**")
            if not filtered_df.empty:
                fig_hist = px.histogram(
                    filtered_df, x="val",
                    nbins=20, color_discrete_sequence=["#636EFA"],
                    labels={"val": "Mean Age"}
                )
                fig_hist.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5))
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("No data for histogram.")

        with row2_col2:
            st.write("**Forecasted Mean Age for Future Years (ARIMA)**")
            if not filtered_df.empty:
                try:
                    # Prepare yearly series
                    yearly_mean = (
                        filtered_df.groupby("year_id")["val"]
                        .mean().reset_index()
                        .sort_values("year_id")
                    )
                    y = yearly_mean["val"]
                    y.index = pd.Index(yearly_mean["year_id"])

                    # Fit ARIMA(1,1,1)
                    model = sm.tsa.ARIMA(y, order=(1, 1, 1)).fit()

                    # Forecast next 10 years
                    future = model.get_forecast(steps=10)
                    future_index = np.arange(y.index.max() + 1, y.index.max() + 11)
                    forecast_mean = future.predicted_mean
                    conf_int = future.conf_int()

                    # Plot historical + forecast + CI
                    fig = px.line(
                        x=np.concatenate([y.index, future_index]),
                        y=np.concatenate([y.values, forecast_mean]),
                        labels={"x": "Year", "y": "Mean Age"}
                    )

                    fig.add_scatter(
                        x=future_index,
                        y=conf_int.iloc[:, 0],
                        mode="lines",
                        line=dict(color="lightgrey"),
                        name="Lower CI"
                    )
                    fig.add_scatter(
                        x=future_index,
                        y=conf_int.iloc[:, 1],
                        mode="lines",
                        line=dict(color="lightgrey"),
                        name="Upper CI",
                        fill="tonexty"
                    )

                    fig.add_scatter(
                        x=y.index,
                        y=y.values,
                        mode="markers",
                        name="Historical Mean Age",
                        marker=dict(color="red", size=6)
                    )

                    fig.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"ARIMA model could not fit: {e}")
            else:
                st.warning("No data for forecast plot.")
