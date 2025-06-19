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

    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            h1 { margin-top: 0; margin-bottom: 1rem; }
            .small-metric { font-size: 18px !important; }
            div[data-baseweb="select"] { max-height: 150px; overflow-y: auto; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>📊 Suicide Mean Age Dashboard — Final Compact Filters</h1>", unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()

    # Layout: Left = Filters + Insights | Right = Top 12 bar + Map
    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.subheader("🎛️ Filters (One Row)")

        # ✅ Filters in one row using columns:
        fcol1, fcol2, fcol3 = st.columns(3)

        with fcol1:
            selected_locations = st.multiselect(
                "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
            )

        with fcol2:
            selected_sexes = st.multiselect(
                "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
            )

        with fcol3:
            selected_years = st.multiselect(
                "Year(s)", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
            )

        # Apply filters
        filtered_df = df[
            df['location_name'].isin(selected_locations) &
            df['sex_name'].isin(selected_sexes) &
            df['year_id'].isin(selected_years)
        ]

        st.subheader("📌 Insights")
        mean_age = filtered_df['val'].mean()
        min_age = filtered_df['val'].min()
        max_age = filtered_df['val'].max()

        st.markdown(f"<div class='small-metric'>Overall Mean Age: <b>{mean_age:.2f} years</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-metric'>Age Range: <b>{min_age:.2f} - {max_age:.2f}</b></div>", unsafe_allow_html=True)

        if not filtered_df.empty:
            st.markdown("<b>Mean Age by Sex:</b>", unsafe_allow_html=True)
            sex_stats = filtered_df.groupby("sex_name")["val"].mean().reset_index()
            for _, row in sex_stats.iterrows():
                st.markdown(f"<div class='small-metric'>{row['sex_name']}: <b>{row['val']:.2f} years</b></div>", unsafe_allow_html=True)
        else:
            st.warning("No data to show Mean Age by Sex.")

    with col_right:
        st.subheader("📊 Top 12 Ranked + Map")

        chart_col1, chart_col2 = st.columns(2)

        # ✅ 1️⃣ Ranked Horizontal Bar: Top 12 Locations
        with chart_col1:
            st.write("**Top 12 Ranked Mean Age by Location**")
            if not filtered_df.empty:
                avg_loc = (
                    filtered_df.groupby("location_name")["val"]
                    .mean().reset_index()
                    .sort_values("val", ascending=True)
                    .head(12)
                )
                height = max(400, len(avg_loc) * 30 + 100)
                fig_ranked = px.bar(
                    avg_loc,
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

        # ✅ 2️⃣ Choropleth Map
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
        "<div style='text-align: center;'>✅ Final Compact Filters Dashboard • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
