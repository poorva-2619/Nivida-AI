import os
import json
import anthropic

class LLMService:
    @staticmethod
    def _get_client():
        return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    @staticmethod
    def _clean_json_response(text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    @staticmethod
    def extract_tender_criteria(tender_text: str) -> dict:
        client = LLMService._get_client()
        system_prompt = "You are a senior government procurement expert in India. Extract eligibility criteria from tender documents with absolute precision. Return only valid JSON. No markdown. No explanation outside JSON."
        
        prompt = f"""
Extract the eligibility criteria from the following tender document. 
Return the output EXACTLY matching this JSON structure:
{{
  "tender_summary": "2-line plain English summary of what this tender is procuring",
  "criteria": [
    {{
      "id": "C1",
      "title": "Minimum Annual Turnover",
      "type": "Financial",
      "mandatory": true,
      "requirement": "Annual turnover must be at least Rs 5 Crore",
      "threshold_value": 5,
      "threshold_unit": "Crore INR",
      "comparison": "gte",
      "document_required": "Audited Balance Sheet or CA Certificate",
      "raw_text": "exact quote from tender"
    }}
  ],
  "total_mandatory": 4,
  "total_optional": 1
}}

Tender Document:
{tender_text}
"""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return LLMService._clean_json_response(response.content[0].text)

    @staticmethod
    def extract_vendor_evidence(vendor_text: str, criteria_list: list) -> dict:
        client = LLMService._get_client()
        system_prompt = "You are an expert auditor evaluating vendor submissions against tender criteria. Extract precise values and evidence. Return only valid JSON. No markdown. No explanation outside JSON."
        
        criteria_json = json.dumps(criteria_list, indent=2)
        prompt = f"""
Evaluate the following vendor document against the provided tender criteria.
Handle language variations automatically (e.g., 'Annual Revenue', 'Yearly Turnover', 'Total Revenue', 'वार्षिक कारोबार' map to turnover criterion). Convert numbers written as words to numeric values (e.g., 'Seven Crore Twenty Lakhs' to 7.2).

Tender Criteria:
{criteria_json}

Vendor Document:
{vendor_text}

Return the output EXACTLY matching this JSON structure:
{{
  "vendor_name": "Name of the vendor",
  "extracted_values": [
    {{
      "criteria_id": "C1",
      "found": true,
      "extracted_value": "7.2 Crore",
      "numeric_value": 7.2,
      "unit": "Crore INR",
      "source_snippet": "exact quote from vendor document",
      "page_reference": "Page 3, Balance Sheet FY 2023-24",
      "confidence": 0.91
    }}
  ]
}}
"""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return LLMService._clean_json_response(response.content[0].text)

    @staticmethod
    def generate_explanation(criterion: dict, evidence: dict, verdict: str) -> str:
        client = LLMService._get_client()
        prompt = f"""
Generate a brief explanation (under 80 words) for a tender evaluation verdict.
- If Pass: cite criterion, value found, where found, confirm it meets requirement
- If Fail: cite criterion, value found, what was required, state shortfall clearly
- If Review: cite criterion, explain what was unclear and why confidence was insufficient

Criterion:
{json.dumps(criterion)}

Evidence found:
{json.dumps(evidence)}

Verdict: {verdict}
"""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()

    @staticmethod
    def generate_summary_document(tender_text: str, criteria_list: list) -> dict:
        client = LLMService._get_client()
        system_prompt = "You are an expert at summarizing complex procurement documents for vendors. Return only valid JSON. No markdown. No explanation outside JSON."
        
        criteria_json = json.dumps(criteria_list, indent=2)
        prompt = f"""
Generate a summary document for vendors so they know exactly what to prepare for this tender.

Tender Document:
{tender_text}

Extracted Criteria:
{criteria_json}

Return the output EXACTLY matching this JSON structure:
{{
  "title": "Tender Requirements Summary",
  "sections": [
    {{ "heading": "What This Tender Is For", "content": "..." }},
    {{ "heading": "Mandatory Requirements", "items": ["..."] }},
    {{ "heading": "Optional Requirements", "items": ["..."] }},
    {{ "heading": "Documents You Must Submit", "items": ["..."] }}
  ]
}}
"""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return LLMService._clean_json_response(response.content[0].text)
