"""Configuration management for Gemma 4 Personal OS"""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables
load_dotenv()


@dataclass
class OllamaConfig:
    """Ollama configuration"""
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    num_parallel: int = int(os.getenv("OLLAMA_NUM_PARALLEL", "2"))
    gpu_enabled: bool = os.getenv("OLLAMA_GPU", "1") == "1"
    gpu_memory: str = os.getenv("OLLAMA_GPU_MEMORY", "24gb")
    model_expert: str = os.getenv("CREW_AI_LLM", "gemma2:26b")
    model_fast: str = os.getenv("CREW_AI_LLM_FAST", "gemma2:2b")
    complexity_threshold: int = int(os.getenv("COMPLEXITY_THRESHOLD", "500"))


@dataclass
class RAGConfig:
    """AnythingLLM RAG configuration"""
    host: str = os.getenv("ANYTHINGLLM_HOST", "http://localhost:3001")
    api_key: str = os.getenv("ANYTHINGLLM_API_KEY", "default")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1024"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    top_k: int = int(os.getenv("RAG_TOP_K", "5"))


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: str = os.getenv("DATABASE_TYPE", "sqlite")
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///.gemma-os/gemma_os.db")
    echo: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "json")
    file: str = os.path.expanduser(os.getenv("LOG_FILE", "~/.gemma-os/logs/app.log"))
    audit_log: str = os.path.expanduser(os.getenv("AUDIT_LOG_PATH", "~/.gemma-os/audit.log"))
    audit_retention_days: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))


@dataclass
class APIConfig:
    """External API configuration"""
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    serper_enabled: bool = os.getenv("SERPER_ENABLED", "true").lower() == "true"
    offline_mode: bool = os.getenv("OFFLINE_MODE", "false").lower() == "true"


class Config:
    """Central configuration manager"""

    def __init__(self):
        """Initialize all configuration sections"""
        self.ollama = OllamaConfig()
        self.rag = RAGConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self.api = APIConfig()

        # Create directories if they don't exist
        self._ensure_directories()

    @staticmethod
    def _ensure_directories():
        """Create required directories"""
        dirs = [
            Path.home() / ".gemma-os" / "results",
            Path.home() / ".gemma-os" / "cache",
            Path.home() / ".gemma-os" / "skills",
            Path.home() / ".gemma-os" / "logs",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """Validate configuration"""
        checks = [
            (self.ollama.host, "Ollama host must be set"),
            (self.ollama.model_expert, "Expert model must be configured"),
            (self.ollama.model_fast, "Fast model must be configured"),
        ]

        for value, error_msg in checks:
            if not value:
                print(f"❌ {error_msg}")
                return False

        print("✓ Configuration validated")
        return True

    def summary(self) -> dict:
        """Return configuration summary"""
        return {
            "ollama": {
                "host": self.ollama.host,
                "expert_model": self.ollama.model_expert,
                "fast_model": self.ollama.model_fast,
                "gpu_enabled": self.ollama.gpu_enabled,
            },
            "rag": {
                "host": self.rag.host,
                "chunk_size": self.rag.chunk_size,
            },
            "database": {
                "type": self.database.db_type,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
            },
        }
