import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# ✅ 1️⃣ Simple Password Gate
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
    st.title("📊 Suicide Mean Age Dashboard (Compact View)")

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    # -------------------------------
    # ✅ 3️⃣ Compact Filters in One Row
    # -------------------------------
    with st.container():
        col1, col2, col3 = st.columns(3)

        selected_locations = col1.multiselect(
            "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
        )
        selected_sexes = col2.multiselect(
            "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
        )
        selected_years = col3.multiselect(
            "Year(s)", sorted(df['year_id'].unique()), default=sorted(df['year_id'].unique())
        )

    # -------------------------------
    # ✅ 4️⃣ Filtered Data
    # -------------------------------
    filtered_df = df[
        df['location_name'].isin(selected_locations) &
        df['sex_name'].isin(selected_sexes) &
        df['year_id'].isin(selected_years)
    ]

    # -------------------------------
    # ✅ 5️⃣ Compact Key Insights
    # -------------------------------
    col1, col2 = st.columns(2)
    col1.metric("Mean Age", f"{filtered_df['val'].mean():.2f} years")
    col2.metric("Age Range", f"{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}")

    # -------------------------------
    # ✅ 6️⃣ Single Trend Chart (no facets)
    # -------------------------------
    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x="year_id",
            y="val",
            color="sex_name",
            markers=True,
            labels={"year_id": "Year", "val": "Mean Age"},
            title=""
        )
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

    # -------------------------------
    # ✅ 7️⃣ Hidden Table (optional)
    # -------------------------------
    with st.expander("Show Data Table (optional)"):
        st.dataframe(filtered_df, height=200)

    st.caption("✅ Compact dashboard • Streamlit • IHME GBD 2021")
