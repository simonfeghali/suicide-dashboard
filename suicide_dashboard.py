import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 1. Password Gate
# -------------------------------
def check_password():
    """Returns `True` if the user has the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "123456":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "🔒 Enter password:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "🔒 Enter password:", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Wrong password")
        return False
    else:
        # Password correct.
        return True

# -------------------------------
# 2. Main App
# -------------------------------
if check_password():
    st.set_page_config(layout="wide")

    # --- Custom CSS for styling ---
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            h1 { margin-top: 0; margin-bottom: 1rem; }
            .small-metric { font-size: 15px !important; line-height: 1.2; }
            .column-title { font-size: 16px !important; font-weight: bold; text-align: center; margin-bottom: 0px; }
            /* Single-line multiselect styles */
            div[data-baseweb="select"] > div:first-child { flex-wrap: nowrap !important; overflow-x: auto !important; }
            div[data-baseweb="select"] {
                max-height: 50px;
                overflow-y: hidden;
                font-size: 14px !important;
                align-items: flex-start !important; /* Forces icons to stay at the top */
            }
            label { font-size: 14px !important; }
            .left-column { max-width: 250px; padding-right: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- Main Title with Data Source Subtitle ---
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='margin-bottom: 5px;'>Exploring the Mean Age of Suicide Mortality</h1>
            <p style='font-size: 16px; font-style: italic;'>Data Source: IHME GBD 2021</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Data Loading ---
    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()

    # --- Aligned Title Row ---
    title_col1, title_col2, title_col3 = st.columns([0.8, 1.6, 1.6])
    with title_col1:
        st.markdown('<p class="column-title">Controls & Insights</p>', unsafe_allow_html=True)
    with title_col2:
        st.markdown('<p class="column-title">Top 12 Ranked Mean Age by Location</p>', unsafe_allow_html=True)
    with title_col3:
        st.markdown('<p class="column-title">Mean Age by Location (Map)</p>', unsafe_allow_html=True)

    # --- Main Content Row ---
    col_left, col_right = st.columns([0.8, 3.2])

    # --- Left Column: Controls & Insights ---
    with col_left:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)
        
        all_locations = sorted(df['location_name'].unique())
        all_sexes = sorted(df['sex_name'].unique())
        all_years = sorted(df['year_id'].unique())
        
        # Initialize session state for all filters on first run
        if "global_view_checkbox" not in st.session_state:
            st.session_state.global_view_checkbox = False
            st.session_state.locations_filter = []  # Default to empty
            st.session_state.sexes_filter = all_sexes
            st.session_state.years_filter = all_years
        
        # Reset button logic
        if st.button("Reset All Filters"):
            st.session_state.global_view_checkbox = False
            st.session_state.locations_filter = []
            st.session_state.sexes_filter = all_sexes
            st.session_state.years_filter = all_years
            st.rerun()

        # Filter widgets bound to session state
        st.checkbox(
            "Show top 12 locations globally",
            key="global_view_checkbox",
            help="Ignores the 'Location(s)' filter to find the top 12 across all data."
        )
        
        st.multiselect(
            "Location(s)", all_locations,
            key="locations_filter",
            disabled=st.session_state.global_view_checkbox
        )
        
        st.multiselect("Sex(es)", all_sexes, key="sexes_filter")
        st.multiselect("Year(s)", all_years, key="years_filter")
        
        # Filtering logic using session state
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

        # Insights display
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
            st.warning("Please select at least one location to see data.")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- Right Column: Charts ---
    with col_right:
        chart_col1, chart_col2 = st.columns(2)

        # Bar chart
        with chart_col1:
            if not filtered_df.empty:
                avg_loc = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .sort_values("val", ascending=False)
                    .head(12)
                )
                if not avg_loc.empty:
                    height = max(400, len(avg_loc) * 25 + 100)
                    fig_ranked = px.bar(
                        avg_loc, x="val", y="location_name", orientation="h",
                        color="val",
                        color_continuous_scale="Viridis",
                        labels={"val": "Mean Age", "location_name": "Location"},
                    )
                    fig_ranked.update_yaxes(automargin=True, categoryorder="total ascending")
                    fig_ranked.update_layout(
                        height=height, margin=dict(l=10, r=10, t=0, b=10),
                        title_text=None
                    )
                    st.plotly_chart(fig_ranked, use_container_width=True)
                else:
                    st.warning("No data for ranking chart. Please select a location.")
            else:
                st.warning("No data for ranking chart. Please select a location.")

        # Map chart
        with chart_col2:
            if not filtered_df.empty:
                avg_map = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .rename(columns={"location_name": "Country", "val": "Mean Age"})
                )
                fig_map = px.choropleth(
                    avg_map, locations="Country", locationmode="country names",
                    color="Mean Age",
                    color_continuous_scale="Viridis",
                    labels={"Mean Age": "Mean Age"},
                )
                fig_map.update_layout(
                    mapbox_style="carto-positron",
                    mapbox_zoom=0.5,
                    mapbox_center={"lat": 30, "lon": 0},
                    height=500,
                    margin=dict(l=0, r=0, t=0, b=0),
                    title_text=None
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No data for map. Please select a location.")
