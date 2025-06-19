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
    # ✅ Full width + custom CSS for tight top alignment
    st.set_page_config(layout="wide")
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
    # ✅ Main layout: Left = Filters+Insights stacked, Right = 2 charts side-by-side
    # -------------------------------
    col_left, col_right = st.columns([1, 3])

    # -------------------------------
    # ✅ Left: Filters & Insights stacked vertically
    # -------------------------------
    with col_left:
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

        filtered_df = df[
            df['location_name'].isin(selected_locations) &
            df['sex_name'].isin(selected_sexes) &
            df['year_id'].isin(selected_years)
        ]

        st.subheader("📌 Insights")
        st.metric("Mean Age", f"{filtered_df['val'].mean():.2f} years")
        st.metric("Age Range", f"{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}")

    # -------------------------------
    # ✅ Right: 2 charts side-by-side in columns
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
        "<div style='text-align: center;'>✅ Clean Compact Dashboard • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
