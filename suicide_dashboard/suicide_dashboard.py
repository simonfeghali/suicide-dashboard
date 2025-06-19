import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 1️⃣ Simple Password Gate
# -------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "123456":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store it!
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Wrong password
        st.text_input("🔒 Enter password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Password incorrect")
        return False
    else:
        # Password correct
        return True

# -------------------------------
# 2️⃣ Run password check first
# -------------------------------
if check_password():
    # -------------------------------
    # 3️⃣ Now show your dashboard!
    # -------------------------------

    @st.cache_data
    def load_data():
        df = pd.read_csv("IHME_GBD_2021_SUICIDE_1990_2021_DEATHS_MEAN_AGE_Y2025M02D12_0.csv")
        return df

    df = load_data()

    st.sidebar.header("Filter Data")
    locations = df['location_name'].unique().tolist()
    sexes = df['sex_name'].unique().tolist()
    years = sorted(df['year_id'].unique().tolist())

    selected_location = st.sidebar.multiselect("Select Location(s):", locations, default=["Global"])
    selected_sex = st.sidebar.multiselect("Select Sex:", sexes, default=sexes)
    selected_years = st.sidebar.slider("Select Year Range:", min_value=min(years), max_value=max(years), value=(min(years), max(years)))

    filtered_df = df[
        (df['location_name'].isin(selected_location)) &
        (df['sex_name'].isin(selected_sex)) &
        (df['year_id'].between(selected_years[0], selected_years[1]))
    ]

    st.title("📊 Suicide Mean Age of Death Dashboard")

    with st.expander("🔍 Show Raw Data"):
        st.write(filtered_df)

    st.subheader("Mean Age of Death Over Time")
    fig_line = px.line(
        filtered_df,
        x="year_id",
        y="val",
        color="sex_name",
        line_group="location_name",
        markers=True,
        facet_col="location_name",
        facet_col_wrap=2,
        labels={"year_id": "Year", "val": "Mean Age"}
    )
    st.plotly_chart(fig_line)

    st.subheader("Distribution of Mean Age by Sex")
    fig_box = px.box(
        filtered_df,
        x="sex_name",
        y="val",
        color="sex_name",
        points="all",
        labels={"val": "Mean Age", "sex_name": "Sex"}
    )
    st.plotly_chart(fig_box)

    st.subheader("Key Statistics")
    st.write(filtered_df.groupby("sex_name")["val"].describe())

    st.markdown("---")
    st.markdown("✅ Built with ❤️ using Streamlit | Data: IHME GBD 2021")
