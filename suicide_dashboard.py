import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# ✅ 1️⃣ Password Gate (same)
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
    st.title("📊 Suicide Mean Age of Death Dashboard (Custom Filters)")

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    # -------------------------------
    # ✅ 3️⃣ Sidebar Filters — all multi-select
    # -------------------------------
    st.sidebar.header("🎛️ Filters")

    selected_locations = st.sidebar.multiselect(
        "Select Location(s):",
        sorted(df['location_name'].unique()),
        default=["Global"]
    )

    selected_sexes = st.sidebar.multiselect(
        "Select Sex(es):",
        sorted(df['sex_name'].unique()),
        default=sorted(df['sex_name'].unique())
    )

    selected_years = st.sidebar.multiselect(
        "Select Year(s):",
        sorted(df['year_id'].unique()),
        default=sorted(df['year_id'].unique())
    )

    # -------------------------------
    # ✅ 4️⃣ Filter DataFrame
    # -------------------------------
    filtered_df = df[
        df['location_name'].isin(selected_locations) &
        df['sex_name'].isin(selected_sexes) &
        df['year_id'].isin(selected_years)
    ]

    # -------------------------------
    # ✅ 5️⃣ Show Summary Insights
    # -------------------------------
    st.subheader("📌 Key Insights for Current Filters")

    col1, col2, col3 = st.columns(3)
    col1.metric("Records", len(filtered_df))
    col2.metric("Mean Age", f"{filtered_df['val'].mean():.2f} years")
    col3.metric("Age Range", f"{filtered_df['val'].min():.2f} - {filtered_df['val'].max():.2f}")

    # -------------------------------
    # ✅ 6️⃣ Trend Chart with Confidence Intervals
    # -------------------------------
    st.subheader("📈 Mean Age Trend (with CI)")

    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x="year_id",
            y="val",
            color="sex_name",
            facet_col="location_name",
            facet_col_wrap=2,
            markers=True,
            labels={"year_id": "Year", "val": "Mean Age"},
            title="Mean Age of Death Over Years (by Sex & Location)"
        )

        # Add CI ribbon (upper & lower)
        for loc in filtered_df['location_name'].unique():
            for sex in filtered_df['sex_name'].unique():
                subset = filtered_df[
                    (filtered_df['location_name'] == loc) &
                    (filtered_df['sex_name'] == sex)
                ]
                fig.add_traces(
                    px.line(
                        subset, x="year_id", y="upper"
                    ).update_traces(line=dict(dash="dot"), name=f"{sex} Upper").data +
                    px.line(
                        subset, x="year_id", y="lower"
                    ).update_traces(line=dict(dash="dot"), name=f"{sex} Lower").data
                )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for selected filters.")

    # -------------------------------
    # ✅ 7️⃣ Show Filtered Table (optional)
    # -------------------------------
    with st.expander("🔍 Show Filtered Data Table"):
        st.dataframe(filtered_df)

    st.markdown("---")
    st.markdown("✅ Built with ❤️ using Streamlit | Data: IHME GBD 2021")
