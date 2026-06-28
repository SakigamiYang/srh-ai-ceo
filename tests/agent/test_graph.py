from pprint import pprint

from ai_ceo.agent.graph import run_ceo_agent


def test_single_query():
    """
    Basic test：full pipeline
    """

    query = "SAP AI strategy and product issues"

    res = run_ceo_agent(query)

    print("\n=== RESULT ===")
    pprint(res)

    # basic assertion (avoiding silent failure)
    assert "intelligence" in res
    assert "decision" in res


def test_routing_behavior():
    """
    test plan_node for correct routing
    """

    test_cases = [
        # shall go retrieve
        "SAP market competition and AI strategy",
        "What are SAP product issues from users",

        # shall go skip（theoretically）
        "What is artificial intelligence",
        "Explain machine learning basics",
    ]

    for q in test_cases:

        print("\n==============================")
        print(f"QUERY: {q}")

        res = run_ceo_agent(q)

        # if state == route
        route = res.get("route", "unknown")

        print(f"ROUTE: {route}")

        print("Documents:", len(res.get("documents", [])))
        print("Reviews:", len(res.get("reviews", [])))

        print("Intelligence keys:", list(res.get("intelligence", {}).keys()))
        print("Decision keys:", list(res.get("decision", {}).keys()))


def test_skip_path():
    """
    test skip route (can control manually)
    """

    query = "What is deep learning"

    res = run_ceo_agent(query)

    docs = res.get("documents", [])
    reviews = res.get("reviews", [])

    print("\n=== SKIP TEST ===")
    print("Documents:", docs)
    print("Reviews:", reviews)

    # if skip is correct, shall be empty
    assert isinstance(docs, list)
    assert isinstance(reviews, list)


def test_output_structure():
    """
    Ensure the stability of the final output structure
    """

    query = "SAP cloud product feedback"

    res = run_ceo_agent(query)

    assert isinstance(res.get("documents"), list)
    assert isinstance(res.get("reviews"), list)
    assert isinstance(res.get("intelligence"), dict)
    assert isinstance(res.get("decision"), dict)

    print("\n=== STRUCTURE OK ===")


if __name__ == "__main__":

    print("\n\n===== TEST 1: SINGLE =====")
    test_single_query()

    print("\n\n===== TEST 2: ROUTING =====")
    test_routing_behavior()

    print("\n\n===== TEST 3: SKIP =====")
    test_skip_path()

    print("\n\n===== TEST 4: STRUCTURE =====")
    test_output_structure()