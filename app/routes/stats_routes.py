"""
统计数据路由
"""

from flask import Blueprint, request, jsonify
from app.services.stats_service import StatsService
from app.utils.auth import login_required

# 创建蓝图
bp = Blueprint('stats_routes', __name__)

@bp.route('/api/stats/overview', methods=['GET'])
@login_required
def get_overview_stats():
    """
    获取系统概览统计
    """
    try:
        stats = StatsService.get_overview_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取系统概览统计失败: {str(e)}'
        }), 500

@bp.route('/api/stats/usage', methods=['GET'])
@login_required
def get_usage_stats():
    """
    获取使用统计
    """
    try:
        # 获取查询参数
        period = request.args.get('period', 'all')  # all, daily, weekly, monthly
        
        stats = StatsService.get_usage_stats(period)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取使用统计失败: {str(e)}'
        }), 500

@bp.route('/api/stats/keys', methods=['GET'])
@login_required
def get_key_stats():
    """
    获取Key统计
    """
    try:
        # 获取查询参数
        key_id = request.args.get('key_id', type=int)
        
        if key_id:
            # 获取特定Key的统计
            stats = StatsService.get_key_stats(key_id)
            if not stats:
                return jsonify({
                    'success': False,
                    'message': 'Key不存在'
                }), 404
        else:
            # 获取所有Key的统计信息
            from app.models.key import Key
            keys = Key.query.all()
            stats = []
            for key in keys:
                key_stat = StatsService.get_key_stats(key.id)
                if key_stat:
                    stats.append(key_stat)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取Key统计失败: {str(e)}'
        }), 500

@bp.route('/api/stats/models', methods=['GET'])
@login_required
def get_model_stats():
    """
    获取模型统计
    """
    try:
        # 获取查询参数
        model_name = request.args.get('model_name')
        
        if model_name:
            # 获取特定模型的统计
            stats = StatsService.get_model_stats(model_name)
            if not stats:
                return jsonify({
                    'success': False,
                    'message': '模型不存在'
                }), 404
        else:
            # 获取所有模型的统计信息
            from app.models.model import Model
            models = Model.query.all()
            stats = []
            for model in models:
                model_stat = StatsService.get_model_stats(model.model_name)
                if model_stat:
                    stats.append(model_stat)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型统计失败: {str(e)}'
        }), 500

@bp.route('/api/stats/hourly', methods=['GET'])
@login_required
def get_hourly_stats():
    """
    获取每小时使用统计
    """
    try:
        # 获取查询参数
        hours = request.args.get('hours', 24, type=int)
        
        stats = StatsService.get_hourly_usage(hours)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取每小时使用统计失败: {str(e)}'
        }), 500