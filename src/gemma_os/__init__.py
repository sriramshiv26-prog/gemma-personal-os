"""
Gemma 4 Personal OS - Enterprise Local AI Workstation

A production-ready, local-first AI system delivering enterprise-grade reasoning
on consumer hardware without cloud dependency.

Version: 1.0
Status: Production Ready
"""

__version__ = "1.0.0"
__author__ = "Sriram"
__license__ = "MIT"

from .core.router import ModelRouter
from .core.orchestrator import Orchestrator
from .core.config import Config
from .core.database import Database

__all__ = [
    "ModelRouter",
    "Orchestrator",
    "Config",
    "Database",
]


def init_db():
    """Initialize database on first run"""
    db = Database()
    db.init()
    return db


def load_skills():
    """Load SKILL.md files from skills directory"""
    from .utils.skill_loader import SkillLoader
    loader = SkillLoader()
    return loader.load_all()
