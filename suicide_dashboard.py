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
    # ✅ Custom CSS: tight padding + small metrics + small year selector
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        h1 {
            margin-top: 0rem;
            margin-bottom: 1rem;
        }
        .small-metric {
            font-size: 18px !important;
            color: #fff !important;
        }
        div[data-baseweb="select"] {
            max-height: 150px;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align: center;'>📊 Suicide Mean Age Dashboard (Compact)</h1>", unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    # -------------------------------
    # ✅ Layout: Left = Filters + Insights | Right = 2 charts
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
        # ✅ Make Year filter small by wrapping in expander OR controlling max height
        with st.expander("Select Year(s)"):
            selected_years = st.multiselect(
                "", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
            )

        # ✅ Filter data
        filtered_df = df[
            df['location_name'].isin(selected_locations) &
            df['sex_name'].isin(selected_sexes) &
            df['year_id'].isin(selected_years)
        ]

        st.subheader("📌 Insights")
        st.markdown(f"<div class='small-metric'>Mean Age: <b>{filtered_df['val'].mean():.2f} years</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-metric'>Age Range: <b>{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}</b></div>", unsafe_allow_html=True)

    # -------------------------------
    # ✅ Right: 2 charts side-by-side
    # -------------------------------
    with col_right:
        st.subheader("📊 Insights Charts")

        chart_col1, chart_col2 = st.columns(2)

        # ✅ Chart 1: Bar by Sex
        with chart_col1:
            st.write("**Mean Age by Sex**")
            if not filtered_df.empty:
                avg_by_sex = filtered_df.groupby("sex_name")["val"].mean().reset_index()
                fig_bar = px.bar(
                    avg_by_sex,
                    x="sex_name",
                    y="val",
                    color="sex_name",
                    labels={"val": "Mean Age", "sex_name": "Sex"},
                )
                fig_bar.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("No data to show bar chart.")

        # ✅ Chart 2: Bar by Location
        with chart_col2:
            st.write("**Mean Age by Location**")
            if not filtered_df.empty:
                avg_by_location = filtered_df.groupby("location_name")["val"].mean().reset_index()
                fig_location = px.bar(
                    avg_by_location,
                    x="location_name",
                    y="val",
                    color="location_name",
                    labels={"val": "Mean Age", "location_name": "Location"},
                )
                fig_location.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_location, use_container_width=True)
            else:
                st.warning("No data to show location chart.")

    st.markdown(
        "<hr style='margin-top: 20px; margin-bottom: 10px;'>"
        "<div style='text-align: center;'>✅ Compact Dashboard • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
