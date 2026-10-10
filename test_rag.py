from app import app
from utils.rag_pipeline import rag_answer

query = "which section deals with culpable homicide ?"
sector = "laws"

with app.app_context():
    result = rag_answer(query, sector)

    print("\nANSWER:\n", result["answer"])
    print("\nSOURCES:")
    for s in result["sources"]:
        print("-", s)
