"""LLM Service Module

Integrates Google Gemini API for news analysis, sentiment extraction,
and justification text generation. Provides structured outputs for
the Scalpel Dive analysis workflow.
"""

import logging
import json
from typing import Dict, List, Optional
import google.generativeai as genai

from config.settings import settings
from config.strategy_params import NEWS_LLM_SETTINGS
from data.models import NewsArticle

logger = logging.getLogger(__name__)


# ============================================================================
# Gemini Configuration
# ============================================================================

def configure_gemini():
    """Configure Gemini API with credentials"""
    if not settings.gemini_available:
        logger.warning("Gemini API key not configured")
        return False

    try:
        genai.configure(api_key=settings.gemini_api_key)
        logger.info("Gemini API configured successfully")
        return True

    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        return False


# ============================================================================
# LLM Service Class
# ============================================================================

class LLMService:
    """Google Gemini LLM service for news analysis"""

    def __init__(self):
        self.configured = configure_gemini()
        if self.configured:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_news(
        self,
        ticker: str,
        etf_name: str,
        articles: List[NewsArticle]
    ) -> Optional[Dict]:
        """Analyze news articles and extract structured insights

        Args:
            ticker: ETF ticker symbol
            etf_name: Full ETF name
            articles: List of NewsArticle models

        Returns:
            Dict with sentiment, themes, risks, and summary
        """
        if not self.configured or not articles:
            logger.warning(f"Cannot analyze news for {ticker} - LLM not configured or no articles")
            return None

        logger.info(f"Analyzing {len(articles)} articles for {ticker} using Gemini...")

        # Prepare article text
        article_text = self._format_articles_for_llm(articles)

        # Build prompt
        prompt = self._build_news_analysis_prompt(ticker, etf_name, article_text)

        try:
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=NEWS_LLM_SETTINGS['llm_temperature'],
                    max_output_tokens=NEWS_LLM_SETTINGS['llm_max_tokens'],
                )
            )

            # Parse response
            result = self._parse_news_analysis_response(response.text)
            logger.info(f"Successfully analyzed news for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing news for {ticker}: {e}")
            return None

    def _format_articles_for_llm(self, articles: List[NewsArticle]) -> str:
        """Format articles for LLM input

        Args:
            articles: List of NewsArticle models

        Returns:
            Formatted article text
        """
        formatted = []

        for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles
            formatted.append(f"Article {i}:")
            formatted.append(f"  Title: {article.title}")
            formatted.append(f"  Source: {article.source}")
            if article.description:
                formatted.append(f"  Description: {article.description}")
            if article.content:
                # Truncate content to avoid token limits
                content = article.content[:500]
                formatted.append(f"  Content: {content}")
            formatted.append("")

        return "\n".join(formatted)

    def _build_news_analysis_prompt(
        self,
        ticker: str,
        etf_name: str,
        article_text: str
    ) -> str:
        """Build structured prompt for news analysis

        Args:
            ticker: ETF ticker
            etf_name: Full ETF name
            article_text: Formatted article text

        Returns:
            Prompt string
        """
        return f"""You are a financial analyst analyzing news for {ticker} ({etf_name}).

Below are recent news articles related to this ETF and its underlying sector:

{article_text}

Please provide a comprehensive analysis in JSON format with the following fields:

1. **summary** (string): A 2-3 sentence summary of the main themes and narratives across all articles. Focus on actionable investment insights.

2. **sentiment_score** (float): Overall sentiment score from -1.0 (very negative) to +1.0 (very positive). Consider both explicit sentiment and implicit market implications.

3. **relevance_score** (float): How relevant these articles are to the ETF's investment thesis, from 0.0 (not relevant) to 1.0 (highly relevant).

4. **key_themes** (array of strings): List 2-4 key investment themes or narratives. Examples: "AI infrastructure spending", "Regulatory headwinds", "Earnings strength".

5. **risk_factors** (array of strings): List 2-4 risk factors or concerns mentioned. Examples: "Valuation concerns", "Geopolitical risk", "Supply chain disruptions".

6. **investment_implication** (string): One sentence describing the key investment implication (bullish, bearish, or mixed).

Respond ONLY with valid JSON. No markdown formatting, no code blocks, just raw JSON.

Example format:
{{
  "summary": "Technology sector showing strong momentum...",
  "sentiment_score": 0.65,
  "relevance_score": 0.85,
  "key_themes": ["AI growth", "Strong earnings", "Institutional buying"],
  "risk_factors": ["Valuation concerns", "Potential profit-taking"],
  "investment_implication": "Positive momentum supported by fundamentals, but monitor valuation"
}}
"""

    def _parse_news_analysis_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured dict

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed dict or default values if parsing fails
        """
        try:
            # Try to find JSON in response
            # Sometimes LLM wraps JSON in markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()

            # Parse JSON
            result = json.loads(json_text)

            # Validate and clamp values
            result['sentiment_score'] = max(-1.0, min(1.0, float(result.get('sentiment_score', 0.0))))
            result['relevance_score'] = max(0.0, min(1.0, float(result.get('relevance_score', 0.5))))

            # Ensure arrays
            if 'key_themes' not in result or not isinstance(result['key_themes'], list):
                result['key_themes'] = []
            if 'risk_factors' not in result or not isinstance(result['risk_factors'], list):
                result['risk_factors'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Response text: {response_text[:200]}")
            return self._get_default_response()
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._get_default_response()

    def _get_default_response(self) -> Dict:
        """Get default response when LLM fails

        Returns:
            Default response dict
        """
        return {
            'summary': 'News analysis unavailable',
            'sentiment_score': 0.0,
            'relevance_score': 0.0,
            'key_themes': [],
            'risk_factors': [],
            'investment_implication': 'Unable to determine'
        }

    def generate_justification_enhancement(
        self,
        ticker: str,
        action: str,
        quantitative_evidence: Dict[str, str],
        qualitative_evidence: Dict[str, str]
    ) -> Optional[str]:
        """Generate enhanced justification text using LLM

        Args:
            ticker: ETF ticker
            action: Action type (BUY, SELL, HOLD, etc.)
            quantitative_evidence: Dict of quantitative metrics
            qualitative_evidence: Dict of qualitative factors

        Returns:
            Enhanced justification text or None
        """
        if not self.configured:
            return None

        prompt = f"""As a portfolio manager, write a professional 2-3 sentence justification for the following trade recommendation:

