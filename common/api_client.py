#!/usr/bin/env python3
"""
api_client.py - API 客户端模块
封装 LLM 和视觉模型的 API 调用
"""

import base64
import json
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import get_api_config, get_workflow_config


class APIClient:
    """统一的 API 客户端"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or get_api_config()
        self.workflow_config = get_workflow_config()
        self._client: Optional[OpenAI] = None
        
        if OPENAI_AVAILABLE:
            self._init_openai_client()
    
    def _init_openai_client(self):
        """初始化 OpenAI 兼容客户端"""
        self._client = OpenAI(
            api_key=self.config.get("api_key", ""),
            base_url=self.config.get("base_url", "https://coding.dashscope.aliyuncs.com/v1"),
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.config.get('api_key', '')}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天补全 API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            API 响应
        """
        model = model or self.config.get("model", "qwen3.5-plus")
        max_retries = self.workflow_config.get("max_retries", 3)
        retry_delay = self.workflow_config.get("retry_delay", 1.0)
        
        if self._client:
            for attempt in range(max_retries):
                try:
                    response = self._client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    return {
                        "status": "success",
                        "content": response.choices[0].message.content,
                        "model": model,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        } if response.usage else None
                    }
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                    else:
                        return {"status": "error", "error": str(e)}
        
        if HTTPX_AVAILABLE:
            return self._chat_completion_httpx(messages, model, temperature, max_tokens)
        
        return {"status": "error", "error": "No HTTP client available. Install openai or httpx."}
    
    def _chat_completion_httpx(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """使用 httpx 调用 API"""
        url = f"{self.config.get('base_url', '')}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        max_retries = self.workflow_config.get("max_retries", 3)
        retry_delay = self.workflow_config.get("retry_delay", 1.0)
        timeout = self.workflow_config.get("timeout", 60)
        
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(
                        url,
                        headers=self._get_headers(),
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    return {
                        "status": "success",
                        "content": data["choices"][0]["message"]["content"],
                        "model": model,
                        "usage": data.get("usage")
                    }
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    return {"status": "error", "error": str(e)}
        
        return {"status": "error", "error": "Max retries exceeded"}
    
    def vision_completion(
        self,
        image_path: str,
        prompt: str = "请详细描述这张图片的内容，包括文字、图表、公式等信息。",
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用视觉模型分析图片
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            model: 模型名称
            
        Returns:
            分析结果
        """
        model = model or self.config.get("vision_model", self.config.get("model", "qwen3.5-plus"))
        
        image_data = self._encode_image(image_path)
        if image_data["status"] == "error":
            return image_data
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data['base64']}"
                        }
                    }
                ]
            }
        ]
        
        return self.chat_completion(messages, model=model, **kwargs)
    
    def _encode_image(self, image_path: str) -> Dict[str, Any]:
        """将图片编码为 base64"""
        try:
            path = Path(image_path)
            if not path.exists():
                return {"status": "error", "error": f"Image not found: {image_path}"}
            
            with open(path, "rb") as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode("utf-8")
            return {"status": "success", "base64": base64_image}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型名称
            
        Returns:
            嵌入向量
        """
        model = model or self.config.get("embedding_model", "text-embedding-v3")
        
        if self._client:
            try:
                response = self._client.embeddings.create(
                    model=model,
                    input=text
                )
                return {
                    "status": "success",
                    "embedding": response.data[0].embedding,
                    "model": model
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        if HTTPX_AVAILABLE:
            return self._embedding_httpx(text, model)
        
        return {"status": "error", "error": "No HTTP client available"}
    
    def _embedding_httpx(self, text: str, model: str) -> Dict[str, Any]:
        """使用 httpx 调用嵌入 API"""
        url = f"{self.config.get('base_url', '')}/embeddings"
        
        payload = {
            "model": model,
            "input": text
        }
        
        timeout = self.workflow_config.get("timeout", 60)
        
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "embedding": data["data"][0]["embedding"],
                    "model": model
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}


_client: Optional[APIClient] = None


def get_client() -> APIClient:
    """获取全局 API 客户端"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：调用 LLM
    
    Args:
        prompt: 用户提示
        system_prompt: 系统提示
        model: 模型名称
        
    Returns:
        响应结果
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    return get_client().chat_completion(messages, model=model, **kwargs)


def analyze_image(
    image_path: str,
    prompt: str = "请详细描述这张图片的内容，包括文字、图表、公式等信息。",
    model: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：分析图片
    
    Args:
        image_path: 图片路径
        prompt: 提示词
        model: 模型名称
        
    Returns:
        分析结果
    """
    return get_client().vision_completion(image_path, prompt, model, **kwargs)


def get_embedding(text: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    便捷函数：获取文本嵌入
    
    Args:
        text: 输入文本
        model: 模型名称
        
    Returns:
        嵌入向量
    """
    return get_client().embedding(text, model)
