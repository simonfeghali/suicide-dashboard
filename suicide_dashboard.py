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
# ✅ 2️⃣ Run if password OK
# -------------------------------
if check_password():
    st.set_page_config(layout="wide")
    # Tight styling
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            h1 { margin-top: 0; margin-bottom: 1rem; }
            .small-metric { font-size: 18px !important; }
            div[data-baseweb="select"] { max-height: 150px; overflow-y: auto; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>📊 Suicide Mean Age Dashboard (Pro Version)</h1>", unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        return pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")

    df = load_data()

    # -------------------------------
    # ✅ Layout: Left = Filters + Insights | Right = 2 advanced plots
    # -------------------------------
    col_left, col_right = st.columns([1, 3])

    # -------------------------------
    # ✅ Left: Filters & Insights stacked
    # -------------------------------
    with col_left:
        st.subheader("🎛️ Filters")
        selected_locations = st.multiselect(
            "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
        )
        selected_sexes = st.multiselect(
            "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
        )
        with st.expander("Select Year(s)"):
            selected_years = st.multiselect(
                "", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
            )

        filtered_df = df[
            df['location_name'].isin(selected_locations) &
            df['sex_name'].isin(selected_sexes) &
            df['year_id'].isin(selected_years)
        ]

        st.subheader("📌 Insights")
        st.markdown(f"<div class='small-metric'>Mean Age: <b>{filtered_df['val'].mean():.2f} years</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-metric'>Age Range: <b>{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}</b></div>", unsafe_allow_html=True)

    # -------------------------------
    # ✅ Right: Advanced charts
    # -------------------------------
    with col_right:
        st.subheader("📊 Advanced Insights")

        chart_col1, chart_col2 = st.columns(2)

        # ✅ Chart 1: Grouped bar by Sex & Year
        with chart_col1:
            st.write("**Mean Age by Sex & Year**")
            if not filtered_df.empty:
                grouped = filtered_df.groupby(["year_id", "sex_name"])["val"].mean().reset_index()
                fig_grouped = px.bar(
                    grouped,
                    x="year_id",
                    y="val",
                    color="sex_name",
                    barmode="group",
                    labels={"year_id": "Year", "val": "Mean Age", "sex_name": "Sex"},
                    title=""
                )
                fig_grouped.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_grouped, use_container_width=True)
            else:
                st.warning("No data to show grouped chart.")

        # ✅ Chart 2: Sorted horizontal bar by Location
        with chart_col2:
            st.write("**Mean Age by Location (Ranked)**")
            if not filtered_df.empty:
                avg_loc = filtered_df.groupby("location_name")["val"].mean().reset_index()
                avg_loc = avg_loc.sort_values("val", ascending=True)
                fig_ranked = px.bar(
                    avg_loc,
                    x="val",
                    y="location_name",
                    orientation="h",
                    color="val",
                    color_continuous_scale="Viridis",
                    labels={"val": "Mean Age", "location_name": "Location"},
                    title=""
                )
                fig_ranked.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_ranked, use_container_width=True)
            else:
                st.warning("No data to show ranking chart.")

    st.markdown(
        "<hr style='margin-top: 20px; margin-bottom: 10px;'>"
        "<div style='text-align: center;'>✅ Pro Dashboard • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
