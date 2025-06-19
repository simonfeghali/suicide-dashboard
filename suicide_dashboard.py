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
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Wrong password")
        return False
    else:
        return True

# -------------------------------
# ✅ 2️⃣ Main App
# -------------------------------
if check_password():
    st.set_page_config(layout="wide")

    # ✅ CSS: force single row chips + horizontal scroll
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            h1 { margin-top: 0; margin-bottom: 1rem; }
            .small-metric { font-size: 16px !important; }

            /* Target the container that holds all the selected "chips" */
            div[data-baseweb="select"] > div:first-child {
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
            }

            /* Force the multiselect widget itself to a fixed, single-line height */
            div[data-baseweb="select"] {
                max-height: 50px;
                overflow-y: hidden;
                font-size: 14px !important;
            }

            label {
                font-size: 14px !important;
            }

            .left-column {
                max-width: 250px;
                padding-right: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>📊 Suicide Mean Age Dashboard — Single Row Filters</h1>", unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()

    # ✅ Narrower left column
    col_left, col_right = st.columns([0.8, 3.2])

    with col_left:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)

        st.subheader("🎛️ Filters")

        selected_locations = st.multiselect(
            "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
        )

        selected_sexes = st.multiselect(
            "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
        )

        selected_years = st.multiselect(
            "Year(s)", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
        )

        # ✅ Apply filters
        filtered_df = df[
            df['location_name'].isin(selected_locations) &
            df['sex_name'].isin(selected_sexes) &
            df['year_id'].isin(selected_years)
        ]

        # -------------------------------
        # ⭐️ CHANGE 1: ADD VIEW OPTIONS ⭐️
        # -------------------------------
        st.subheader("⚙️ View Options")
        show_all = st.checkbox("Show all locations in ranked chart", value=False)
        st.info("The map always shows all locations from the filters above.")

        st.subheader("📌 Insights")
        if not filtered_df.empty:
            mean_age = filtered_df['val'].mean()
            min_age = filtered_df['val'].min()
            max_age = filtered_df['val'].max()

            st.markdown(f"<div class='small-metric'>Overall Mean Age: <b>{mean_age:.2f} years</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-metric'>Age Range: <b>{min_age:.2f} - {max_age:.2f}</b></div>", unsafe_allow_html=True)

            st.markdown("<b>Mean Age by Sex:</b>", unsafe_allow_html=True)
            sex_stats = filtered_df.groupby("sex_name")["val"].mean().reset_index()
            for _, row in sex_stats.iterrows():
                st.markdown(f"<div class='small-metric'>{row['sex_name']}: <b>{row['val']:.2f} years</b></div>", unsafe_allow_html=True)
        else:
            st.warning("No data to show for selected filters.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.subheader("📊 Ranked Data + Map")

        chart_col1, chart_col2 = st.columns(2)

        # ------------------------------------------------------------------
        # ⭐️ CHANGE 2: MODIFY RANKED BAR CHART LOGIC AND TITLE ⭐️
        # ------------------------------------------------------------------
        with chart_col1:
            # Dynamic title based on the checkbox state
            ranked_chart_title = (
                "**Top 12 Ranked Mean Age by Location**"
                if not show_all
                else "**Ranked Mean Age by Location (All)**"
            )
            st.write(ranked_chart_title)
            
            if not filtered_df.empty:
                # First, prepare the full sorted data
                avg_loc_all = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .sort_values("val", ascending=True)
                )

                # Conditionally decide which data to display
                if not show_all:
                    data_to_display = avg_loc_all.head(12)
                else:
                    data_to_display = avg_loc_all

                if not data_to_display.empty:
                    # Height is dynamic based on the number of rows being displayed
                    height = max(400, len(data_to_display) * 25 + 100)
                    fig_ranked = px.bar(
                        data_to_display,
                        x="val",
                        y="location_name",
                        orientation="h",
                        color="val",
                        color_continuous_scale="Blues",
                        labels={"val": "Mean Age", "location_name": "Location"},
                    )
                    fig_ranked.update_yaxes(automargin=True, categoryorder="total ascending")
                    fig_ranked.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_ranked, use_container_width=True)
                else:
                    st.warning("No data for ranking chart.")
            else:
                st.warning("No data for ranking chart.")

        # ✅ 2️⃣ Choropleth Map (No changes needed here, it already shows all data)
        with chart_col2:
            st.write("**🌍 Mean Age by Location (Map)**")
            if not filtered_df.empty:
                avg_map = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .rename(columns={"location_name": "Country", "val": "Mean Age"})
                )
                fig_map = px.choropleth(
                    avg_map,
                    locations="Country",
                    locationmode="country names",
                    color="Mean Age",
                    color_continuous_scale="Viridis",
                    title="",
                    labels={"Mean Age": "Mean Age"},
                )
                fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No data for map.")

    st.markdown(
        "<hr style='margin-top: 20px; margin-bottom: 10px;'>"
        "<div style='text-align: center;'>✅ Single Row Filters • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
