"""
LLM Provider abstraction with MockProvider (default) and OpenAIProvider.
Mock provider returns realistic responses with deliberate failure injection,
so the project runs out-of-the-box without an API key.
"""

from __future__ import annotations

import json
import os
import re
import random
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.models import DocumentType


class LLMResponse:
    """Standardized response from any LLM provider."""
    def __init__(self, content: str, token_count: int, raw_response: str, prompt: str):
        self.content = content
        self.token_count = token_count
        self.raw_response = raw_response
        self.prompt = prompt

    def parse_json(self) -> dict[str, Any]:
        """Parse the response content as JSON, handling common LLM quirks."""
        text = self.content.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}")


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(self, prompt: str) -> LLMResponse:
        """Send a prompt and get a completion."""
        pass


class UniversalProvider(LLMProvider):
    """Universal LLM Provider using litellm (supports OpenAI, Anthropic, Google, etc.)."""

    def __init__(self, api_key: str, model: str):
        try:
            import litellm
        except ImportError:
            raise ImportError("litellm package required. Install with: pip install litellm")
        # Ensure litellm uses the provided key implicitly or through environment
        # litellm automatically picks up OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.
        # But we can also pass it explicitly if we want to override for a specific provider.
        # For simplicity, litellm relies on environment variables for keys.
        self.model = model
        self.api_key = api_key

    async def complete(self, prompt: str) -> LLMResponse:
        import litellm
        
        # litellm supports acompletion for async calls
        response = await litellm.acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
            api_key=self.api_key, # pass the api key to litellm directly
        )
        content = response.choices[0].message.content or ""
        token_count = (response.usage.total_tokens if response.usage else 0)
        return LLMResponse(
            content=content,
            token_count=token_count,
            raw_response=content,
            prompt=prompt,
        )


