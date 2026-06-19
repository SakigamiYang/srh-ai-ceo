from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph

import chromadb

from ai_ceo.retrieval.utils import encode_query

from ai_ceo.retrieval.hybrid_search import hybrid_search
from ai_ceo.retrieval.bm25_search import bm25_search

from ai_ceo.intelligence.extract_intelligence import extract_intelligence
from ai_ceo.agent.ceo_agent import ceo_decision


# ========================
# State 定义（关键）
# ========================

class CEOState(TypedDict, total=False):
    query: str
    query_embedding: List[List[float]]

    documents: List[Dict[str, Any]]
    reviews: List[Dict[str, Any]]

    intelligence: Dict[str, Any]
    decision: Dict[str, Any]


# ========================
# 全局依赖（只初始化一次）
# ========================

chroma_client = chromadb.HttpClient(host="localhost", port=8000)

document_collection = chroma_client.get_collection("documents_chunks")
review_collection = chroma_client.get_collection("reviews")


# ========================
# Node 1: Retrieval
# ========================

def retrieve_node(state: CEOState) -> CEOState:

    query = state["query"]

    query_embedding = encode_query([query])

    result = hybrid_search(
        query=query,
        query_embedding=query_embedding,
        bm25_search=bm25_search,
        document_collection=document_collection,
        review_collection=review_collection,
        top_k=5
    )

    return {
        "documents": result["documents"],
        "reviews": result["reviews"]
    }


# ========================
# Node 2: Intelligence
# ========================

def intelligence_node(state: CEOState) -> CEOState:

    intelligence = extract_intelligence(
        state["documents"],
        state["reviews"]
    )

    return {
        "intelligence": intelligence
    }


# ========================
# Node 3: Decision
# ========================

def decision_node(state: CEOState) -> CEOState:

    decision = ceo_decision(
        state["intelligence"]
    )

    return {
        "decision": decision
    }


# ========================
# Graph 构建
# ========================

def build_graph():

    graph = StateGraph(CEOState)

    # nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("intelligence", intelligence_node)
    graph.add_node("decision", decision_node)

    # flow
    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "intelligence")
    graph.add_edge("intelligence", "decision")

    graph.set_finish_point("decision")

    return graph.compile()


# ========================
# 统一入口（考试用）
# ========================

def run_ceo_agent(query: str):

    graph = build_graph()

    result = graph.invoke({
        "query": query
    })

    return result


# ========================
# CLI test
# ========================

if __name__ == "__main__":
    from pprint import pp

    res = run_ceo_agent("SAP AI strategy and product issues")
    pp(res)