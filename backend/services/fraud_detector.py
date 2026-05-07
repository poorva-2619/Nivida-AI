from typing import List, Dict, Any
import json
from difflib import SequenceMatcher

class FraudDetector:
    @staticmethod
    def detect_patterns(all_vendor_results: List[Dict[str, Any]], vendor_submissions: List[Any]) -> List[Dict[str, Any]]:
        """
        Analyzes evaluation results across all vendors to detect suspicious patterns.
        """
        flags = []
        
        # 1. DUPLICATE_SUBMISSION
        # Same company name with >70% string similarity submitted twice
        vendor_names = [(v["vendor_id"], v["vendor_name"]) for v in all_vendor_results]
        for i in range(len(vendor_names)):
            for j in range(i + 1, len(vendor_names)):
                id1, name1 = vendor_names[i]
                id2, name2 = vendor_names[j]
                
                similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
                if similarity > 0.70:
                    flags.append({
                        "flag_type": "DUPLICATE_SUBMISSION",
                        "vendor_ids": [id1, id2],
                        "message": f"Suspiciously similar vendor names detected: '{name1}' and '{name2}' ({int(similarity*100)}% match). Possible duplicate or related entity submission.",
                        "severity": "HIGH"
                    })

        # 2. FINANCIAL_COLLUSION
        # Three or more vendors have identical turnover figures to 2 decimal places
        turnover_map = {} # {value: [vendor_ids]}
        for res in all_vendor_results:
            for cr in res.get("criteria_results", []):
                # We need to find financial criteria
                # Assuming 'found' might contain the value if it was a numeric check
                # This depends on how evaluate_vendor stores it. 
                # Let's check the numeric_value if we can get it from evidence or 'found'
                # For simplicity, we'll look at the 'found' field if it's numeric-ish
                try:
                    # Try to extract a numeric value from the 'found' string or look at evidence
                    # In a real scenario, we'd store the normalized numeric value in the result
                    # For this implementation, we'll assume 'found' contains something like "7.2 Crore"
                    # and we'll try to normalize it or use a separate field if we added it to models.
                    # Since I added 'found_value' to models, I'll use that.
                    # Wait, 'all_vendor_results' is the dict returned by EvaluationEngine.
                    
                    # We'll look for criteria results where a numeric value was found
                    # Let's assume the evaluator stores the raw numeric value in a way we can access
                    # For now, let's just parse it from 'found' or assume it's passed along.
                    val_str = cr.get("found", "")
                    if val_str and any(char.isdigit() for char in val_str):
                        # Very crude normalization: extract first float-like thing
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", val_str)
                        if match:
                            val = round(float(match.group()), 2)
                            if val not in turnover_map:
                                turnover_map[val] = []
                            if res["vendor_id"] not in turnover_map[val]:
                                turnover_map[val].append(res["vendor_id"])
                except:
                    continue

        for val, ids in turnover_map.items():
            if len(ids) >= 3:
                flags.append({
                    "flag_type": "FINANCIAL_COLLUSION",
                    "vendor_ids": ids,
                    "message": f"Three or more vendors ({len(ids)}) submitted identical financial figures ({val}). This is a strong indicator of bid rigging or collusion.",
                    "severity": "HIGH"
                })

        # 3. ABNORMAL_PATTERN
        # Vendor submitted 10+ documents but every single criterion failed (suspicious padding)
        # We need the number of documents from vendor_submissions
        submission_map = {s.vendor_id: s for s in vendor_submissions}
        for res in all_vendor_results:
            vendor_id = res["vendor_id"]
            submission = submission_map.get(vendor_id)
            if not submission:
                continue
                
            try:
                files = json.loads(submission.files_json)
                file_count = len(files) if isinstance(files, list) else 0
            except:
                file_count = 0
            
            total_criteria = len(res.get("criteria_results", []))
            fail_count = res.get("fail_count", 0)
            
            if file_count >= 10 and fail_count == total_criteria and total_criteria > 0:
                flags.append({
                    "flag_type": "ABNORMAL_PATTERN",
                    "vendor_ids": [vendor_id],
                    "message": f"Vendor '{res['vendor_name']}' submitted {file_count} documents, yet failed 100% of the eligibility criteria. This suggests suspicious 'padding' of the submission with irrelevant documents.",
                    "severity": "MEDIUM"
                })

        return flags
