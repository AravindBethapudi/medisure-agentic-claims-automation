import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from pypdf import PdfReader


class ExtractionAgent:
    """
    Agent responsible for extracting structured data from claim files.
    Supports JSON, XML, and PDF formats.
    """
    
    def __init__(self):
        print("🔧 Initializing Extraction Agent...")
        print("✅ Extraction Agent ready")
    
    def parse_claim(self, file_bytes: bytes, content_type: str) -> Dict[str, Any]:
        """
        Parse claim file based on content type.
        """
        if "json" in content_type.lower():
            return self._parse_json(file_bytes)
        elif "xml" in content_type.lower():
            return self._parse_xml(file_bytes)
        elif "pdf" in content_type.lower():
            return self._parse_pdf(file_bytes)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def _parse_json(self, file_bytes: bytes) -> Dict[str, Any]:
        """Parse JSON claim file."""
        try:
            data = json.loads(file_bytes.decode("utf-8"))
            return self._normalize_claim(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def _parse_xml(self, file_bytes: bytes) -> Dict[str, Any]:
        """Parse XML claim file."""
        try:
            root = ET.fromstring(file_bytes.decode("utf-8"))
            data = self._xml_to_dict(root)
            return self._normalize_claim(data)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result
    
    def _parse_pdf(self, file_bytes: bytes) -> Dict[str, Any]:
        """Parse PDF claim file using pypdf."""
        import io
        
        try:
            text = ""
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Extract structured data from text
            return self._extract_from_text(text)
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract claim data from raw text."""
        # Basic extraction - can be enhanced with regex or NLP
        data = {
            "claim_id": self._find_pattern(text, ["claim id", "claim_id", "claim #"]),
            "member_id": self._find_pattern(text, ["member id", "member_id", "member #"]),
            "patient_name": self._find_pattern(text, ["patient name", "patient"]),
            "diagnosis_codes": self._find_codes(text, "icd"),
            "procedure_codes": self._find_codes(text, "cpt"),
            "claim_amount": self._find_amount(text),
            "service_date": self._find_pattern(text, ["service date", "date of service"]),
            "provider_name": self._find_pattern(text, ["provider", "physician"]),
            "raw_text": text[:500]  # First 500 chars for reference
        }
        return self._normalize_claim(data)
    
    def _find_pattern(self, text: str, keywords: List[str]) -> str:
        """Find value after keyword in text."""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                # Get text after keyword (next 50 chars)
                snippet = text[idx:idx+100]
                # Try to extract value after colon or space
                if ":" in snippet:
                    value = snippet.split(":")[1].strip().split("\n")[0].strip()
                    return value[:50]  # Limit length
        return ""
    
    def _find_codes(self, text: str, code_type: str) -> List[str]:
        """Find medical codes in text."""
        import re
        codes = []
        if code_type == "icd":
            # ICD-10 pattern: letter followed by digits, optional decimal
            pattern = r'[A-Z]\d{2}\.?\d*'
        else:  # CPT
            # CPT pattern: 5 digits
            pattern = r'\b\d{5}\b'
        
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]  # Unique, max 10
    
    def _find_amount(self, text: str) -> float:
        """Find dollar amount in text."""
        import re
        # Pattern: $ followed by digits with optional decimal
        pattern = r'\$[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        if matches:
            # Get the largest amount (likely the claim total)
            amounts = []
            for m in matches:
                try:
                    amount = float(m.replace("$", "").replace(",", ""))
                    amounts.append(amount)
                except:
                    pass
            return max(amounts) if amounts else 0.0
        return 0.0
    
    def _normalize_claim(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize claim data to standard schema."""
        return {
            "claim_id": data.get("claim_id", data.get("claimId", "UNKNOWN")),
            "member_id": data.get("member_id", data.get("memberId", "")),
            "patient_name": data.get("patient_name", data.get("patientName", "")),
            "diagnosis_codes": data.get("diagnosis_codes", data.get("diagnosisCodes", [])),
            "procedure_codes": data.get("procedure_codes", data.get("procedureCodes", [])),
            "claim_amount": float(data.get("claim_amount", data.get("claimAmount", 0))),
            "service_date": data.get("service_date", data.get("serviceDate", "")),
            "provider_name": data.get("provider_name", data.get("providerName", "")),
            "plan_type": data.get("plan_type", data.get("planType", "STANDARD")),
        }