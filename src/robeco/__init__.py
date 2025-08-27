"""
Robeco AI Investment Analysis System

A comprehensive AI-powered investment analysis platform with real-time streaming,
multi-agent collaboration, and professional-grade financial reporting.

Version: 2.0.0
Author: Robeco Investment Research Team
"""

__version__ = "2.0.0"
__author__ = "Robeco Investment Research Team"

from .core.config import Settings
from .core.models import AnalysisContext

__all__ = ["Settings", "AnalysisContext"]