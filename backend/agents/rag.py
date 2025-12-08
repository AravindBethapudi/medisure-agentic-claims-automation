# backend/agents/rag.py
from pathlib import Path

class RAGAgent:
    def __init__(self):
        print("RAG Agent ready (keyword-based)")
        path = Path(__file__).parent.parent / "data" / "sample_policies"
        self.policies = {}
        for f in path.glob("*.txt"):
            self.policies[f.name] = f.read_text(encoding="utf-8")

    def retrieve(self, claim_data: dict, top_k=3):
        keywords = claim_data.get("diagnosis_codes", []) + claim_data.get("procedure_codes", [])
        results = []
        for name, content in self.policies.items():
            score = sum(1 for kw in keywords if kw.lower() in content.lower())
            if score > 0:
                results.append({"source": name, "score": score, "content": content[:800]})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]