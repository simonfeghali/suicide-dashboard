import streamlit as st
import pandas as pd
import plotly.express as px

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

    # ✅ Bulletproof single-row multiselect chips with scroll
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            h2 { margin-top: 0; }
            .small-metric { font-size: 15px !important; line-height: 1.2; }
            .column-title { font-size: 16px !important; font-weight: bold; text-align: center; margin-bottom: 0px; }

            div[data-baseweb="tag"] {
                display: flex;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                white-space: nowrap;
                max-height: 40px;
            }

            div[data-baseweb="select"] {
                min-height: 40px !important;
                font-size: 14px !important;
                align-items: flex-start !important;
            }

            label { font-size: 14px !important; }
            .left-column { max-width: 250px; padding-right: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # ✅ Main Title & subtitle
    st.markdown("""
        <div style='text-align: center;'>
            <h2 style='margin-bottom: 5px;'>Exploring the Mean Age of Suicide Mortality</h2>
            <p style='font-size: 16px; font-style: italic;'>Data Source: IHME GBD 2021</p>
        </div>
    """, unsafe_allow_html=True)

    # ✅ Load data
    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()

    # ✅ Column titles
    title_col1, title_col2, title_col3 = st.columns([0.8, 1.6, 1.6])
    with title_col1:
        st.markdown('<p class="column-title">Controls & Insights</p>', unsafe_allow_html=True)
    with title_col2:
        st.markdown('<p class="column-title">Ranked & Map</p>', unsafe_allow_html=True)
    with title_col3:
        st.markdown('<p class="column-title">Distribution & Boxplot</p>', unsafe_allow_html=True)

    # ✅ Main layout: left filters, right plots
    col_left, col_right = st.columns([0.7, 3.3])  # slightly narrower left panel

    with col_left:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)

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

        # ✅ Filtering
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

        st.markdown("<hr style='margin: 0.75rem 0'>", unsafe_allow_html=True)

        if not filtered_df.empty:
            mean_age = filtered_df['val'].mean()
            min_age = filtered_df['val'].min()
            max_age = filtered_df['val'].max()

            insights_html = [
                f"Overall Mean Age: <b>{mean_age:.2f} years</b>",
                f"Age Range: <b>{min_age:.2f} - {max_age:.2f}</b><br>",
                "<b>Mean Age by Sex:</b>"
            ]

            sex_stats = filtered_df.groupby("sex_name")["val"].mean().reset_index()
            for _, row in sex_stats.iterrows():
                insights_html.append(f"{row['sex_name']}: <b>{row['val']:.2f} years</b>")

            full_insights_html = f"<div class='small-metric'>{'<br>'.join(insights_html)}</div>"
            st.markdown(full_insights_html, unsafe_allow_html=True)
        else:
            st.warning("Please select filters to see data.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ Right: compact multi-plots
    with col_right:
        # ✅ Row 1: Bar & Map
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
                if not avg_loc.empty:
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

        # ✅ Row 2: Histogram & Boxplot
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
            st.write("**Mean Age by Sex (Boxplot)**")
            if not filtered_df.empty:
                fig_box = px.box(
                    filtered_df, x="sex_name", y="val",
                    color="sex_name",
                    labels={"sex_name": "Sex", "val": "Mean Age"},
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                fig_box.update_layout(height=250, margin=dict(l=5, r=5, t=5, b=5))
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.warning("No data for boxplot.")
