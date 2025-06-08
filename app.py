import streamlit as st
import pandas as pd
from analyze_competitors import analyze_competitors

st.set_page_config(page_title="SEO Competitor Analyzer", layout="wide")
st.title("🔍 SEO Competitor Analyzer")

keyword = st.text_input("Enter your target keyword:")

if keyword:
    with st.spinner("🔍 Step 1: Finding top competitors..."):
        df = analyze_competitors(keyword)

    with st.spinner("📄 Step 2: Scraping metadata, H1s, and schema..."):
        pass  # Already included in analyze_competitors()

    with st.spinner("🔗 Step 3: Checking links and alt text ratios..."):
        pass  # Already included in analyze_competitors()

    with st.spinner("🚀 Step 4: Running PageSpeed analysis (mobile & desktop)..."):
        pass  # Already included in analyze_competitors()

    st.success("✅ All done! Here's your full competitor analysis:")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("📥 Download as CSV", data=csv, file_name="seo_analysis.csv", mime="text/csv")
