import streamlit as st
import pandas as pd
import altair as alt

st.title("FAIR Scores by RDI (samples)")

# List of datasets
datasets = [
    "e!DAL-PGP (IPK)",
    "BonaRes (ZALF)",
    "OpenAgrar (JKI)",
    "National Soil & Forest Inventories (Thünen)",
    "PUBLISSO Repository for Life Sciences (ZB MED)",
    "PhenoRob DB (UBN)",
    "PlabiPD (FZJ)",
    "Edaphobase (SGN)",
    "GBIS/I, LIMS (IPK)",
    "JKI-DataCube (JKI)",
    "SRADI (TUM)",
    "BonaRes Knowledge Library (UFZ)",
    "Open Data Server (DWD)"
]

# Let user select a dataset
dataset_name = st.selectbox("Select Dataset", datasets)

# Predefined scores
dataset_scores = {
    "e!DAL-PGP (IPK)": {
        "All Tests Average": 0.5303898,
        "Findability": 0.68421054,
        "Accessibility": 0.45,
        "Interoperability": 0.61538464,
        "Reusability": 0.37688366
    },
    "BonaRes (ZALF)": {
        "All Tests Average": 0.46385714,
        "Findability": 0.60057896,
        "Accessibility": 0.3,
        "Interoperability": 0.49046153,
        "Reusability": 0.4017143
    },
    "OpenAgrar (JKI)": {
        "All Tests Average": 0.5925926,
        "Findability": 0.6885965,
        "Accessibility": 0.5416667,
        "Interoperability": 0.63461536,
        "Reusability": 0.50396824
    },
    "National Soil & Forest Inventories (Thünen)": {
        "All Tests Average": 0.48562735,
        "Findability": 0.5853064,
        "Accessibility": 0.38675496,
        "Interoperability": 0.6972477,
        "Reusability": 0.3124216
    },
    "PUBLISSO Repository for Life Sciences (ZB MED)": {
        "All Tests Average": 0.4485367,
        "Findability": 0.60238487,
        "Accessibility": 0.5,
        "Interoperability": 0.46153846,
        "Reusability": 0.2767857
    },
}

# Default baseline for other datasets
baseline_scores = {
    "All Tests Average": 0.0,
    "Findability": 0.0,
    "Accessibility": 0.0,
    "Interoperability": 0.0,
    "Reusability": 0.0
}

# Use real scores if available, otherwise baseline
dimension_scores = dataset_scores.get(dataset_name, baseline_scores)

# Calculate FAIR Dimensions Average dynamically
fair_dimensions_average = sum(dimension_scores[d] for d in ["Findability","Accessibility","Interoperability","Reusability"]) / 4

# Combine all scores for display
scores = {
    "All Tests Average": dimension_scores["All Tests Average"],
    **dimension_scores,
    "FAIR Dimensions Average": fair_dimensions_average
}

# Convert to DataFrame
df = pd.DataFrame({
    "Dimension": list(scores.keys()),
    "Score": list(scores.values())
})

# Show table
st.subheader(f"{dataset_name} - Scores Table")
st.table(df)

# Show chart
st.subheader(f"{dataset_name} - Scores Chart")
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Dimension", sort=None),
    y=alt.Y("Score", scale=alt.Scale(domain=[0, 1])),
    color=alt.Color("Dimension", legend=None)
).properties(width=600, height=400)

st.altair_chart(chart)
