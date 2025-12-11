# backend/utils/medical_codes.py
"""
Medical Code Lookup Service for ICD-10 and CPT codes
"""

# Common ICD-10 codes with descriptions
ICD10_DATABASE = {
    # Respiratory
    "J45.909": "Unspecified asthma, uncomplicated",
    "J45.901": "Unspecified asthma, with status asthmaticus",
    "J44.9": "Chronic obstructive pulmonary disease, unspecified",
    "J06.9": "Acute upper respiratory infection, unspecified",
    
    # Endocrine/Metabolic
    "Z79.899": "Other long term (current) drug therapy",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "E78.5": "Hyperlipidemia, unspecified",
    
    # Musculoskeletal
    "M54.5": "Low back pain",
    "M25.561": "Pain in right knee",
    "M25.562": "Pain in left knee",
    
    # Circulatory
    "I10": "Essential (primary) hypertension",
    "I25.10": "Atherosclerotic heart disease of native coronary artery without angina pectoris",
    
    # Mental/Behavioral
    "F41.9": "Anxiety disorder, unspecified",
    "F32.9": "Major depressive disorder, single episode, unspecified",
    
    # General/Preventive
    "Z00.00": "Encounter for general adult medical examination without abnormal findings",
    "Z00.01": "Encounter for general adult medical examination with abnormal findings",
    "Z23": "Encounter for immunization",
    
    # Symptoms
    "R05": "Cough",
    "R07.9": "Chest pain, unspecified",
    "R51": "Headache",
    
    # Injuries
    "S06.0X0A": "Concussion without loss of consciousness, initial encounter",
    "S63.401A": "Sprain of unspecified site of right wrist, initial encounter",
}

# Common CPT codes with descriptions
CPT_DATABASE = {
    # Evaluation and Management
    "99213": "Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.",
    "99214": "Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.",
    "99215": "Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.",
    "99203": "Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.",
    
    # Procedures
    "94640": "Inhalation treatment for acute airway obstruction with administration of an aerosolized medication",
    "94010": "Spirometry, including graphic record, total and timed vital capacity, expiratory flow rate measurement(s), with or without maximal voluntary ventilation",
    "94060": "Bronchodilation responsiveness, spirometry as in 94010, pre- and post-bronchodilator administration",
    
    # Laboratory
    "80050": "General health panel (includes comprehensive metabolic panel and complete blood count)",
    "85025": "Blood count; complete (CBC), automated and automated differential WBC count",
    "81000": "Urinalysis, by dip stick or tablet reagent for bilirubin, glucose, hemoglobin, ketones, leukocytes, nitrite, pH, protein, specific gravity, urobilinogen, any number of these constituents; non-automated, with microscopy",
    "81001": "Urinalysis, by dip stick or tablet reagent for bilirubin, glucose, hemoglobin, ketones, leukocytes, nitrite, pH, protein, specific gravity, urobilinogen, any number of these constituents; automated, with microscopy",
    
    # Radiology
    "71045": "Radiologic examination, chest; single view",
    "71046": "Radiologic examination, chest; 2 views",
    "72040": "Radiologic examination, spine, cervical; 2 or 3 views",
    
    # Injections
    "96372": "Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); subcutaneous or intramuscular",
    "96374": "Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); intravenous push, single or initial substance/drug",
    
    # Physical Therapy
    "97110": "Therapeutic procedure, 1 or more areas, each 15 minutes; therapeutic exercises to develop strength and endurance, range of motion and flexibility",
    "97140": "Manual therapy techniques (eg, mobilization/manipulation, manual lymphatic drainage, manual traction), 1 or more regions, each 15 minutes",
    
    # Surgery
    "12001": "Simple repair of superficial wounds of scalp, neck, axillae, external genitalia, trunk and/or extremities (including hands and feet); 2.5 cm or less",
    "12002": "Simple repair of superficial wounds of scalp, neck, axillae, external genitalia, trunk and/or extremities (including hands and feet); 2.6 cm to 7.5 cm",
    
    # Invalid/Test codes
    "99999": "Unlisted procedure or service",
    "00000": "Invalid procedure code",
}

def get_icd10_description(code):
    """Get description for an ICD-10 code"""
    # Clean the code (remove trailing .0, etc.)
    clean_code = code.strip().upper()
    
    # Try exact match first
    if clean_code in ICD10_DATABASE:
        return ICD10_DATABASE[clean_code]
    
    # Try without decimal if present
    if '.' in clean_code:
        base_code = clean_code.split('.')[0]
        if base_code in ICD10_DATABASE:
            return ICD10_DATABASE[base_code]
    
    # Try to find partial matches (category level)
    for stored_code, description in ICD10_DATABASE.items():
        if stored_code.startswith(clean_code.split('.')[0]):
            return f"{description} (category match)"
    
    return "ICD-10 code description not available"

def get_cpt_description(code):
    """Get description for a CPT code"""
    clean_code = code.strip()
    
    # Try exact match
    if clean_code in CPT_DATABASE:
        return CPT_DATABASE[clean_code]
    
    # Try 5-digit format
    if len(clean_code) == 5 and clean_code.isdigit():
        # Check if it's a valid CPT range
        code_num = int(clean_code)
        
        # Evaluation and Management (99201-99499)
        if 99201 <= code_num <= 99499:
            return "Evaluation and Management service"
        
        # Anesthesia (00100-01999)
        elif 100 <= code_num <= 1999:
            return "Anesthesia service"
        
        # Surgery (10021-69990)
        elif 10021 <= code_num <= 69990:
            return "Surgical procedure"
        
        # Radiology (70010-79999)
        elif 70010 <= code_num <= 79999:
            return "Radiology service"
        
        # Pathology/Lab (80047-89398)
        elif 80047 <= code_num <= 89398:
            return "Pathology/Laboratory service"
        
        # Medicine (90281-99607)
        elif 90281 <= code_num <= 99607:
            return "Medicine service"
    
    return "CPT code description not available"

def get_code_description(code, is_procedure=False):
    """Get description for any medical code"""
    if not code:
        return "No code provided"
    
    clean_code = str(code).strip()
    
    # Determine code type
    if is_procedure:
        return get_cpt_description(clean_code)
    else:
        # Check if it looks like ICD-10 (starts with letter)
        if clean_code and clean_code[0].isalpha():
            return get_icd10_description(clean_code)
        # Check if it looks like CPT (5 digits)
        elif len(clean_code) == 5 and clean_code.isdigit():
            return get_cpt_description(clean_code)
        else:
            return f"Unknown code format: {clean_code}"

def get_code_category(code, is_procedure=False):
    """Get category for a medical code"""
    description = get_code_description(code, is_procedure)
    
    if "asthma" in description.lower():
        return "Respiratory"
    elif "diabetes" in description.lower():
        return "Endocrine/Metabolic"
    elif "hypertension" in description.lower() or "heart" in description.lower():
        return "Cardiovascular"
    elif "pain" in description.lower() or "musculoskeletal" in description.lower():
        return "Musculoskeletal"
    elif "depress" in description.lower() or "anxiety" in description.lower():
        return "Mental Health"
    elif "examination" in description.lower() or "visit" in description.lower():
        return "Evaluation & Management"
    elif "inhalation" in description.lower() or "spirometry" in description.lower():
        return "Pulmonary"
    elif "injection" in description.lower():
        return "Medication Administration"
    elif "radiology" in description.lower() or "x-ray" in description.lower():
        return "Imaging"
    elif "laboratory" in description.lower() or "blood" in description.lower() or "urinalysis" in description.lower():
        return "Laboratory"
    else:
        return "General"