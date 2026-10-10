def build_prompt(context_chunks, query):
    context_text = ""

    for i, chunk in enumerate(context_chunks, start=1):
        context_text += f"""
SOURCE {i}:
{chunk['text']}
"""

    prompt = f"""
You are a domain-specific consultancy assistant.

RULES (STRICT):
1. BNS-AWARENESS (PRIORITY): 
   - If the SOURCES include "Bharatiya Nyaya Sanhita" (BNS) or "BNSS", you MUST use the BNS section numbers.
   - Do NOT use outdated IPC (Indian Penal Code) section numbers (e.g., Section 299, 302, 376) unless the sources specifically say they are still in force for that specific case.
   - For example: Culpable Homicide is Section 100 in BNS (previously 299 in IPC). If the sources mention BNS, use Section 100.
2. If the user asks for the MEANING or DEFINITION of a word or term present in document only :
   - You MAY explain it in simple language.
   - Prefer explanations consistent with the domain context.
3. For advisory, legal, procedural, or factual questions:
   - Answer ONLY using the information in the sources below.
4. Do NOT invent legal rules, laws, or procedures.
5. If the answer cannot be derived from sources and is not a definition:
   reply exactly:
   "Answer not found in the provided documents."

SOURCES:
{context_text}

QUESTION:
{query}

ANSWER:
"""
    return prompt
