"""
Prompt templates for all LLM calls in the pipeline.
Each prompt is designed to return structured JSON with confidence scores.
"""

EXTRACTION_PROMPT = """You are a precise document entity extraction system. Extract structured entities from the following document text.

DOCUMENT TEXT:
---
{document_text}
---

Extract the following entity types:
- **persons**: Full names of people mentioned
- **organizations**: Company names, institutions, agencies
- **dates**: Any dates in any format
- **amounts**: Monetary amounts with currency
- **key_terms**: Important domain-specific terms or phrases (max 10)

For each entity, also provide:
- The surrounding text snippet where it was found
- A confidence score from 0.0 to 1.0

Respond with ONLY valid JSON in this exact format:
{{
    "persons": ["name1", "name2"],
    "organizations": ["org1", "org2"],
    "dates": ["date1", "date2"],
    "amounts": ["$1,000", "€500"],
    "key_terms": ["term1", "term2"],
    "entities": [
        {{"entity_type": "person", "value": "John Doe", "confidence": 0.95, "source_snippet": "...signed by John Doe..."}},
        ...
    ],
    "extraction_confidence": 4
}}

The extraction_confidence is your self-assessment from 1 (very uncertain) to 5 (very confident).
"""

CLASSIFICATION_PROMPT = """You are a document classification system. Classify the following document into exactly one category.

DOCUMENT TEXT:
---
{document_text}
---

EXTRACTED ENTITIES:
{entities_json}

Categories:
- **contract**: Legal agreements, terms of service, NDAs, employment contracts
- **invoice**: Bills, payment requests, receipts, purchase orders
- **report**: Analysis documents, research papers, status updates, meeting minutes
- **correspondence**: Letters, emails, memos, notices

Respond with ONLY valid JSON:
{{
    "document_type": "contract|invoice|report|correspondence",
    "classification_confidence": 4,
    "reasoning": "Brief explanation of why this classification was chosen",
    "alternative_types": ["other_possible_type"]
}}

The classification_confidence is your self-assessment from 1 (very uncertain) to 5 (very confident).
"""

SUMMARIZATION_PROMPT = """You are a document summarization system. Generate a structured summary tailored to the document type.

DOCUMENT TYPE: {document_type}
DOCUMENT TEXT:
---
{document_text}
---

EXTRACTED ENTITIES:
{entities_json}

Based on the document type "{document_type}", generate an appropriate summary:

For contracts: Focus on parties involved, key obligations, terms, dates, and conditions.
For invoices: Focus on line items, totals, due dates, and payment terms.
For reports: Focus on key findings, methodology, conclusions, and recommendations.
For correspondence: Focus on sender/recipient intent, key requests, action items, and deadlines.

Respond with ONLY valid JSON:
{{
    "summary": "A comprehensive 2-4 sentence summary",
    "key_points": ["point1", "point2", "point3"],
    "action_items": ["action1", "action2"],
    "summarization_confidence": 4
}}

The summarization_confidence is your self-assessment from 1 (very uncertain) to 5 (very confident).
"""

JUDGE_PROMPT = """You are a quality assessment judge for an AI pipeline. Evaluate whether a pipeline step produced a reasonable output given its input.

STEP NAME: {step_name}
STEP INPUT:
---
{step_input}
---

STEP OUTPUT:
---
{step_output}
---

ORIGINAL DOCUMENT:
---
{original_document}
---

Evaluate the quality of this transformation. Consider:
1. Is the output factually consistent with the input?
2. Are there any hallucinated entities or facts not present in the source?
3. Is important information lost or distorted?
4. Does the output format match expectations for this step?

Respond with ONLY valid JSON:
{{
    "quality_score": 0.85,
    "is_problematic": false,
    "failure_type": "none|extraction_hallucination|misclassification|propagation_error|prompt_failure|context_loss",
    "explanation": "Brief explanation of the quality assessment",
    "evidence": "Specific text showing the issue, if any"
}}

quality_score ranges from 0.0 (completely wrong) to 1.0 (perfect).
"""
