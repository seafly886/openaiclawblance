"""
Key管理路由
"""

from flask import Blueprint, request, jsonify
from app.services.key_service import KeyService

# 创建蓝图
bp = Blueprint('key_routes', __name__)

@bp.route('/api/keys', methods=['GET'])
def get_keys():
    """
    获取所有Key列表
    """
    try:
        keys = KeyService.get_all_keys()
        return jsonify({
            'success': True,
            'data': [key.to_dict() for key in keys]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取Key列表失败: {str(e)}'
        }), 500

@bp.route('/api/keys/<int:key_id>', methods=['GET'])
def get_key(key_id):
    """
    获取特定Key信息
    """
    try:
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return jsonify({
                'success': False,
                'message': 'Key不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': key.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取Key信息失败: {str(e)}'
        }), 500

@bp.route('/api/keys', methods=['POST'])
def create_key():
    """
    创建新Key
    """
    try:
        data = request.get_json()
        
        if not data or 'key_value' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: key_value'
            }), 400
        
        try:
            new_key = KeyService.create_key(
                key_value=data['key_value'],
                name=data.get('name', ''),
                status=data.get('status', 'active')
            )
            
            return jsonify({
                'success': True,
                'message': 'Key创建成功',
                'data': new_key.to_dict()
            }), 201
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建Key失败: {str(e)}'
        }), 500

@bp.route('/api/keys/<int:key_id>', methods=['PUT'])
def update_key(key_id):
    """
    更新Key信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '缺少更新数据'
            }), 400
        
        updated_key = KeyService.update_key(key_id, **data)
        if not updated_key:
            return jsonify({
                'success': False,
                'message': 'Key不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Key更新成功',
            'data': updated_key.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新Key失败: {str(e)}'
        }), 500

@bp.route('/api/keys/<int:key_id>', methods=['DELETE'])
def delete_key(key_id):
    """
    删除Key
    """
    try:
        success = KeyService.delete_key(key_id)
        if not success:
            return jsonify({
                'success': False,
                'message': 'Key不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Key删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除Key失败: {str(e)}'
        }), 500

@bp.route('/api/keys/<int:key_id>/stats', methods=['GET'])
def get_key_stats(key_id):
    """
    获取Key使用统计
    """
    try:
        stats = KeyService.get_key_stats(key_id)
        if not stats:
            return jsonify({
                'success': False,
                'message': 'Key不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取Key统计失败: {str(e)}'
        }), 500

@bp.route('/api/keys/<int:key_id>/test', methods=['POST'])
def test_key(key_id):
    """
    测试Key是否有效
    """
    try:
        test_result = KeyService.test_key(key_id)
        return jsonify({
            'success': True,
            'data': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试Key失败: {str(e)}'
        }), 500

@bp.route('/api/keys/summary', methods=['GET'])
def get_keys_summary():
    """
    获取Keys摘要信息
    """
    try:
        summary = KeyService.get_keys_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取Keys摘要失败: {str(e)}'
        }), 500