Ticker: {ticker}
Action: {action}

Quantitative Evidence:
{self._format_evidence(quantitative_evidence)}

Qualitative Evidence:
{self._format_evidence(qualitative_evidence)}

Write a concise, professional justification that synthesizes both quantitative and qualitative factors. Focus on the "why" behind the trade, not just the "what". Suitable for inclusion in an investment prospectus.

Respond with only the justification text, no additional commentary."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=300,
                )
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating justification enhancement: {e}")
            return None

    def _format_evidence(self, evidence: Dict[str, str]) -> str:
        """Format evidence dict for LLM prompt

        Args:
            evidence: Evidence dict

        Returns:
            Formatted evidence string
        """
        return "\n".join([f"- {k}: {v}" for k, v in evidence.items()])

    def test_connection(self) -> bool:
        """Test Gemini API connection

        Returns:
            True if API is working, False otherwise
        """
        if not self.configured:
            return False

        try:
            response = self.model.generate_content(
                "Respond with only the word 'OK' if you receive this message.",
                generation_config=genai.GenerationConfig(max_output_tokens=10)
            )
            result = "OK" in response.text.upper()
            if result:
                logger.info("Gemini API connection test: SUCCESS")
            else:
                logger.warning("Gemini API connection test: FAILED")
            return result

        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            return False


# ============================================================================
# Convenience Functions
# ============================================================================

# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance

    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def analyze_news_with_llm(
    ticker: str,
    etf_name: str,
    articles: List[NewsArticle]
) -> Optional[Dict]:
    """Convenience function for news analysis

    Args:
        ticker: ETF ticker
        etf_name: Full ETF name
        articles: List of NewsArticle models

    Returns:
        Analysis dict or None
    """
    service = get_llm_service()
    return service.analyze_news(ticker, etf_name, articles)
