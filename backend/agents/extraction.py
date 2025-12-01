import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import fitz  # PyMuPDF for PDF extraction

class ExtractionAgent:
    """
    Extracts data from JSON, XML, or PDF claim files and normalizes
    into a unified claim schema.
    """

    def parse_claim(self, file_bytes: bytes, content_type: str) -> Dict[str, Any]:
        if content_type == "application/json":
            return self._parse_json(file_bytes)

        elif content_type in ["application/xml", "text/xml"]:
            return self._parse_xml(file_bytes)

        elif content_type == "application/pdf":
            return self._parse_pdf(file_bytes)

        else:
            raise ValueError(f"Unsupported file type: {content_type}")

    # ---------------- JSON Parser ----------------
    def _parse_json(self, file_bytes: bytes) -> Dict[str, Any]:
        data = json.loads(file_bytes.decode("utf-8"))
        return self._normalize(data, raw_text=json.dumps(data))

    # ---------------- XML Parser ----------------
    def _parse_xml(self, file_bytes: bytes) -> Dict[str, Any]:
        root = ET.fromstring(file_bytes.decode("utf-8"))
        
        extracted = {
            "patient": {
                "name": root.findtext("patient/name"),
                "member_id": root.findtext("patient/member_id")
            },
            "provider": {
                "name": root.findtext("provider/name"),
                "npi": root.findtext("provider/npi")
            },
            "diagnosis_codes": [d.text for d in root.findall("diagnosis/code")],
            "procedure_codes": [p.text for p in root.findall("procedures/code")],
            "total_amount": float(root.findtext("total_amount")),
            "date_of_service": root.findtext("date_of_service"),
        }

        return self._normalize(extracted, raw_text=ET.tostring(root, encoding="unicode"))

    # ---------------- PDF Parser ----------------
    def _parse_pdf(self, file_bytes: bytes) -> Dict[str, Any]:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()

        # Simplified PDF extraction (improved later)
        extracted = {
            "patient": {"name": None, "member_id": None},
            "provider": {"name": None, "npi": None},
            "diagnosis_codes": [],
            "procedure_codes": [],
            "total_amount": None,
            "date_of_service": None,
        }

        return self._normalize(extracted, raw_text=text)

    # ---------------- Normalization ----------------
    def _normalize(self, data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        Handles multiple JSON formats and normalizes to a consistent schema.
        """
        # Handle your actual claim format (flat structure)
        if "patient_name" in data:
            return {
                "claim_id": data.get("claim_id"),
                "patient": {
                    "name": data.get("patient_name"),
                    "member_id": data.get("member_id")
                },
                "provider": {
                    "name": data.get("provider_name"),
                    "npi": data.get("provider_npi"),
                    "id": data.get("provider_id")
                },
                "diagnosis_codes": data.get("diagnosis_codes", []),
                "procedure_codes": self._extract_procedure_codes(data.get("procedures", [])),
                "total_amount": data.get("total_amount"),
                "date_of_service": data.get("service_date") or data.get("date_of_service"),
                "raw_text": raw_text,
            }
        
        # Handle nested format (standard format)
        else:
            return {
                "claim_id": data.get("claim_id"),
                "patient": data.get("patient", {}),
                "provider": data.get("provider", {}),
                "diagnosis_codes": data.get("diagnosis_codes", []),
                "procedure_codes": data.get("procedure_codes", []),
                "total_amount": data.get("total_amount"),
                "date_of_service": data.get("date_of_service"),
                "raw_text": raw_text,
            }

    def _extract_procedure_codes(self, procedures: List) -> List[str]:
        """
        Extract CPT codes from procedures array.
        Handles: [{"cpt_code": "99213"}] or just ["99213"]
        """
        if not procedures:
            return []
        
        codes = []
        for proc in procedures:
            if isinstance(proc, dict):
                codes.append(proc.get("cpt_code"))
            else:
                codes.append(proc)
        
        return [c for c in codes if c]  # Remove None values