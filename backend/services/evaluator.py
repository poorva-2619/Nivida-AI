from typing import List, Dict, Any
from services.llm_service import LLMService

class EvaluationEngine:
    @staticmethod
    def evaluate_vendor(vendor_name: str, vendor_id: int, vendor_evidence: Dict[str, Any], criteria_list: List[Any]) -> Dict[str, Any]:
        """
        Evaluates a vendor against a list of criteria based on extracted evidence.
        """
        criteria_results = []
        pass_count = 0
        fail_count = 0
        review_count = 0
        
        # Create a map of evidence for quick lookup by criteria_id
        evidence_map = {ev["criteria_id"]: ev for ev in vendor_evidence.get("extracted_values", [])}
        
        for criterion in criteria_list:
            evidence = evidence_map.get(criterion.id)
            
            result = {
                "criteria_id": criterion.id,
                "criteria_title": criterion.title,
                "verdict": "REVIEW",
                "required": f"{criterion.comparison} {criterion.threshold_value} {criterion.threshold_unit}" if criterion.threshold_value else criterion.requirement,
                "found": "Not found",
                "confidence": 0.0,
                "explanation": "No evidence found in submission.",
                "source_snippet": None,
                "fail_warning": None,
                "officer_override": None,
                "officer_notes": None
            }
            
            if not evidence:
                if criterion.mandatory:
                    result["verdict"] = "FAIL"
                    result["fail_warning"] = f"Critical document/evidence for '{criterion.title}' is missing from the submission."
                    fail_count += 1
                else:
                    result["verdict"] = "REVIEW"
                    review_count += 1
                criteria_results.append(result)
                continue

            # Evidence exists
            result["found"] = evidence.get("extracted_value", "Present")
            result["confidence"] = evidence.get("confidence", 0.0)
            result["source_snippet"] = evidence.get("source_snippet")
            
            confidence = result["confidence"]
            
            if criterion.type == "Financial" and criterion.threshold_value is not None:
                numeric_found = evidence.get("numeric_value")
                if numeric_found is None:
                    # Try to parse if LLM didn't provide it
                    result["verdict"] = "REVIEW"
                    result["explanation"] = "Could not verify numeric value from evidence."
                    review_count += 1
                else:
                    condition_met = EvaluationEngine._check_condition(numeric_found, criterion.comparison, criterion.threshold_value)
                    
                    if confidence >= 0.85:
                        if condition_met:
                            result["verdict"] = "PASS"
                            pass_count += 1
                        else:
                            result["verdict"] = "FAIL"
                            result["fail_warning"] = f"This criterion has been marked FAIL. Found {numeric_found} which does not meet requirement of {criterion.comparison} {criterion.threshold_value}. Document: {evidence.get('page_reference', 'Submission')}"
                            fail_count += 1
                    elif 0.50 <= confidence < 0.85:
                        if condition_met:
                            result["verdict"] = "PASS"
                            result["fail_warning"] = "Low confidence in extracted value. Manual verification recommended."
                            pass_count += 1
                        else:
                            result["verdict"] = "REVIEW"
                            review_count += 1
                    else: # confidence < 0.50
                        result["verdict"] = "REVIEW"
                        review_count += 1
            else:
                # Existence check or non-financial
                found_and_readable = evidence.get("found", False)
                if found_and_readable:
                    if confidence >= 0.85:
                        result["verdict"] = "PASS"
                        pass_count += 1
                    else:
                        result["verdict"] = "REVIEW"
                        review_count += 1
                else:
                    result["verdict"] = "FAIL"
                    result["fail_warning"] = f"Mandatory document '{criterion.title}' was not found or is unreadable. Document: {evidence.get('page_reference', 'Submission')}"
                    fail_count += 1

            # Generate explanation using LLM if needed (or use default)
            # In a real implementation, we might call LLMService.generate_explanation here
            # For now, we use a placeholder or the LLM's own explanation if provided
            result["explanation"] = LLMService.generate_explanation(
                {"title": criterion.title, "requirement": criterion.requirement},
                evidence,
                result["verdict"]
            )
            
            criteria_results.append(result)

        # Overall verdict rules
        overall_verdict = "ELIGIBLE"
        # Any mandatory FAIL -> NOT_ELIGIBLE
        # Wait, the spec says "Any mandatory criterion FAIL -> NOT_ELIGIBLE"
        # And "Any criterion REVIEW -> NEEDS_REVIEW"
        
        any_fail = any(r["verdict"] == "FAIL" for r in criteria_results)
        any_review = any(r["verdict"] == "REVIEW" for r in criteria_results)
        
        if any_fail:
            overall_verdict = "NOT_ELIGIBLE"
        elif any_review:
            overall_verdict = "NEEDS_REVIEW"
        else:
            overall_verdict = "ELIGIBLE"

        return {
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "overall_verdict": overall_verdict,
            "criteria_results": criteria_results,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "review_count": review_count
        }

    @staticmethod
    def _check_condition(found: float, operator: str, threshold: float) -> bool:
        if operator == "gte":
            return found >= threshold
        elif operator == "lte":
            return found <= threshold
        elif operator == "gt":
            return found > threshold
        elif operator == "lt":
            return found < threshold
        elif operator == "eq":
            return found == threshold
        return False
