"""
聊天功能路由
"""

import logging
from flask import Blueprint, request, jsonify, Response, current_app, g
from app import db
from app.models.key import Key
from app.models.model import Model
from app.models.usage_stats import UsageStat
from app.models.chat_history import ChatHistory
from app.services.openai_service import openai_service
from app.services.key_service import KeyService
import json

# 创建蓝图
bp = Blueprint('chat_routes', __name__)

@bp.route('/api/chat', methods=['POST'])
def chat():
    """
    聊天接口
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data or 'model' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: messages 或 model'
            }), 400
        
        model_name = data['model']
        messages = data['messages']
        
        # 检查模型是否存在
        model = Model.query.filter_by(model_name=model_name).first()
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }), 400
        
        # 创建聊天历史记录
        chat_record = ChatHistory.create_record(
            key_id=0,  # 先设置为0，后面更新
            model=model_name,
            model_id=model.id,
            request=json.dumps(data)
        )
        
        # 获取额外参数
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        # 调用OpenAI API
        try:
            response_data = openai_service.chat_completion(
                messages=messages,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 从OpenAI API响应中获取使用的Key信息
            key_info = response_data.get('_key_info')
            if key_info:
                # 更新聊天历史记录中的Key ID
                chat_record.key_id = key_info['id']
                
                # 更新聊天历史记录
                chat_record.update_response(
                    response=json.dumps(response_data),
                    tokens_used=response_data.get('usage', {}).get('total_tokens', 0)
                )
        except Exception as api_error:
            # 如果API调用失败，仍然记录聊天历史
            chat_record.update_response(
                response=json.dumps({'error': str(api_error)}),
                tokens_used=0
            )
            
            # 重新抛出异常
            raise api_error
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'聊天请求失败: {str(e)}'
        }), 500

@bp.route('/api/chat/completions', methods=['POST'])
@bp.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    OpenAI兼容的聊天完成接口
    """
    try:
        logging.info("Received request for /v1/chat/completions")
        data = request.get_json()
        logging.info(f"Request data: {data}")
        
        if not data or 'messages' not in data or 'model' not in data:
            logging.warning("Missing required parameters: messages or model")
            return jsonify({
                'error': {
                    'message': 'Missing required parameters: messages or model',
                    'type': 'invalid_request_error',
                    'code': 'missing_parameters'
                }
            }), 400
        
        model_name = data['model']
        messages = data['messages']
        stream = data.get('stream', False)

        # 检查模型是否存在
        model = Model.query.filter_by(model_name=model_name).first()
        if not model:
            logging.warning(f"Model not found: {model_name}")
            return jsonify({
                'error': {
                    'message': f'Model {model_name} not found',
                    'type': 'invalid_request_error',
                    'code': 'model_not_found'
                }
            }), 404
        
        # 创建聊天历史记录
        chat_record = ChatHistory.create_record(
            key_id=0,  # 先设置为0，后面更新
            model=model_name,
            model_id=model.id,
            request=json.dumps(data)
        )
        
        # 获取额外参数
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        top_p = data.get('top_p', 1.0)
        frequency_penalty = data.get('frequency_penalty', 0)
        presence_penalty = data.get('presence_penalty', 0)
        
        if stream:
            logging.info("Streaming response requested")
            g.app = current_app._get_current_object()
            def generate():
                with g.app.app_context():
                    is_empty = True
                    try:
                        for chunk in openai_service.stream_chat_completion(
                            messages=messages,
                            model=model_name,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty
                        ):
                            if chunk:
                                is_empty = False
                                logging.info(f"Streaming chunk: {chunk}")
                                yield chunk
                    except Exception as e:
                        logging.error(f"流式聊天请求失败: {e}")
                        # 在流中返回错误信息
                        error_message = json.dumps({'error': str(e)})
                        yield f"data: {error_message}\n\n"
                    
                    if is_empty:
                        logging.warning("Empty completion in streaming response")
                        # 如果没有收到任何数据，则返回一个错误
                        error_message = json.dumps({'error': 'Empty completion in streaming response'})
                        yield f"data: {error_message}\n\n"

            return Response(generate(), mimetype='text/event-stream')

        # 调用OpenAI API
        try:
            logging.info("Calling OpenAI API for chat completion")
            response_data = openai_service.chat_completion(
                messages=messages,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            logging.info(f"OpenAI API response: {response_data}")
            
            # 从OpenAI API响应中获取使用的Key信息
            key_info = response_data.get('_key_info')
            if key_info:
                # 更新聊天历史记录中的Key ID
                chat_record.key_id = key_info['id']
                
                # 更新聊天历史记录
                chat_record.update_response(
                    response=json.dumps(response_data),
                    tokens_used=response_data.get('usage', {}).get('total_tokens', 0)
                )
        except Exception as api_error:
            logging.error(f"Error calling OpenAI API: {api_error}")
            # 如果API调用失败，仍然记录聊天历史
            chat_record.update_response(
                response=json.dumps({'error': str(api_error)}),
                tokens_used=0
            )
            
            # 重新抛出异常
            raise api_error
        
        # 移除自定义的 _key_info 字段
        if '_key_info' in response_data:
            del response_data['_key_info']
            
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error in chat_completions: {e}")
        return jsonify({
            'error': {
                'message': str(e),
                'type': 'api_error',
                'code': 'api_error'
            }
        }), 500

@bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """
    获取聊天历史记录
    """
    try:
        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        key_id = request.args.get('key_id', type=int)
        model = request.args.get('model')
        
        if key_id:
            # 根据Key获取聊天历史
            history = ChatHistory.get_history_by_key(key_id, limit)
        elif model:
            # 根据模型获取聊天历史
            history = ChatHistory.get_history_by_model(model, limit)
        else:
            # 获取最近的聊天历史
            history = ChatHistory.get_recent_history(limit)
        
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in history]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取聊天历史失败: {str(e)}'
        }), 500

@bp.route('/api/chat/history/<int:history_id>', methods=['GET'])
def get_chat_history_detail(history_id):
    """
    获取聊天历史详情
    """
    try:
        chat_record = ChatHistory.query.get_or_404(history_id)
        
        return jsonify({
            'success': True,
            'data': chat_record.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取聊天历史详情失败: {str(e)}'
        }), 500

@bp.route('/api/chat/history/<int:history_id>', methods=['DELETE'])
def delete_chat_history(history_id):
    """
    删除聊天历史记录
    """
    try:
        chat_record = ChatHistory.query.get_or_404(history_id)
        db.session.delete(chat_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '聊天历史记录删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除聊天历史记录失败: {str(e)}'
        }), 500