# backend/agents/extraction.py
import io
import re
import json
import hashlib
from datetime import datetime
from pypdf import PdfReader
from ..utils.ollama_client import ask_llama

class ExtractionAgent:
    def __init__(self):
        print("Hybrid Extraction Agent ready (rules + Ollama)")

    def extract(self, file_bytes: bytes, content_type: str, filename: str) -> dict:
        text = self._file_to_text(file_bytes, content_type)
        
        # First, try to extract JSON directly
        json_data = self._try_extract_json(text)
        if json_data:
            json_data["extraction_method"] = "json_parse"
            return json_data
        
        # If no JSON, use rules
        data = self._extract_with_rules(text)

        # Use LLM only if key fields missing
        if not data.get("patient_name") or not data.get("claim_amount"):
            messages = [
                {"role": "system", "content": "You are an expert medical claims extractor. Return ONLY valid JSON with these fields: patient_name, member_id, claim_amount, service_date, diagnosis_codes, procedure_codes, provider_name, claim_id."},
                {"role": "user", "content": f"""Extract claim information from this text. Return valid JSON.

Text:
{text[:7000]}"""}
            ]
            llm_out = ask_llama(messages)
            llm_data = self._try_extract_json(llm_out)
            if llm_data:
                data.update(llm_data)
                data["extraction_method"] = "hybrid_llm"

        data["extraction_method"] = "hybrid_rules"
        return data

    def _try_extract_json(self, text):
        """Try to extract and parse JSON from text"""
        try:
            # Try to parse the whole text as JSON
            data = json.loads(text.strip())
            if isinstance(data, dict):
                return self._clean_json_data(data)
        except json.JSONDecodeError:
            # Try to find JSON within the text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if isinstance(data, dict):
                        return self._clean_json_data(data)
                except:
                    return None
        return None

    def _clean_json_data(self, data):
        """Clean and standardize JSON data"""
        # Ensure claim_id is always present
        claim_id = str(data.get("claim_id", "")).strip()
        if not claim_id:
            # Try alternative field names
            alternatives = ["claimid", "claim_number", "reference", "claim_no", "id", "claim", "reference_number"]
            for alt in alternatives:
                if alt in data:
                    claim_id = str(data[alt]).strip()
                    if claim_id:
                        break
        
        # Generate a claim ID if none found
        if not claim_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            data_str = f"{data.get('patient_name','')}{data.get('member_id','')}{data.get('service_date','')}"
            if data_str:
                hash_part = hashlib.md5(data_str.encode()).hexdigest()[:6].upper()
                claim_id = f"AUTO-{timestamp}-{hash_part}"
            else:
                claim_id = f"AUTO-{timestamp}"
        
        # Ensure other fields have defaults
        return {
            "claim_id": claim_id,
            "patient_name": data.get("patient_name", ""),
            "member_id": data.get("member_id", ""),
            "claim_amount": float(data.get("claim_amount", 0.0)),
            "service_date": data.get("service_date", ""),
            "diagnosis_codes": list(data.get("diagnosis_codes", [])),
            "procedure_codes": list(data.get("procedure_codes", [])),
            "provider_name": data.get("provider_name", ""),
            "plan_type": data.get("plan_type", "STANDARD"),
            "raw_text_preview": str(data)[:500] if len(str(data)) > 500 else str(data),
            "extraction_timestamp": datetime.now().isoformat()
        }

    def _file_to_text(self, file_bytes, content_type):
        if "json" in content_type:
            return file_bytes.decode("utf-8", errors="ignore")
        if "pdf" in content_type:
            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        return file_bytes.decode("utf-8", errors="ignore")

    def _extract_with_rules(self, text):
        return {
            "claim_id": self._find(text, ["claim id", "claim #", "claimid", "claim no", "reference", "id:"]),
            "patient_name": self._find(text, ["patient:", "name:", "patient name", "patient_name", "patient"]),
            "member_id": self._find(text, ["member id", "member #", "memberid", "member_id", "member"]),
            "claim_amount": self._find_amount(text),
            "service_date": self._find(text, ["service date", "dos:", "date of service", "service_date", "date"]),
            "diagnosis_codes": re.findall(r'[A-Z]\d{2,3}\.?\d*', text),
            "procedure_codes": re.findall(r'\b\d{5}\b', text),
            "provider_name": self._find(text, ["provider", "physician", "doctor", "provider_name", "attending"]),
            "plan_type": self._find(text, ["plan type", "plan_type", "plan", "coverage type"]),
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