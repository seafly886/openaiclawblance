"""
健康检查路由
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from app.services.heartbeat_service import heartbeat_service
from app.utils.auth import login_required

# 创建蓝图
bp = Blueprint('health_routes', __name__)

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
logger = logging.getLogger(__name__)

@bp.route('/health')
def basic_health_check():
    """
    基础健康检查端点
    """
    try:
        # 返回简单的健康状态
        return jsonify({
            'status': 'healthy',
            'message': 'OpenAI代理服务运行正常',
            'timestamp': datetime.now().isoformat(),
            'uptime': _get_uptime()
        })
    except Exception as e:
        logger.error(f"基础健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': f'健康检查失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/health/detailed')
@login_required
def detailed_health_check():
    """
    详细健康检查端点
    """
    try:
        # 获取所有服务的状态
        service_status = heartbeat_service.get_service_status()
        
        # 检查整体健康状态
        all_healthy = all(status['healthy'] for status in service_status.values())
        critical_services_healthy = all(
            status['healthy'] for status in service_status.values() 
            if status['critical']
        )
        
        # 构建响应
        response = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'critical_services_healthy': critical_services_healthy,
            'timestamp': datetime.now().isoformat(),
            'uptime': _get_uptime(),
            'services': service_status,
            'summary': {
                'total_services': len(service_status),
                'healthy_services': sum(1 for status in service_status.values() if status['healthy']),
                'unhealthy_services': sum(1 for status in service_status.values() if not status['healthy']),
                'critical_services': sum(1 for status in service_status.values() if status['critical']),
                'critical_unhealthy_services': sum(
                    1 for status in service_status.values() 
                    if not status['healthy'] and status['critical']
                )
            }
        }
        
        # 设置适当的HTTP状态码
        status_code = 200 if all_healthy else 503
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"详细健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': f'详细健康检查失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/health/service/<service_name>')
@login_required
def service_health_check(service_name):
    """
    检查特定服务的健康状态
    
    Args:
        service_name: 服务名称
    """
    try:
        # 获取服务状态
        service_status = heartbeat_service.get_service_status()
        
        if service_name not in service_status:
            return jsonify({
                'status': 'error',
                'message': f'未知的服务: {service_name}',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        service_info = service_status[service_name]
        
        # 构建响应
        response = {
            'service_name': service_name,
            'status': 'healthy' if service_info['healthy'] else 'unhealthy',
            'description': service_info['description'],
            'response_time': service_info['response_time'],
            'critical': service_info['critical'],
            'failure_count': service_info['failure_count'],
            'last_failure': service_info['last_failure'],
            'timestamp': datetime.now().isoformat()
        }
        
        # 设置适当的HTTP状态码
        status_code = 200 if service_info['healthy'] else 503
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"服务 {service_name} 健康检查失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'服务 {service_name} 健康检查失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/admin/heartbeat/start', methods=['POST'])
@login_required
def start_heartbeat():
    """
    启动心跳检测服务
    """
    try:
        success = heartbeat_service.start()
        if success:
            return jsonify({
                'success': True,
                'message': '心跳检测服务已启动',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '心跳检测服务已禁用或已在运行中',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        logger.error(f"启动心跳检测服务失败: {e}")
        return jsonify({
            'success': False,
            'message': f'启动心跳检测服务失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/admin/heartbeat/stop', methods=['POST'])
@login_required
def stop_heartbeat():
    """
    停止心跳检测服务
    """
    try:
        heartbeat_service.stop()
        return jsonify({
            'success': True,
            'message': '心跳检测服务已停止',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"停止心跳检测服务失败: {e}")
        return jsonify({
            'success': False,
            'message': f'停止心跳检测服务失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/admin/heartbeat/status')
@login_required
def heartbeat_status():
    """
    获取心跳检测服务状态
    """
    try:
        # 获取所有服务的状态
        service_status = heartbeat_service.get_service_status()
        
        # 构建响应
        response = {
            'heartbeat_enabled': heartbeat_service.enabled,
            'heartbeat_running': heartbeat_service.is_running,
            'auto_start': heartbeat_service.auto_start,
            'check_interval': heartbeat_service.check_interval,
            'max_retries': heartbeat_service.max_retries,
            'restart_cooldown': heartbeat_service.restart_cooldown,
            'services': service_status,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取心跳检测服务状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取心跳检测服务状态失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

def _get_uptime():
    """
    获取服务运行时间
    
    Returns:
        str: 格式化的运行时间
    """
    try:
        # 获取进程启动时间
        import psutil
        process = psutil.Process()
        create_time = process.create_time()
        uptime_seconds = datetime.now().timestamp() - create_time
        
        # 格式化运行时间
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟"
        elif hours > 0:
            return f"{int(hours)}小时 {int(minutes)}分钟"
        elif minutes > 0:
            return f"{int(minutes)}分钟 {int(seconds)}秒"
        else:
            return f"{int(seconds)}秒"
            
    except Exception as e:
        logger.error(f"获取运行时间失败: {e}")
        return "未知"