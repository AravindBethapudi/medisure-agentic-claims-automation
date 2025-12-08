# backend/agents/extraction.py
import io
import re
from pypdf import PdfReader
from utils.ollama_client import ask_llama

class ExtractionAgent:
    def __init__(self):
        print("Hybrid Extraction Agent ready (rules + Ollama)")

    def extract(self, file_bytes: bytes, content_type: str, filename: str) -> dict:
        text = self._file_to_text(file_bytes, content_type)
        data = self._extract_with_rules(text)

        # Use LLM only if key fields missing
        if not data.get("patient_name") or not data.get("claim_amount"):
            messages = [
                {"role": "system", "content": "You are an expert medical claims extractor. Return ONLY valid JSON."},
                {"role": "user", "content": f"""Extract as JSON:
- patient_name
- member_id
- claim_amount (number)
- service_date
- diagnosis_codes (list)
- procedure_codes (list)
- provider_name

Text:
{text[:7000]}"""}
            ]
            llm_out = ask_llama(messages)
            try:
                json_match = re.search(r'\{.*\}', llm_out, re.DOTALL)
                if json_match:
                    import json
                    llm_data = json.loads(json_match.group())
                    data.update(llm_data)
            except:
                pass

        data["extraction_method"] = "hybrid"
        return data

    def _file_to_text(self, file_bytes, content_type):
        if "json" in content_type:
            return file_bytes.decode("utf-8", errors="ignore")
        if "pdf" in content_type:
            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        return file_bytes.decode("utf-8", errors="ignore")

    def _extract_with_rules(self, text):
        return {
            "claim_id": self._find(text, ["claim id", "claim #", "claimid", "claim no"]),
            "patient_name": self._find(text, ["patient:", "name:", "patient name"]),
            "member_id": self._find(text, ["member id", "member #", "memberid"]),
            "claim_amount": self._find_amount(text),
            "service_date": self._find(text, ["service date", "dos:", "date of service"]),
            "diagnosis_codes": re.findall(r'[A-Z]\d{2,3}\.?\d*', text),
            "procedure_codes": re.findall(r'\b\d{5}\b', text),
            "provider_name": self._find(text, ["provider", "physician", "doctor"]),
            "raw_text_preview": text[:500]
        }

    def _find(self, text, keywords):
        t = text.lower()
        for kw in keywords:
            if kw in t:
                start = t.find(kw) + len(kw)
                snippet = text[start:start+120]
                return re.split(r'\n|\||\$|\s{2,}', snippet)[0].strip()
        return ""

    def _find_amount(self, text):
        matches = re.findall(r'\$[\d,]+\.?\d*', text)
        if matches:
            return max(float(m.replace('$','').replace(',','')) for m in matches)
        return 0.0