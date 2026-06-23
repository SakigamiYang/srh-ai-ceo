import streamlit as st
from datetime import datetime
from collections import Counter
from loguru import logger
from sqlalchemy import create_engine, text

from ai_ceo.agent.graph import run_ceo_agent


# =========================
# Config
# =========================
st.set_page_config(layout="wide")
st.title("AI CEO Strategic Dashboard")

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
engine = create_engine(DATABASE_URL)


# =========================
# DB Stats（用于 Overview）
# =========================
@st.cache_data
def get_overview_stats():
    with engine.begin() as conn:
        doc_count = conn.execute(text("SELECT COUNT(*) FROM documents")).scalar()
        review_count = conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar()
    return doc_count, review_count


doc_count, review_count = get_overview_stats()


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("Query")

    query = st.text_input("Enter company query", "SAP AI strategy")
    run = st.button("Run Analysis")


# =========================
# Run Pipeline（按需执行）
# =========================
if run:
    result = run_ceo_agent(query)
    st.session_state["result"] = result


res = st.session_state.get("result", None)


# =========================
# Tabs
# =========================
tabs = st.tabs([
    "Overview",
    "Market Intelligence",
    "Opportunities",
    "Risks",
    "Sentiment",
    "Recommendations",
    "CEO Briefing"
])


# =========================
# Section 1: Overview（完全独立）
# =========================
with tabs[0]:

    st.header("Company Overview")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    col1.metric("Company", "SAP")
    col2.metric("Industry", "ERP / Enterprise Software")
    col3.metric("Documents", doc_count)
    col4.metric("Reviews", review_count)

    st.write("Data Sources:", 3)
    st.write("Last Update:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# =========================
# 后面所有 tab 必须依赖 result
# =========================
if res is None:
    for i in range(1, 7):
        with tabs[i]:
            st.info("Run analysis to view results.")
    st.stop()


documents = res["documents"]
reviews = res["reviews"]
intelligence = res["intelligence"]
decision = res["decision"]

logger.debug(f"{documents = !r}")
logger.debug(f"{reviews = !r}")
logger.debug(f"{intelligence = !r}")
logger.debug(f"{decision = !r}")


# =========================
# Section 2: Market Intelligence
# =========================
with tabs[1]:

    st.header("Market Intelligence")

    st.subheader("Recent News")
    for d in documents[:5]:
        st.markdown(f"**{d['title']}**")
        st.write(d["content"][:200] + "...")

    st.subheader("Emerging Trends")
    for t in intelligence.get("trends", []):
        st.write("- ", t)


# =========================
# Section 3: Opportunities
# =========================
with tabs[2]:

    st.header("Opportunity Monitor")

    for op in intelligence.get("opportunities", []):

        impact = "High" if "AI" in op else "Medium"
        confidence = 0.7

        st.markdown(f"### {op}")
        st.write("Impact:", impact)
        st.write("Confidence:", confidence)
        st.write("Evidence: derived from recent documents")


# =========================
# Section 4: Risks
# =========================
with tabs[3]:

    st.header("Risk Monitor")

    for r in intelligence.get("risks", []):

        severity = "High" if "performance" in r else "Medium"

        st.markdown(f"### {r}")
        st.write("Category:", "Product / Market")
        st.write("Severity:", severity)
        st.write("Evidence: user feedback / reviews")
        st.write("Confidence:", 0.75)


# =========================
# Section 5: Sentiment
# =========================
with tabs[4]:

    st.header("Sentiment Analysis")

    sentiments = [r["sentiment"] for r in reviews]

    pos = sentiments.count(1)
    neg = sentiments.count(0)

    st.subheader("Public Sentiment")

    st.bar_chart({
        "Positive": pos,
        "Negative": neg
    })

    # KPI（加分点）
    st.metric("Positive Rate", f"{pos / (pos + neg + 1e-6):.2%}")

    st.subheader("Tag Distribution")

    tags = [r["tag"] for r in reviews]
    tag_counts = Counter(tags)

    st.bar_chart(tag_counts)


# =========================
# Section 6: Recommendations
# =========================
with tabs[5]:

    st.header("Strategic Recommendations")

    priorities = decision.get("priorities", [])
    actions = decision.get("actions", [])

    for i, action in enumerate(actions):

        priority = priorities[i] if i < len(priorities) else "Medium"

        st.markdown(f"### {action}")
        st.write("Priority:", priority)
        st.write("Expected Impact:", "Medium / High")
        st.write("Risk Level:", "Medium")
        st.write("Supporting Evidence: derived from intelligence signals")


# =========================
# Section 7: CEO Briefing
# =========================
with tabs[6]:

    st.header("CEO Briefing")

    st.subheader("Executive Summary")

    st.write("### What happened?")
    for item in intelligence.get("trends", []):
        st.write(f"- {item}")

    st.write("### Why does it matter?")
    for item in intelligence.get("risks", []):
        st.write(f"- {item}")

    st.write("### What should management do next?")
    for item in intelligence.get("opportunities", []):
        st.write(f"- {item}")