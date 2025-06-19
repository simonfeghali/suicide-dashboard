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
    st.markdown("<h1 style='text-align: center;'>📊 Suicide Mean Age Dashboard</h1>", unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    # -------------------------------
    # ✅ 3️⃣ 100% wide layout: [Filters] [big gap] [Insights] [big gap] [Chart]
    # -------------------------------
    col1, spacer1, col2, spacer2, col3 = st.columns([1, 0.5, 1, 0.5, 3])

    # -------------------------------
    # ✅ Column 1: Filters
    # -------------------------------
    with col1:
        st.header("🎛️ Filters")
        selected_locations = st.multiselect(
            "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
        )
        selected_sexes = st.multiselect(
            "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
        )
        selected_years = st.multiselect(
            "Year(s)", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
        )

    # -------------------------------
    # ✅ Apply Filters
    # -------------------------------
    filtered_df = df[
        df['location_name'].isin(selected_locations) &
        df['sex_name'].isin(selected_sexes) &
        df['year_id'].isin(selected_years)
    ]

    # -------------------------------
    # ✅ Column 2: Insights
    # -------------------------------
    with col2:
        st.header("📌 Insights")
        st.metric("Mean Age", f"{filtered_df['val'].mean():.2f} years")
        st.metric("Age Range", f"{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}")

    # -------------------------------
    # ✅ Column 3: Chart (+ Table)
    # -------------------------------
    with col3:
        st.header("📈 Chart")
        if not filtered_df.empty:
            fig = px.line(
                filtered_df,
                x="year_id",
                y="val",
                color="sex_name",
                markers=True,
                labels={"year_id": "Year", "val": "Mean Age"},
            )
            fig.update_layout(
                height=500, margin=dict(l=20, r=20, t=30, b=20),
                legend_title=None
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data for selected filters.")

        with st.expander("Show Filtered Data Table"):
            st.dataframe(filtered_df, height=200)

    st.markdown(
        "<hr style='margin-top: 30px; margin-bottom: 10px;'>"
        "<div style='text-align: center;'>✅ Clean Full-Screen Dashboard • IHME GBD 2021</div>",
        unsafe_allow_html=True
    )
