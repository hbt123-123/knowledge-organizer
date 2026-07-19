#!/usr/bin/env python3
"""
config.py - 统一配置管理模块
管理 API 密钥、模型配置等
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any


DEFAULT_CONFIG = {
    "api": {
        "base_url": "https://coding.dashscope.aliyuncs.com/v1",
        "api_key": "",
        "model": "qwen3.5-plus",
        "vision_model": "qwen3.5-plus",
        "embedding_model": "text-embedding-v3",
        "enable_embedding": False
    },
    "workflow": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "timeout": 120
    }
}


def find_config_file() -> Optional[Path]:
    """查找配置文件"""
    possible_paths = [
        Path.cwd() / "config.json",
        Path(__file__).parent.parent.parent / "config.json",
        Path.home() / ".knowledge-organizer" / "config.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None


def load_config() -> Dict[str, Any]:
    """加载配置"""
    config = DEFAULT_CONFIG.copy()
    
    config_file = find_config_file()
    if config_file:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                config = deep_merge(config, user_config)
        except Exception:
            pass
    
    env_api_key = os.environ.get("DASHSCOPE_API_KEY")
    if env_api_key:
        config["api"]["api_key"] = env_api_key
    
    env_base_url = os.environ.get("DASHSCOPE_BASE_URL")
    if env_base_url:
        config["api"]["base_url"] = env_base_url
    
    return config


def deep_merge(base: Dict, override: Dict) -> Dict:
    """深度合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_api_config() -> Dict[str, str]:
    """获取 API 配置"""
    config = load_config()
    return config.get("api", {})


def get_workflow_config() -> Dict[str, Any]:
    """获取工作流配置"""
    config = load_config()
    return config.get("workflow", {})


_config: Optional[Dict] = None


def get_config() -> Dict[str, Any]:
    """获取完整配置（带缓存）"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Dict[str, Any]:
    """重新加载配置"""
    global _config
    _config = None
    return get_config()
