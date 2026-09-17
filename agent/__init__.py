"""
Agent Package for Apple Customer Support AI System.
"""
from agent.agent import SupportAgent, AgentOutput
from agent.taxonomy import INTENT_TAXONOMY, ALL_INTENTS
from agent.config import BRAND_NAME, BRAND_VOICE, APPLE_RESOURCES

__all__ = ["SupportAgent", "AgentOutput", "INTENT_TAXONOMY", "ALL_INTENTS", "BRAND_NAME", "BRAND_VOICE", "APPLE_RESOURCES"]
