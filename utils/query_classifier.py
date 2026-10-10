def is_definition_query(query: str) -> bool:
    keywords = [
        "what is",
        "meaning of",
        "define",
        "definition of",
        "what does"
    ]

    query_lower = query.lower()
    print('query classifier worked')
    return any(k in query_lower for k in keywords)