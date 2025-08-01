# OpenAI代理服务

一个用于管理多个OpenAI API Key并提供统一代理服务的Web应用。

## 功能特点

- **Key管理**：添加、编辑、删除和测试OpenAI API Key
- **Key轮询**：支持多种Key轮询策略（轮询、随机、最少使用）
- **模型管理**：从OpenAI API自动获取模型列表，支持手动添加和编辑模型
- **聊天功能**：提供简单的聊天界面，支持与OpenAI模型交互
- **统计分析**：提供Key和模型使用情况的详细统计和图表展示
- **Web界面**：直观的Web界面，方便管理和监控

## 技术栈

- **后端**：Python 3.10, Flask, SQLAlchemy
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **数据库**：SQLite
- **部署**：Docker, Docker Compose

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装步骤

1. 克隆项目代码：

```bash
git clone https://github.com/yourusername/openai-proxy.git
cd openai-proxy
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 初始化数据库：

```bash
python -c "from app import db; db.create_all()"
```

5. 启动应用：

```bash
python run.py
```

6. 访问 http://localhost:5000

## Docker部署

### 使用Docker Compose（推荐）

1. 确保已安装Docker和Docker Compose
2. 在项目根目录下运行：

```bash
docker-compose up -d
```

3. 访问 http://localhost:5000

详细部署说明请参考 [docker-deployment.md](docker-deployment.md)。

## 配置

### 环境变量

可以通过环境变量配置应用：

```bash
export FLASK_ENV=production
export OPENAI_API_BASE_URL=https://api.openai.com/v1
export SECRET_KEY=your-secret-key
```

### 配置文件

配置文件位于 `app/config.py`，可以根据需要修改：

```python
class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/openai_proxy.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API配置
    OPENAI_API_BASE_URL = 'https://api.openai.com/v1'
    
    # Key轮询策略
    KEY_ROTATION_STRATEGY = 'round_robin'  # round_robin, random, least_used
    
    # 应用配置
    SECRET_KEY = 'your-secret-key'
    DEBUG = False
```

## API文档

### Key管理

#### 获取所有Key

```
GET /api/keys
```

#### 添加Key

```
POST /api/keys
Content-Type: application/json

{
    "name": "Key 1",
    "key_value": "sk-...",
    "status": "active"
}
```

#### 更新Key

```
PUT /api/keys/{key_id}
Content-Type: application/json

{
    "name": "Key 1",
    "key_value": "sk-...",
    "status": "active"
}
```

#### 删除Key

```
DELETE /api/keys/{key_id}
```

#### 测试Key

```
POST /api/keys/{key_id}/test
```

### 模型管理

#### 获取所有模型

```
GET /api/models
```

#### 刷新模型列表

```
GET /api/models?refresh=true
```

#### 添加模型

```
POST /api/models
Content-Type: application/json

{
    "model_name": "gpt-3.5-turbo",
    "description": "GPT-3.5 Turbo",
    "capabilities": "{}"
}
```

#### 更新模型

```
PUT /api/models/{model_name}
Content-Type: application/json

{
    "description": "GPT-3.5 Turbo",
    "capabilities": "{}"
}
```

#### 删除模型

```
DELETE /api/models/{model_name}
```

### 聊天功能

#### 发送聊天请求

```
POST /api/chat
Content-Type: application/json

{
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Hello, world!"}
    ]
}
```

#### 获取聊天历史

```
GET /api/chat/history?limit=10
```

### 统计分析

#### 获取系统概览统计

```
GET /api/stats/overview
```

#### 获取使用统计

```
GET /api/stats/usage?period=all
```

#### 获取Key统计

```
GET /api/stats/keys?key_id=1
```

#### 获取模型统计

```
GET /api/stats/models?model_name=gpt-3.5-turbo
```

#### 获取每小时使用趋势

```
GET /api/stats/hourly?hours=24
```

## 开发指南

### 项目结构

```
openai-proxy/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── config.py            # 配置文件
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── key.py           # Key模型
│   │   ├── model.py         # 模型模型
│   │   ├── usage_stats.py   # 使用统计模型
│   │   └── chat_history.py  # 聊天历史模型
│   ├── routes/              # 路由
│   │   ├── __init__.py
│   │   ├── key_routes.py    # Key管理路由
│   │   ├── model_routes.py  # 模型管理路由
│   │   ├── chat_routes.py   # 聊天路由
│   │   └── stats_routes.py  # 统计路由
│   ├── services/            # 服务
│   │   ├── __init__.py
│   │   ├── key_service.py   # Key服务
│   │   ├── model_service.py # 模型服务
│   │   ├── openai_service.py # OpenAI API服务
│   │   └── stats_service.py # 统计服务
│   ├── utils/               # 工具
│   │   ├── __init__.py
│   │   ├── database.py      # 数据库工具
│   │   └── key_rotation.py  # Key轮询工具
│   └── static/              # 静态文件
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── app.js
│       └── index.html
├── data/                    # 数据目录
├── requirements.txt        # Python依赖
├── run.py                  # 应用入口
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
└── README.md              # 项目说明
```

### 添加新功能

1. 在 `app/models/` 中添加数据模型
2. 在 `app/services/` 中添加服务逻辑
3. 在 `app/routes/` 中添加路由
4. 在 `app/static/js/app.js` 中添加前端交互逻辑
5. 在 `app/static/index.html` 中添加UI元素

### 数据库迁移

使用Flask-Migrate进行数据库迁移：

```bash
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 常见问题

### Q: 如何添加新的OpenAI API Key？

A: 在Web界面的"Key管理"页面，点击"添加Key"按钮，填写Key信息并保存。

### Q: 如何修改Key轮询策略？

A: 在 `app/config.py` 中修改 `KEY_ROTATION_STRATEGY` 配置，可选值有：`round_robin`（轮询）、`random`（随机）、`least_used`（最少使用）。

### Q: 如何自定义OpenAI API基础URL？

A: 在 `app/config.py` 中修改 `OPENAI_API_BASE_URL` 配置，或通过环境变量 `OPENAI_API_BASE_URL` 设置。

### Q: 如何备份数据？

A: 备份 `data/` 目录下的数据库文件即可。如果使用Docker部署，确保挂载了数据卷。

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue：[GitHub Issues](https://github.com/yourusername/openai-proxy/issues)
- 邮箱：your.email@example.com