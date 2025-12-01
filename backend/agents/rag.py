from typing import List, Dict, Any
import os
from pathlib import Path


class RAGAgent:
    """
    Simplified RAG using keyword matching (no vector DB needed).
    Loads policies from backend/data/sample_policies reliably.
    """

    def __init__(self, policy_dir: str | None = None):
        print("🔧 Initializing RAG Agent...")

        # ------------------------------------------------------------
        # Resolve backend/data/sample_policies folder safely
        # ------------------------------------------------------------
        backend_dir = Path(__file__).resolve().parents[1]   # .../backend
        data_dir = backend_dir / "data" / "sample_policies"

        if policy_dir is None:
            self.policy_dir = data_dir
        else:
            self.policy_dir = Path(policy_dir)

        self.policies = {}

        if self.policy_dir.exists():
            self._load_policies()
        else:
            print(f"❌ Policy directory not found: {self.policy_dir}")

    def _load_policies(self):
        """Load all .txt policy files."""
        print(f"📁 Loading policies from {self.policy_dir}...")

        for filename in os.listdir(self.policy_dir):
            if filename.endswith(".txt"):
                filepath = self.policy_dir / filename
                with open(filepath, "r", encoding="utf-8") as f:
                    self.policies[filename] = f.read()

        print(f"✅ Loaded {len(self.policies)} policy documents")

    def retrieve_policies(self, claim_data: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve related policies using simple keyword scoring."""

        if not self.policies:
            return [{
                "content": "No policies available",
                "source": "system",
                "relevance_score": 0.0
            }]

        keywords = self._extract_keywords(claim_data)

        scored = []
        for filename, content in self.policies.items():
            score = self._calculate_relevance(content, keywords)
            scored.append({
                "content": content[:800],      # excerpt (avoid huge payloads)
                "source": filename,
                "relevance_score": score
            })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)

        return scored[:top_k]

    def _extract_keywords(self, claim_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from claim fields."""

        keywords = []

        if claim_data.get("diagnosis_codes"):
            keywords.extend(claim_data["diagnosis_codes"])

        if claim_data.get("procedure_codes"):
            keywords.extend(claim_data["procedure_codes"])

        patient = claim_data.get("patient", {})
        if patient.get("member_id"):
            keywords.append(patient["member_id"])

        return keywords

    def _calculate_relevance(self, content: str, keywords: List[str]) -> float:
        """Simple keyword match scoring."""
        if not keywords:
            return 0.0

        text = content.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text)

        return matches / len(keywords)


# Manual test
if __name__ == "__main__":
    print("\n🚀 Testing RAG Agent...\n")

    agent = RAGAgent()

    test_claim = {
        "diagnosis_codes": ["J10.1"],
        "procedure_codes": ["99213", "80050"],
        "patient": {"member_id": "M12345678"}
    }

    results = agent.retrieve_policies(test_claim)

    for r in results:
        print(f"{r['source']} — Score: {r['relevance_score']}")
