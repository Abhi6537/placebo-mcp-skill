"""
Placebo Interface Protocols.
"""

from placebo.protocols.storage import StorageAdapter
from placebo.protocols.falsifier import FalsificationEngine
from placebo.protocols.llm import LLMExplainer

__all__ = ["StorageAdapter", "FalsificationEngine", "LLMExplainer"]