class MockProvider(LLMProvider):
    """
    Mock LLM provider that returns realistic, deterministic responses.
    Uses document content hash for consistency — same input always gives same output.
    Deliberately injects failures for certain document patterns.
    """

    def __init__(self, failure_rate: float = 0.2):
        self.failure_rate = failure_rate

    def _hash_seed(self, text: str) -> int:
        return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)

    def _should_fail(self, text: str, step: str) -> bool:
        """Deterministic failure based on content patterns."""
        seed = self._hash_seed(text + step)
        rng = random.Random(seed)
        return rng.random() < self.failure_rate

    def _detect_doc_type(self, text: str) -> str:
        """Simple heuristic to detect document type for realistic mock responses."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["agreement", "hereby", "parties", "clause", "terms and conditions", "obligations"]):
            return "contract"
        if any(kw in text_lower for kw in ["invoice", "bill", "payment", "amount due", "total", "qty", "unit price"]):
            return "invoice"
        if any(kw in text_lower for kw in ["report", "findings", "analysis", "methodology", "conclusion", "recommendation"]):
            return "report"
        if any(kw in text_lower for kw in ["dear", "regards", "sincerely", "re:", "subject:", "memo", "attention"]):
            return "correspondence"
        return "report"

    def _extract_names(self, text: str) -> list[str]:
        """Extract plausible person names using simple patterns."""
        # Look for capitalized word pairs
        patterns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
        # Filter out common non-names
        stopwords = {"The Company", "The Client", "Terms And", "This Agreement", "United States",
                      "New York", "San Francisco", "Los Angeles", "North America", "South America",
                      "Dear Sir", "Dear Madam", "Key Findings", "Action Items", "Executive Summary"}
        names = [p for p in patterns if p not in stopwords and len(p.split()) <= 3]
        return list(dict.fromkeys(names))[:5]  # Deduplicate, max 5

    def _extract_dates(self, text: str) -> list[str]:
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
        ]
        dates = []
        for pat in patterns:
            dates.extend(re.findall(pat, text))
        return list(dict.fromkeys(dates))[:5]

    def _extract_amounts(self, text: str) -> list[str]:
        patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'€[\d,]+(?:\.\d{2})?',
            r'£[\d,]+(?:\.\d{2})?',
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|INR)',
        ]
        amounts = []
        for pat in patterns:
            amounts.extend(re.findall(pat, text))
        return list(dict.fromkeys(amounts))[:5]

    def _extract_orgs(self, text: str) -> list[str]:
        patterns = re.findall(r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*)*(?:\s+(?:Inc|LLC|Corp|Ltd|Co|Group|Partners|Associates|International|Services|Solutions|Technologies|Consulting)\.?))\b', text)
        return list(dict.fromkeys(patterns))[:5]

    async def complete(self, prompt: str) -> LLMResponse:
        # Simulate latency
        time.sleep(0.05)

        # Determine which step this is for
        if "entity extraction" in prompt.lower() or "extract" in prompt.lower()[:100]:
            response = await self._mock_extraction(prompt)
        elif "classify" in prompt.lower()[:100] or "classification" in prompt.lower()[:100]:
            response = await self._mock_classification(prompt)
        elif "summar" in prompt.lower()[:100]:
            response = await self._mock_summarization(prompt)
        elif "quality assessment" in prompt.lower()[:100] or "judge" in prompt.lower()[:100]:
            response = await self._mock_judge(prompt)
        else:
            response = await self._mock_extraction(prompt)

        return response

    async def _mock_extraction(self, prompt: str) -> LLMResponse:
        # Extract the document text from the prompt
        doc_match = re.search(r'DOCUMENT TEXT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)
        doc_text = doc_match.group(1) if doc_match else prompt

        names = self._extract_names(doc_text)
        dates = self._extract_dates(doc_text)
        amounts = self._extract_amounts(doc_text)
        orgs = self._extract_orgs(doc_text)

        # Extract key terms (simple: frequent capitalized words)
        words = re.findall(r'\b[A-Z][a-z]{3,}\b', doc_text)
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        key_terms = sorted(word_freq, key=word_freq.get, reverse=True)[:6]

        confidence = 4
        entities = []

        # Inject failures
        if self._should_fail(doc_text, "extraction"):
            # Hallucinate an entity
            hallucinated_names = ["Alexander Worthington", "Dr. Evelyn Chambers", "Marcus Sterling III"]
            seed = self._hash_seed(doc_text)
            rng = random.Random(seed)
            fake_name = rng.choice(hallucinated_names)
            names.append(fake_name)
            entities.append({
                "entity_type": "person",
                "value": fake_name,
                "confidence": 0.6,
                "source_snippet": f"...referenced by {fake_name} in the document..."
            })
            confidence = 2

        for name in names:
            if not any(e["value"] == name for e in entities):
                entities.append({
                    "entity_type": "person",
                    "value": name,
                    "confidence": 0.9,
                    "source_snippet": f"...{name}..."
                })

        for org in orgs:
            entities.append({
                "entity_type": "organization",
                "value": org,
                "confidence": 0.85,
                "source_snippet": f"...{org}..."
            })

        for date in dates:
            entities.append({
                "entity_type": "date",
                "value": date,
                "confidence": 0.95,
                "source_snippet": f"...{date}..."
            })

        for amt in amounts:
            entities.append({
                "entity_type": "amount",
                "value": amt,
                "confidence": 0.9,
                "source_snippet": f"...{amt}..."
            })

        result = {
            "persons": names,
            "organizations": orgs,
            "dates": dates,
            "amounts": amounts,
            "key_terms": key_terms,
            "entities": entities,
            "extraction_confidence": confidence
        }

        content = json.dumps(result, indent=2)
        token_count = len(prompt.split()) + len(content.split())
        return LLMResponse(content=content, token_count=token_count, raw_response=content, prompt=prompt)

    async def _mock_classification(self, prompt: str) -> LLMResponse:
        doc_match = re.search(r'DOCUMENT TEXT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)
        doc_text = doc_match.group(1) if doc_match else prompt

        actual_type = self._detect_doc_type(doc_text)
        confidence = 4

        if self._should_fail(doc_text, "classification"):
            # Misclassify
            types = ["contract", "invoice", "report", "correspondence"]
            types.remove(actual_type)
            seed = self._hash_seed(doc_text + "misclass")
            rng = random.Random(seed)
            wrong_type = rng.choice(types)
            result = {
                "document_type": wrong_type,
                "classification_confidence": 2,
                "reasoning": f"The document contains elements suggesting it is a {wrong_type}, though some features are ambiguous.",
                "alternative_types": [actual_type]
            }
            confidence = 2
        else:
            result = {
                "document_type": actual_type,
                "classification_confidence": confidence,
                "reasoning": f"The document clearly exhibits characteristics of a {actual_type} based on its structure and terminology.",
                "alternative_types": []
            }

        content = json.dumps(result, indent=2)
        token_count = len(prompt.split()) + len(content.split())
        return LLMResponse(content=content, token_count=token_count, raw_response=content, prompt=prompt)

    async def _mock_summarization(self, prompt: str) -> LLMResponse:
        doc_match = re.search(r'DOCUMENT TEXT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)
        doc_text = doc_match.group(1) if doc_match else prompt

        type_match = re.search(r'DOCUMENT TYPE:\s*(\w+)', prompt)
        doc_type = type_match.group(1) if type_match else "report"

        # Generate a reasonable summary from the first few sentences
        sentences = re.split(r'[.!?]+', doc_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:4]
        summary_text = ". ".join(sentences[:2]) + "." if sentences else "Document contains structured information."

        confidence = 4
        key_points = [s[:80] for s in sentences[:3]] if sentences else ["No key points extracted"]
        action_items = []

        if self._should_fail(doc_text, "summarization"):
            # Context loss — drop important information or inject wrong facts
            seed = self._hash_seed(doc_text + "summary_fail")
            rng = random.Random(seed)
            if rng.random() < 0.5:
                # Include hallucinated entity from extraction
                hallucinated = rng.choice(["Alexander Worthington", "GlobalTech Dynamics", "Protocol X-47"])
                summary_text = f"This {doc_type} involves {hallucinated} and outlines several key provisions. " + summary_text
                confidence = 2
            else:
                # Lose context — make a vague summary
                summary_text = f"This {doc_type} discusses various topics and contains multiple sections of information."
                key_points = ["General information provided", "Multiple topics discussed"]
                confidence = 2

        result = {
            "summary": summary_text,
            "key_points": key_points,
            "action_items": action_items,
            "summarization_confidence": confidence
        }

        content = json.dumps(result, indent=2)
        token_count = len(prompt.split()) + len(content.split())
        return LLMResponse(content=content, token_count=token_count, raw_response=content, prompt=prompt)

    async def _mock_judge(self, prompt: str) -> LLMResponse:
        """Mock judge that detects common failure patterns."""
        step_match = re.search(r'STEP NAME:\s*(\w+)', prompt)
        step_name = step_match.group(1) if step_match else "unknown"

        input_match = re.search(r'STEP INPUT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)
        output_match = re.search(r'STEP OUTPUT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)
        original_match = re.search(r'ORIGINAL DOCUMENT:\s*---\s*(.*?)\s*---', prompt, re.DOTALL)

        step_input = input_match.group(1) if input_match else ""
        step_output = output_match.group(1) if output_match else ""
        original = original_match.group(1) if original_match else ""

        quality_score = 0.9
        failure_type = "none"
        explanation = "The output is a reasonable transformation of the input."
        evidence = ""
        is_problematic = False

        # Check for hallucinated entities
        try:
            output_data = json.loads(step_output)
        except (json.JSONDecodeError, TypeError):
            output_data = {}

        if step_name == "extraction" and "persons" in output_data:
            for person in output_data.get("persons", []):
                if person not in original and person not in step_input:
                    quality_score = 0.3
                    failure_type = "extraction_hallucination"
                    explanation = f"Extracted entity '{person}' does not appear in the source document."
                    evidence = f"Entity '{person}' was extracted but is not present in the original text."
                    is_problematic = True
                    break

        if step_name == "classification" and "document_type" in output_data:
            # Simple check — see if the classification makes sense
            doc_type = output_data["document_type"]
            actual = self._detect_doc_type(original) if original else None
            if actual and doc_type != actual:
                quality_score = 0.3
                failure_type = "misclassification"
                explanation = f"Document classified as '{doc_type}' but content suggests '{actual}'."
                evidence = f"Classification '{doc_type}' doesn't match document characteristics."
                is_problematic = True

        if step_name == "summarization":
            conf = output_data.get("summarization_confidence", 5)
            if conf <= 2:
                quality_score = 0.4
                failure_type = "context_loss"
                explanation = "Summary shows low confidence and may have lost important context."
                evidence = "Summarization confidence was very low."
                is_problematic = True

        result = {
            "quality_score": quality_score,
            "is_problematic": is_problematic,
            "failure_type": failure_type,
            "explanation": explanation,
            "evidence": evidence
        }

        content = json.dumps(result, indent=2)
        token_count = len(prompt.split()) + len(content.split())
        return LLMResponse(content=content, token_count=token_count, raw_response=content, prompt=prompt)


def get_provider() -> LLMProvider:
    """Factory function that returns the appropriate provider based on environment."""
    # Check for any API key to enable the Universal Provider
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    model = os.environ.get("LLM_MODEL", "").strip()
    
    # Fallback to provider-specific keys if LLM_API_KEY is not set
    if not api_key:
        api_key = (
            os.environ.get("OPENAI_API_KEY") or 
            os.environ.get("ANTHROPIC_API_KEY") or 
            os.environ.get("GEMINI_API_KEY") or 
            os.environ.get("DEEPSEEK_API_KEY") or 
            os.environ.get("MOONSHOT_API_KEY") or 
            ""
        ).strip()
        
    if not model and api_key:
        # Default model if an API key was provided but no model was specified
        model = "gpt-4o-mini"
        
    if api_key and model:
        return UniversalProvider(api_key=api_key, model=model)
        
    return MockProvider(failure_rate=0.2)
