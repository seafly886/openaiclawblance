"""
OpenAI API服务
"""

import os
import json
import requests
import time
from typing import Dict, Any, Optional, List
from app import db
from app.models.key import Key
from app.models.model import Model
from app.models.usage_stats import UsageStat
from app.models.chat_history import ChatHistory
from app.utils.key_rotation import key_rotation
from app.services.key_service import KeyService

class OpenAIService:
    """
    OpenAI API服务类
    """
    
    def __init__(self):
        """
        初始化OpenAI API服务
        """
        self.base_url = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
        self.timeout = 30  # 请求超时时间（秒）
        self.max_retries = 3  # 最大重试次数
    
    def get_headers(self, api_key: str) -> Dict[str, str]:
        """
        获取请求头
        """
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None,
                        key: Optional[Key] = None, stream: bool = False) -> Dict[str, Any]:
        """
        发送请求到OpenAI API
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers(key.key_value) if key else {}
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout, stream=stream)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 检查响应状态
                if response.status_code == 200:
                    if stream:
                        return response
                    
                    result = response.json()
                    # 添加使用的Key信息到结果中
                    if key:
                        result['_key_info'] = {
                            'id': key.id,
                            'key_value': key.key_value
                        }
                    return result
                elif response.status_code == 401:
                    # 认证失败，标记Key为无效
                    if key:
                        KeyService.set_key_status(key.id, 'error')
                    raise Exception('API Key无效')
                elif response.status_code == 429:
                    # 请求频率限制，等待后重试
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # 指数退避
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception('请求频率限制')
                else:
                    # 其他错误
                    error_info = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                    raise Exception(f"API请求失败: {response.status_code} - {error_info}")
            
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"请求失败: {str(e)}")
        
        raise Exception("超过最大重试次数")
    
    def get_models(self) -> Dict[str, Any]:
        """
        获取模型列表
        """
        try:
            # 使用加权轮询算法选择Key，确保使用次数均衡
            key = key_rotation.get_key_by_strategy('weighted_round_robin')
            if not key:
                raise Exception('没有可用的API Key')
            
            response = self.make_request('GET', 'models', key=key)
            
            # 更新Key使用统计
            KeyService.update_key_usage(key.id, 'models')
            
            return response
        except Exception as e:
            raise Exception(f"获取模型列表失败: {str(e)}")
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str,
                       temperature: float = 0.7, max_tokens: int = 1000,
                       **kwargs) -> Dict[str, Any]:
        """
        聊天完成
        """
        try:
            # 使用加权轮询算法选择Key，确保使用次数均衡
            key = key_rotation.get_key_by_strategy('weighted_round_robin')
            if not key:
                raise Exception('没有可用的API Key')
            
            # 构建请求数据
            data = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # 添加额外参数
            data.update(kwargs)
            
            # 发送请求
            response = self.make_request('POST', 'chat/completions', data=data, key=key)
            
            # 计算使用的token数量
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            
            # 更新Key使用统计
            KeyService.update_key_usage(key.id, model, tokens_used)
            
            return response
        except Exception as e:
            raise Exception(f"聊天请求失败: {str(e)}")

    def stream_chat_completion(self, messages: List[Dict[str, str]], model: str,
                               **kwargs):
        """
        流式聊天完成
        """
        try:
            # 使用加权轮询算法选择Key，确保使用次数均衡
            key = key_rotation.get_key_by_strategy('weighted_round_robin')
            if not key:
                raise Exception('没有可用的API Key')

            # 构建请求数据
            data = {
                'model': model,
                'messages': messages,
                'stream': True
            }
            data.update(kwargs)

            # 发送请求
            response = self.make_request('POST', 'chat/completions', data=data, key=key, stream=True)

            for chunk in response.iter_content(chunk_size=1024):
                yield chunk
        except Exception as e:
            raise Exception(f"流式聊天请求失败: {str(e)}")
    
    def completion(self, prompt: str, model: str, temperature: float = 0.7,
                  max_tokens: int = 1000, **kwargs) -> Dict[str, Any]:
        """
        文本完成
        """
        try:
            # 使用加权轮询算法选择Key，确保使用次数均衡
            key = key_rotation.get_key_by_strategy('weighted_round_robin')
            if not key:
                raise Exception('没有可用的API Key')
            
            # 构建请求数据
            data = {
                'model': model,
                'prompt': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # 添加额外参数
            data.update(kwargs)
            
            # 发送请求
            response = self.make_request('POST', 'completions', data=data, key=key)
            
            # 计算使用的token数量
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            
            # 更新Key使用统计
            KeyService.update_key_usage(key.id, model, tokens_used)
            
            return response
        except Exception as e:
            raise Exception(f"文本完成请求失败: {str(e)}")
    
    def test_key(self, key: Key) -> Dict[str, Any]:
        """
        测试Key是否有效
        """
        try:
            # 发送一个简单的请求测试Key
            response = self.make_request('GET', 'models', key=key)
            
            # 如果请求成功，Key是有效的
            return {
                'valid': True,
                'message': 'Key有效',
                'models_count': len(response.get('data', []))
            }
        except Exception as e:
            return {
                'valid': False,
                'message': str(e)
            }

# 全局OpenAI服务实例
openai_service = OpenAIService()