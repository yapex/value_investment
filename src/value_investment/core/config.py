"""Configuration module"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration"""

    cache_dir: str = "./.cache"
    cache_ttl: int = 86400  # 1 day in seconds

    def __post_init__(self):
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)
