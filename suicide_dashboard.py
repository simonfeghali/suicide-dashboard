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
    st.title("📊 Suicide Mean Age Dashboard (One-Page, Columns Layout)")

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    # -------------------------------
    # ✅ 3️⃣ Filters Row (in Columns)
    # -------------------------------
    filter_container = st.container()
    with filter_container:
        fcol1, fcol2, fcol3 = st.columns(3)
        selected_locations = fcol1.multiselect(
            "Location(s)", sorted(df['location_name'].unique()), default=["Global"]
        )
        selected_sexes = fcol2.multiselect(
            "Sex(es)", sorted(df['sex_name'].unique()), default=sorted(df['sex_name'].unique())
        )
        selected_years = fcol3.multiselect(
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
    # ✅ 5️⃣ Insights Row (in Columns)
    # -------------------------------
    insights_container = st.container()
    with insights_container:
        icol1, icol2 = st.columns(2)
        icol1.metric("Mean Age", f"{filtered_df['val'].mean():.2f} years")
        icol2.metric("Age Range", f"{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}")

    # -------------------------------
    # ✅ 6️⃣ Chart Row
    # -------------------------------
    chart_container = st.container()
    with chart_container:
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
                height=350, margin=dict(l=20, r=20, t=20, b=20),
                legend_title=None
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data for selected filters.")

    # -------------------------------
    # ✅ 7️⃣ Hidden Table
    # -------------------------------
    table_container = st.container()
    with table_container:
        with st.expander("Show Filtered Data Table (optional)"):
            st.dataframe(filtered_df, height=200)

    st.caption("✅ Compact, column-based one-page dashboard • IHME GBD 2021")
