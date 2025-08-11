"""
模型管理路由
"""

import logging
import time
from flask import Blueprint, request, jsonify
from app.services.model_service import ModelService

# 创建蓝图
bp = Blueprint('model_routes', __name__)

@bp.route('/api/models', methods=['GET'])
@bp.route('/v1/models', methods=['GET'])
def get_models():
    """
    获取所有模型列表
    """
    try:
        logging.info("Received request for /v1/models")
        # 获取查询参数
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        if refresh:
            logging.info("Refreshing models from OpenAI API")
            # 从OpenAI API刷新模型列表
            try:
                models = ModelService.refresh_models()
                logging.info("Successfully refreshed models")
            except Exception as e:
                logging.error(f"Failed to refresh models: {e}")
                # 如果刷新失败，使用数据库中的模型列表
                models = ModelService.get_all_models()
        else:
            logging.info("Fetching models from database")
            # 使用数据库中的模型列表
            models = ModelService.get_all_models()
        
        response_data = {
            "object": "list",
            "data": [
                {
                    "id": model.model_name,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openai"
                }
                for model in models
            ]
        }
        logging.info(f"Returning {len(response_data['data'])} models")
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error getting models: {e}")
        return jsonify({
            'success': False,
            'message': f'获取模型列表失败: {str(e)}'
        }), 500

@bp.route('/api/models/<string:model_name>', methods=['GET'])
def get_model(model_name):
    """
    获取特定模型信息
    """
    try:
        model = ModelService.get_model_by_name(model_name)
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型信息失败: {str(e)}'
        }), 500

@bp.route('/api/models/<string:model_name>/stats', methods=['GET'])
def get_model_stats(model_name):
    """
    获取模型使用统计
    """
    try:
        stats = ModelService.get_model_stats(model_name)
        if not stats:
            return jsonify({
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型统计失败: {str(e)}'
        }), 500

@bp.route('/api/models', methods=['POST'])
def create_model():
    """
    创建新模型
    """
    try:
        data = request.get_json()
        
        if not data or 'model_name' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: model_name'
            }), 400
        
        try:
            new_model = ModelService.create_model(
                model_name=data['model_name'],
                description=data.get('description', ''),
                capabilities=data.get('capabilities', '')
            )
            
            return jsonify({
                'success': True,
                'message': '模型创建成功',
                'data': new_model.to_dict()
            }), 201
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建模型失败: {str(e)}'
        }), 500

@bp.route('/api/models/<string:model_name>', methods=['PUT'])
def update_model(model_name):
    """
    更新模型信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '缺少更新数据'
            }), 400
        
        updated_model = ModelService.update_model(
            model_name=model_name,
            description=data.get('description'),
            capabilities=data.get('capabilities')
        )
        if not updated_model:
            return jsonify({
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '模型更新成功',
            'data': updated_model.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新模型失败: {str(e)}'
        }), 500

@bp.route('/api/models/<string:model_name>', methods=['DELETE'])
def delete_model(model_name):
    """
    删除模型
    """
    try:
        success = ModelService.delete_model(model_name)
        if not success:
            return jsonify({
                'success': False,
                'message': f'模型 {model_name} 不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '模型删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除模型失败: {str(e)}'
        }), 500

@bp.route('/api/models/summary', methods=['GET'])
def get_models_summary():
    """
    获取模型摘要信息
    """
    try:
        summary = ModelService.get_models_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型摘要失败: {str(e)}'
        }), 500

@bp.route('/api/models/chat', methods=['GET'])
def get_chat_models():
    """
    获取支持聊天的模型列表
    """
    try:
        models = ModelService.get_chat_models()
        return jsonify({
            'success': True,
            'data': [model.to_dict() for model in models]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取聊天模型列表失败: {str(e)}'
        }), 500

@bp.route('/api/models/completion', methods=['GET'])
def get_completion_models():
    """
    获取支持文本完成的模型列表
    """
    try:
        models = ModelService.get_completion_models()
        return jsonify({
            'success': True,
            'data': [model.to_dict() for model in models]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取文本完成模型列表失败: {str(e)}'
        }), 500