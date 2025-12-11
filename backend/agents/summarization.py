# backend/agents/summarization.py
from ..utils.ollama_client import ask_llama
from ..utils.medical_codes import get_code_description, get_code_category
from datetime import datetime

class SummarizationAgent:
    def summarize(self, extracted, validation, policies, fraud, final_decision):
        decision = final_decision['decision']
        reason = final_decision.get('reason', 'Standard processing')
        patient_name = extracted.get('patient_name', 'Valued Member')
        claim_amount = extracted.get('claim_amount', 0)
        claim_id = extracted.get('claim_id', 'N/A')
        member_id = extracted.get('member_id', 'N/A')
        
        # Generate professional patient letter
        letter = self._generate_letter(decision, reason, patient_name, claim_amount, claim_id, member_id, fraud)
        
        # Generate improved executive summary
        executive_summary = self._generate_executive_summary(decision, reason, patient_name, claim_amount, claim_id, validation, fraud)
        
        # Build comprehensive detailed breakdown
        detailed_breakdown = self._build_detailed_breakdown(extracted, validation, policies, fraud, final_decision)
        
        # Action items based on decision
        action_required = self._generate_action_items(final_decision, validation.get('details', {}), fraud)
        
        return {
            "patient_letter": letter,
            "executive_summary": executive_summary,
            "detailed_breakdown": detailed_breakdown,
            "action_required": action_required,
            "decision": decision,
            "reason": reason
        }

    def _generate_letter(self, decision, reason, patient_name, claim_amount, claim_id, member_id, fraud):
        """Generate professional patient letter with improved templates"""
        date = datetime.now().strftime("%B %d, %Y")

        # Generate a reference number if claim_id is missing
        if not claim_id or claim_id == 'N/A':
            # Create a temporary reference based on date and member ID
            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            claim_ref = f"TEMP-{timestamp}-{member_id[-4:]}" if member_id != 'N/A' else f"TEMP-{timestamp}"
        else:
            claim_ref = claim_id
        
        if decision == "APPROVE":
            return (
                f"MediSure Health Insurance\n"
                f"Claims Processing Department\n"
                f"{date}\n\n"
                f"Dear {patient_name},\n\n"
                f"RE: CLAIM APPROVAL NOTICE - Reference #{claim_ref}\n\n"
                f"We are pleased to inform you that your health insurance claim has been processed and APPROVED.\n\n"
                f"Claim Details:\n"
                f"• Claim Reference: {claim_ref}\n"
                f"• Member ID: {member_id}\n"
                f"• Amount Approved: ${claim_amount:,.2f}\n"
                f"• Date Processed: {date}\n\n"
                f"Next Steps:\n"
                f"1. Payment will be issued to your provider within 7-10 business days\n"
                f"2. You may receive an Explanation of Benefits (EOB) via mail\n"
                f"3. No further action is required from you\n\n"
                f"If you have any questions about this claim, please contact our Member Services department.\n\n"
                f"Sincerely,\n"
                f"The MediSure Claims Team\n"
                f"📞 1-800-MEDISURE (1-800-633-4787)\n"
                f"📧 claims@medisure.com\n"
                f"🌐 www.medisure.com/claims"
            )
        
        elif decision in ["REJECT", "DENIED"]:
            # Make reason more patient-friendly
            friendly_reason = self._make_reason_patient_friendly(reason)
            
            return (
                f"MediSure Health Insurance\n"
                f"Claims Processing Department\n"
                f"{date}\n\n"
                f"Dear {patient_name},\n\n"
                f"RE: CLAIM DECISION NOTICE - Reference #{claim_ref}\n\n"
                f"After careful review, we regret to inform you that your claim for ${claim_amount:,.2f} has been DENIED.\n\n"
                f"Claim Details:\n"
                f"• Claim Reference: {claim_ref}\n"
                f"• Member ID: {member_id}\n"
                f"• Service Date: As indicated on claim form\n"
                f"• Amount Submitted: ${claim_amount:,.2f}\n\n"
                f"Reason for Denial:\n{friendly_reason}\n\n"
                f"Your Appeal Rights:\n"
                f"You have the right to appeal this decision within 180 days of receiving this notice.\n"
                f"To file an appeal, please:\n"
                f"1. Call our Appeals Department at 1-800-MEDISURE\n"
                f"2. Visit www.medisure.com/appeals\n"
                f"3. Mail your appeal to: MediSure Appeals, PO Box 1234, Anytown, USA\n\n"
                f"If you believe this decision was made in error, or if you have additional information to submit, "
                f"please contact us immediately.\n\n"
                f"Sincerely,\n"
                f"The MediSure Claims Review Team\n"
                f"📞 Appeals Hotline: 1-800-APPEALS (1-800-277-3257)\n"
                f"📧 appeals@medisure.com\n"
                f"🌐 www.medisure.com/appeals\n"
                f"⏰ Monday-Friday, 8am-8pm EST"
            )
        
        else:  # MANUAL_REVIEW or other status
            return (
                f"MediSure Health Insurance\n"
                f"Claims Processing Department\n"
                f"{date}\n\n"
                f"Dear {patient_name},\n\n"
                f"RE: CLAIM REVIEW STATUS UPDATE - Reference #{claim_ref}\n\n"
                f"This letter is to inform you that your claim for ${claim_amount:,.2f} requires additional review.\n\n"
                f"Current Status: UNDER MANUAL REVIEW\n"
                f"Claim Reference: {claim_ref}\n"
                f"Member ID: {member_id}\n\n"
                f"What This Means:\n"
                f"A claims specialist is reviewing your claim to ensure accuracy and completeness. "
                f"This additional review is a standard part of our quality assurance process.\n\n"
                f"Next Steps:\n"
                f"1. A claims adjuster may contact you or your provider for additional information\n"
                f"2. Expected review completion: 10-14 business days\n"
                f"3. You will receive a final decision notice once the review is complete\n\n"
                f"Contact Information:\n"
                f"📞 Claims Status Line: 1-800-MEDISURE, option 2\n"
                f"📧 claims.status@medisure.com\n"
                f"🌐 Check status online: www.medisure.com/claimstatus\n"
                f"Please reference Claim #{claim_ref} in all communications.\n\n"
                f"Sincerely,\n"
                f"The MediSure Claims Processing Team"
            )
    
    def _make_reason_patient_friendly(self, technical_reason):
        """Convert technical validation reasons to patient-friendly language"""
        friendly_mapping = {
            "Member ID not found in system": "The member identification number provided could not be verified in our system. Please verify your member ID or contact Member Services.",
            "Invalid procedure code": "The procedure code submitted does not match our coverage criteria for this service.",
            "Suspicious provider name": "The provider information requires additional verification.",
            "Missing member ID": "The claim submission is missing required member identification information.",
            "Member status: TERMINATED": "Coverage was not active on the date of service.",
            "No procedure codes provided": "Required procedure information is missing from the claim submission.",
            "No diagnosis codes provided": "Required diagnosis information is missing from the claim submission.",
            "High claim amount requires review": "The claim amount exceeds automated processing thresholds and requires manual review.",
            "Invalid claim amount": "The claim amount appears to be incorrect or requires verification.",
            "Provider information missing": "Required provider information is incomplete or missing.",
            "Uncovered procedures": "The procedures billed are not covered under your current benefit plan.",
            "Procedure not medically necessary for diagnosis": "The medical necessity of the service could not be established based on the diagnosis provided."
        }
        
        # Check for partial matches
        for tech_reason, friendly_text in friendly_mapping.items():
            if tech_reason.lower() in technical_reason.lower():
                return friendly_text
        
        # Default friendly response
        return f"Based on our review, the claim does not meet coverage requirements: {technical_reason}"
    
    def _generate_executive_summary(self, decision, reason, patient_name, claim_amount, claim_id, validation, fraud):
        """Generate improved executive summary"""
        validation_details = validation.get('details', {})
        
        # Get key validation failures
        failures = []
        for check_name, check_result in validation_details.items():
            if check_result.get('status') == 'FAILED':
                failures.append(check_name.replace('_', ' ').title())
        
        # Get fraud risk
        fraud_risk = fraud.get('risk_level', 'LOW')
        fraud_score = fraud.get('risk_score', 0)
        
        if decision == "APPROVE":
            if fraud_risk == "HIGH":
                return f"✅ CLAIM {claim_id} — APPROVED with High Fraud Monitoring — ${claim_amount:,.2f} for {patient_name}\n" \
                       f"   • Payment authorized with enhanced scrutiny\n" \
                       f"   • Fraud risk score: {fraud_score:.1%} (monitoring active)\n" \
                       f"   • All validation checks passed"
            else:
                return f"✅ CLAIM {claim_id} — APPROVED — ${claim_amount:,.2f} for {patient_name}\n" \
                       f"   • Standard approval process\n" \
                       f"   • Fraud risk: {fraud_risk} ({fraud_score:.1%})\n" \
                       f"   • Ready for payment processing"
        
        elif decision in ["REJECT", "DENIED"]:
            failure_list = ", ".join(failures) if failures else reason
            return f"❌ CLAIM {claim_id} — REJECTED — ${claim_amount:,.2f} for {patient_name}\n" \
                   f"   • Validation failures: {failure_list}\n" \
                   f"   • Fraud risk: {fraud_risk} ({fraud_score:.1%})\n" \
                   f"   • Claim does not meet coverage criteria"
        
        else:  # MANUAL_REVIEW
            if fraud_risk == "HIGH":
                return f"⚠️ CLAIM {claim_id} — REQUIRES MANUAL REVIEW — ${claim_amount:,.2f} for {patient_name}\n" \
                       f"   • High fraud risk detected: {fraud_score:.1%}\n" \
                       f"   • {len(failures)} validation issue(s) require specialist review\n" \
                       f"   • Escalated to claims investigation team"
            else:
                return f"⚠️ CLAIM {claim_id} — REQUIRES MANUAL REVIEW — ${claim_amount:,.2f} for {patient_name}\n" \
                       f"   • Standard review process\n" \
                       f"   • {len(failures)} validation item(s) need clarification\n" \
                       f"   • Expected resolution: 10-14 business days"
    
    def _build_detailed_breakdown(self, extracted, validation, policies, fraud, final_decision):
        """Build comprehensive breakdown with code descriptions"""
        validation_details = validation.get('details', {})
        
        # Get code descriptions using the medical_codes module
        diagnosis_codes = extracted.get('diagnosis_codes', [])
        procedure_codes = extracted.get('procedure_codes', [])
        
        diagnosis_with_descriptions = []
        for code in diagnosis_codes:
            desc = get_code_description(code, is_procedure=False)
            category = get_code_category(code, is_procedure=False)
            diagnosis_with_descriptions.append({
                "code": code,
                "description": desc,
                "category": category
            })
        
        procedure_with_descriptions = []
        for code in procedure_codes:
            desc = get_code_description(code, is_procedure=True)
            category = get_code_category(code, is_procedure=True)
            procedure_with_descriptions.append({
                "code": code,
                "description": desc,
                "category": category
            })
        
        return {
            "claim_information": {
                "claim_id": extracted.get('claim_id', 'Not provided'),
                "patient_name": extracted.get('patient_name', 'Unknown'),
                "member_id": extracted.get('member_id', 'Unknown'),
                "service_date": extracted.get('service_date', 'Unknown'),
                "provider": extracted.get('provider_name', 'Unknown'),
                "total_amount": f"${extracted.get('claim_amount', 0):,.2f}",
                "extraction_method": extracted.get('extraction_method', 'hybrid'),
                "plan_type": extracted.get('plan_type', 'STANDARD')
            },
            "clinical_information": {
                "diagnoses": diagnosis_with_descriptions,
                "procedures": procedure_with_descriptions,
                "summary": self._generate_clinical_summary(diagnosis_with_descriptions, procedure_with_descriptions)
            },
            "validation_results": {
                "eligibility": {
                    "status": validation_details.get('eligibility', {}).get('status', 'UNKNOWN'),
                    "reason": validation_details.get('eligibility', {}).get('reason', 'N/A'),
                    "icon": "✅" if validation_details.get('eligibility', {}).get('status') == 'PASSED' else "❌"
                },
                "coverage": {
                    "status": validation_details.get('coverage', {}).get('status', 'UNKNOWN'),
                    "reason": validation_details.get('coverage', {}).get('reason', 'N/A'),
                    "icon": "✅" if validation_details.get('coverage', {}).get('status') == 'PASSED' else "❌"
                },
                "authorization": {
                    "status": validation_details.get('authorization', {}).get('status', 'UNKNOWN'),
                    "reason": validation_details.get('authorization', {}).get('reason', 'N/A'),
                    "icon": "✅" if validation_details.get('authorization', {}).get('status') == 'PASSED' else "⚠️"
                },
                "business_rules": {
                    "status": validation_details.get('business_rules', {}).get('status', 'UNKNOWN'),
                    "reason": validation_details.get('business_rules', {}).get('reason', 'N/A'),
                    "icon": "✅" if validation_details.get('business_rules', {}).get('status') == 'PASSED' else "❌"
                }
            },
            "fraud_analysis": {
                "risk_level": fraud.get('risk_level', 'LOW'),
                "risk_score": f"{fraud.get('risk_score', 0):.1%}",
                "recommendation": fraud.get('recommendation', 'APPROVE'),
                "flags": fraud.get('red_flags', []),
                "icon": "🟢" if fraud.get('risk_level') == 'LOW' else "🟡" if fraud.get('risk_level') == 'MEDIUM' else "🔴"
            },
            "final_decision": {
                "decision": final_decision.get('decision', 'UNKNOWN'),
                "reason": final_decision.get('reason', 'N/A'),
                "confidence": final_decision.get('confidence', None),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    def _generate_clinical_summary(self, diagnoses, procedures):
        """Generate a clinical summary based on codes"""
        if not diagnoses and not procedures:
            return "No clinical information available"
        
        summary_parts = []
        
        # Group diagnoses by category
        diag_by_category = {}
        for diag in diagnoses:
            category = diag.get('category', 'General')
            if category not in diag_by_category:
                diag_by_category[category] = []
            diag_by_category[category].append(f"{diag['code']} ({diag['description'].split(',')[0]})")
        
        # Group procedures by category
        proc_by_category = {}
        for proc in procedures:
            category = proc.get('category', 'General')
            if category not in proc_by_category:
                proc_by_category[category] = []
            proc_by_category[category].append(f"{proc['code']} ({proc['description'].split('.')[0]})")
        
        # Build summary
        if diag_by_category:
            summary_parts.append("Diagnoses:")
            for category, codes in diag_by_category.items():
                summary_parts.append(f"  • {category}: {', '.join(codes)}")
        
        if proc_by_category:
            summary_parts.append("Procedures:")
            for category, codes in proc_by_category.items():
                summary_parts.append(f"  • {category}: {', '.join(codes)}")
        
        return "\n".join(summary_parts)
    
    def _get_code_descriptions(self, codes, is_procedure=False):
        """Get human-friendly descriptions for codes"""
        descriptions = []
        for code in codes:
            desc = get_code_description(code, is_procedure)
            descriptions.append(f"{code}: {desc}")
        return descriptions
    
    def _generate_action_items(self, final_decision, validation_details, fraud):
        """Generate specific action items based on decision"""
        decision = final_decision['decision']
        
        if decision == "APPROVE":
            items = [
                "✅ **Payment Processing**: Claim approved for payment",
                "💰 **Amount**: Payment of ${:,.2f} will be issued".format(final_decision.get('claim_amount', 0)),
                "⏱️ **Timeline**: Payment within 7-10 business days",
                "📋 **Next**: EOB will be mailed to your address on file"
            ]
            
            if fraud.get('risk_level') == 'HIGH':
                items.append("🔍 **Monitoring**: Claim flagged for post-payment audit")
                
            return items
        
        elif decision in ["REJECT", "DENIED"]:
            items = []
            
            # Add specific rejection reasons
            for check_name, check_result in validation_details.items():
                if check_result.get('status') == 'FAILED':
                    reason = check_result.get('reason', 'Failed validation')
                    items.append(f"❌ **{check_name.replace('_', ' ').title()}**: {reason}")
            
            if fraud.get('risk_level') == 'HIGH':
                items.append(f"🚨 **Fraud Alert**: High risk detected ({fraud.get('risk_score', 0):.1%})")
            
            # Add appeal information
            items.extend([
                "📝 **Appeal Rights**: You may appeal within 180 days",
                "📞 **Contact**: Appeals Department: 1-800-APPEALS (277-3257)",
                "📧 **Email**: appeals@medisure.com",
                "🌐 **Online Portal**: www.medisure.com/appeals",
                "📨 **Mail**: MediSure Appeals, PO Box 1234, Anytown, USA"
            ])
            
            return items
        
        else:  # MANUAL_REVIEW
            items = [
                "⚠️ **Status**: Claim requires manual review",
                "⏱️ **Timeline**: 10-14 business days for resolution",
                "👨‍💼 **Assignee**: Senior claims adjuster",
                "📞 **Contact**: Claims Status Line: 1-800-MEDISURE, option 2",
                "🌐 **Online**: Check status at www.medisure.com/claimstatus"
            ]
            
            if fraud.get('risk_level') == 'HIGH':
                items.append("🔍 **Note**: Under investigation for potential fraud indicators")
            
            return items