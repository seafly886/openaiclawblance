# 心跳检测功能说明

## 概述

心跳检测功能是为主程序增加的自动监控和修复机制，当检测到后端服务或管理页面不可用时可以自动修复重启。该功能定期检查关键服务的健康状态，并在检测到问题时采取相应的修复措施。

## 功能特性

### 1. 服务监控
监控以下关键服务和页面：
- 主服务健康检查端点 (`/health`)
- 管理登录页面 (`/login`)

### 2. 健康检查
- **基础健康检查**: 通过 `/health` 端点提供简单的服务状态
- **详细健康检查**: 通过 `/health/detailed` 端点提供所有服务的详细状态
- **特定服务检查**: 通过 `/health/service/{service_name}` 端点检查特定服务的状态

### 3. 自动修复机制
- **智能故障诊断**: 根据不同的服务类型采取不同的修复策略
- **分级修复**: 从配置检查到服务重启的多级修复方案
- **冷却机制**: 避免频繁重启，设置重启冷却时间
- **失败计数**: 记录失败次数，达到阈值才触发修复

### 4. 管理接口
- **启动/停止**: 可以通过API接口控制心跳检测服务的启停
- **状态查询**: 可以查询心跳检测服务的运行状态和配置
- **实时监控**: 提供实时的服务状态监控

## 配置参数

可以通过环境变量或配置文件配置心跳检测功能：

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| `HEARTBEAT_ENABLED` | `True` | 是否启用心跳检测功能 |
| `HEARTBEAT_CHECK_INTERVAL` | `30` | 心跳检测间隔（秒） |
| `HEARTBEAT_MAX_RETRIES` | `3` | 最大重试次数 |
| `HEARTBEAT_RESTART_COOLDOWN` | `300` | 重启冷却时间（秒） |
| `HEARTBEAT_AUTO_START` | `True` | 是否自动启动心跳检测 |

## 使用方法

### 1. 启动应用

应用启动时会自动启用心跳检测服务（如果配置为自动启动）：

```bash
python app/main.py
```

### 2. 查看服务状态

#### 基础健康检查
```bash
curl http://localhost:5000/health
```

#### 详细健康检查
```bash
curl http://localhost:5000/health/detailed
```

#### 特定服务检查
```bash
curl http://localhost:5000/health/service/main_service
```

### 3. 管理心跳检测服务

#### 获取心跳检测状态
```bash
curl http://localhost:5000/admin/heartbeat/status
```

#### 启动心跳检测
```bash
curl -X POST http://localhost:5000/admin/heartbeat/start
```

#### 停止心跳检测
```bash
curl -X POST http://localhost:5000/admin/heartbeat/stop
```

## 测试功能

使用提供的测试脚本验证心跳检测功能：

```bash
python test_heartbeat.py
```

测试脚本会自动验证以下功能：
- 基础健康检查
- 详细健康检查
- 特定服务健康检查
- 心跳检测控制
- 登录页面可用性

## 故障处理

### 1. 常见问题

#### 心跳检测服务无法启动
- 检查 `HEARTBEAT_ENABLED` 配置是否为 `True`
- 检查端口是否被占用
- 查看日志文件获取详细错误信息

#### 服务频繁重启
- 检查 `HEARTBEAT_RESTART_COOLDOWN` 配置，适当增加冷却时间
- 检查 `HEARTBEAT_MAX_RETRIES` 配置，适当增加重试次数
- 检查网络连接和依赖服务状态

#### 健康检查失败
- 检查服务是否正常运行
- 检查防火墙设置
- 检查数据库连接状态

### 2. 日志分析

心跳检测功能会产生详细的日志信息，包括：
- 服务检查结果
- 故障诊断过程
- 修复操作记录
- 重启事件记录

可以通过查看应用日志了解心跳检测的运行状态。

## 扩展功能

### 1. 添加新的监控服务

在 `app/services/heartbeat_service.py` 中的 `monitored_services` 字典中添加新的服务：

```python
self.monitored_services = {
    # 现有服务...
    'new_service': {
        'url': 'http://localhost:{port}/new/service',
        'description': '新服务描述',
        'critical': True  # 是否为关键服务
    }
}
```

### 2. 自定义修复策略

在 `app/services/heartbeat_service.py` 中添加自定义的修复方法：

```python
def _repair_new_service(self):
    """自定义修复策略"""
    # 实现修复逻辑
    pass
```

并在 `_attempt_repair` 方法中添加相应的调用。

### 3. 添加通知机制

可以在修复失败或重启事件发生时添加通知功能，如邮件通知、短信通知等。

## 注意事项

1. **权限要求**: 心跳检测功能需要适当的系统权限来执行重启操作
2. **资源使用**: 心跳检测会占用一定的系统资源，请根据实际情况调整检测间隔
3. **网络依赖**: 心跳检测依赖于网络连接，请确保网络配置正确
4. **日志管理**: 心跳检测会产生大量日志，请配置适当的日志轮转策略

## 更新日志

### v1.0.0
- 初始版本，支持基础心跳检测功能
- 实现自动修复重启机制
- 提供管理接口和测试工具