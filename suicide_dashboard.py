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
    # --- PAGE CONFIG AND CSS ---
    st.set_page_config(layout="wide")

    # This CSS block now includes the strict single-line rule
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }

            /* --- NEW CSS FOR STRICTLY SINGLE-LINE MULTISELECT --- */
            div[data-testid="stMultiSelect"] > div > div {
                /* Prevent the selected items from wrapping to the next line */
                flex-wrap: nowrap;
                /* Add a horizontal scrollbar if the items overflow */
                overflow-x: auto;
            }
            /* --- END OF NEW CSS --- */
        </style>
        """, unsafe_allow_html=True)

    # --- TITLE ---
    st.markdown("""
        <div style='text-align: center;'>
            <h2>Exploring the Mean Age of Suicide Mortality</h2>
            <p style='font-size: 14px; font-style: italic; margin-top: -10px; margin-bottom: 20px;'>Data Source: IHME GBD 2021</p>
        </div>
    """, unsafe_allow_html=True)


    # --- DATA LOADING ---
    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()
    all_locations = sorted(df['location_name'].unique())
    all_sexes = sorted(df['sex_name'].unique())
    all_years = sorted(df['year_id'].unique())


    # --- MAIN LAYOUT (SIDEBAR & MAIN CONTENT) ---
    with st.sidebar:
        st.markdown("### Controls & Insights")

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
                (df['location_name'].isin(st.session_state.locations_filter)) &
                (df['sex_name'].isin(st.session_state.sexes_filter)) &
                (df['year_id'].isin(st.session_state.years_filter))
            ]

        st.markdown("---")

        if not filtered_df.empty:
            mean_age = filtered_df['val'].mean()
            min_age = filtered_df['val'].min()
            max_age = filtered_df['val'].max()

            st.metric("Overall Mean Age", f"{mean_age:.2f} years")
            st.metric("Age Range", f"{min_age:.2f} - {max_age:.2f}")

            st.write("**Mean Age by Sex:**")
            sex_stats = filtered_df.groupby("sex_name")["val"].mean()
            for sex, val in sex_stats.items():
                st.text(f"- {sex}: {val:.2f} years")
        else:
            st.warning("Please select filters to see data.")

    # --- PLOTS (MAIN CONTENT AREA) ---
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
            fig_ranked.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5))
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
            fig_map.update_layout(height=300, margin=dict(l=0, r=0, t=5, b=5))
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
            fig_hist.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5))
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
            fig_box.update_layout(height=300, margin=dict(l=5, r=5, t=5, b=5))
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No data for boxplot.")
