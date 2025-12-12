"""
Business Discovery Service - AI-powered Semantic SEO framework generation.

This module takes simple business information from users and uses AI to
automatically generate the technical Koray framework parameters:
- Source Context
- Central Entity
- Central Search Intent
- Functional Words (Predicates)

This removes the complexity for beginners who don't understand Semantic SEO.
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

from config.settings import get_settings
from config.ai_providers import get_ai_client


@dataclass
class FrameworkResult:
    """Result of AI framework generation."""
    source_context: str
    central_entity: str
    central_search_intent: str
    functional_words: list[str]
    explanation: str  # Plain English explanation for the user
    confidence: str  # high, medium, low
    raw_response: Optional[str] = None


# System prompt for generating Koray's Semantic SEO framework
FRAMEWORK_GENERATION_PROMPT = '''You are an expert in Koray Tuğberk GÜBÜR's Semantic SEO framework. 
Your job is to analyze business information and extract the key semantic elements that will be used 
to build a comprehensive Topical Authority strategy.

Based on Koray's framework, you need to identify:

1. **Source Context**: The intersection of "who they are," "what their brand identity is," and 
   "how they make money." This defines the "lens" through which they cover their topic.
   
2. **Central Entity**: The main subject matter that will appear site-wide. This is the core 
   concept that defines their expertise area.
   
3. **Central Search Intent**: The unification of Source Context + Central Entity. This represents 
   what users ultimately want when they search for topics in this space. Think about the 
   predicates (verbs/actions) users associate with the entity.
   
4. **Functional Words**: The key verbs and actions that connect users to the entity. These are 
   words like "buy," "learn," "find," "compare," "get," etc. that indicate what users want to DO.

IMPORTANT RULES:
- The Central Entity should be a broad enough concept to support a full content network
- The Source Context should clearly explain their monetization angle
- Functional Words should be action verbs that represent user intent
- Be specific but not too narrow - they need room to build topical authority

Respond with a JSON object in this exact format:
{
    "source_context": "Who they are and how they make money (2-3 sentences)",
    "central_entity": "Main subject/topic (1-3 words)",
    "central_search_intent": "What users want when searching for this topic (1-2 sentences)",
    "functional_words": ["verb1", "verb2", "verb3", "verb4", "verb5"],
    "explanation": "Plain English explanation of why these were chosen (3-4 sentences for a beginner)",
    "confidence": "high/medium/low - based on how much info was provided"
}'''


USER_PROMPT_TEMPLATE = '''Please analyze this business and generate the Semantic SEO framework parameters.

## Business Information Provided:

**Business Name:** {business_name}

**Business Description:** 
{business_description}

**Products/Services:**
{products_services}

**Target Customers:**
{target_customers}

**How They Make Money:**
{monetization}

**Website URL (if provided):** {website_url}

**Additional Context:**
{additional_context}

---

Now generate the Semantic SEO framework elements (Source Context, Central Entity, 
Central Search Intent, and Functional Words) based on this information.

Remember to explain your reasoning in plain English for someone new to SEO.'''


class BusinessDiscoveryService:
    """Service for AI-powered business discovery and framework generation."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def generate_framework(
        self,
        business_name: str,
        business_description: str = "",
        products_services: str = "",
        target_customers: str = "",
        monetization: str = "",
        website_url: str = "",
        additional_context: str = ""
    ) -> FrameworkResult:
        """
        Generate Koray's Semantic SEO framework from simple business info.
        
        Args:
            business_name: Name of the business (required)
            business_description: What the business does
            products_services: What they sell or offer
            target_customers: Who their customers are
            monetization: How they make money
            website_url: Optional website for context
            additional_context: Any other relevant info
            
        Returns:
            FrameworkResult with generated framework parameters
        """
        # Build the user prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            business_name=business_name or "Not provided",
            business_description=business_description or "Not provided",
            products_services=products_services or "Not provided",
            target_customers=target_customers or "Not provided",
            monetization=monetization or "Not provided",
            website_url=website_url or "Not provided",
            additional_context=additional_context or "None"
        )
        
        # Get AI response
        response = self._call_ai(
            system_prompt=FRAMEWORK_GENERATION_PROMPT,
            user_prompt=user_prompt
        )
        
        # Parse the response
        return self._parse_response(response)
    
    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured AI provider."""
        client = get_ai_client()
        
        if client is None:
            raise ValueError(
                "No AI provider configured. "
                "Please add an API key in Settings."
            )
        
        # Get provider and model from settings
        provider = self.settings.ai.default_provider
        model = self.settings.ai.default_model
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"AI API error: {str(e)}")
    
    def _parse_response(self, response: str) -> FrameworkResult:
        """Parse the AI response into a FrameworkResult."""
        try:
            # Try to extract JSON from the response
            # Handle cases where AI wraps JSON in markdown code blocks
            clean_response = response.strip()
            if "```json" in clean_response:
                clean_response = clean_response.split("```json")[1]
                clean_response = clean_response.split("```")[0]
            elif "```" in clean_response:
                clean_response = clean_response.split("```")[1]
                clean_response = clean_response.split("```")[0]
            
            data = json.loads(clean_response.strip())
            
            return FrameworkResult(
                source_context=data.get("source_context", ""),
                central_entity=data.get("central_entity", ""),
                central_search_intent=data.get("central_search_intent", ""),
                functional_words=data.get("functional_words", []),
                explanation=data.get("explanation", ""),
                confidence=data.get("confidence", "medium"),
                raw_response=response
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract info manually
            return FrameworkResult(
                source_context="Could not parse - please try again",
                central_entity="",
                central_search_intent="",
                functional_words=[],
                explanation=f"The AI response could not be parsed. Raw: {response[:500]}",
                confidence="low",
                raw_response=response
            )


def generate_framework_from_business_info(
    business_name: str,
    business_description: str = "",
    products_services: str = "",
    target_customers: str = "",
    monetization: str = "",
    website_url: str = "",
    additional_context: str = ""
) -> FrameworkResult:
    """
    Convenience function to generate framework without instantiating service.
    
    This is the main entry point for the discovery wizard.
    """
    service = BusinessDiscoveryService()
    return service.generate_framework(
        business_name=business_name,
        business_description=business_description,
        products_services=products_services,
        target_customers=target_customers,
        monetization=monetization,
        website_url=website_url,
        additional_context=additional_context
    )


# Example prompts to help users answer questions
BUSINESS_QUESTION_HINTS = {
    "business_description": [
        "What does the company do in 1-2 sentences?",
        "Example: 'We help people learn Spanish through online courses'",
        "Example: 'We sell organic skincare products made in the USA'",
        "Example: 'We provide visa consulting for people moving to Germany'",
    ],
    "products_services": [
        "List the main things you sell or services you provide",
        "Example: 'Online courses, 1-on-1 tutoring, textbooks'",
        "Example: 'Face creams, serums, cleansers, body lotions'",
        "Example: 'Visa applications, document preparation, relocation advice'",
    ],
    "target_customers": [
        "Who are you trying to reach?",
        "Example: 'Young professionals who want to learn Spanish for travel'",
        "Example: 'Women 25-45 who care about natural ingredients'",
        "Example: 'Tech workers looking to relocate to Europe'",
    ],
    "monetization": [
        "How does the business make money?",
        "Example: 'Selling online course subscriptions'",
        "Example: 'E-commerce product sales + affiliate commissions'",
        "Example: 'Service fees for visa application processing'",
    ],
}