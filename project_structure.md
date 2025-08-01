# OpenAI代理服务项目结构

## 目录结构

```
openai-proxy-service/
├── app/
│   ├── __init__.py                 # Flask应用初始化
│   ├── config.py                   # 应用配置
│   ├── models/                     # 数据库模型
│   │   ├── __init__.py
│   │   ├── key.py                  # Key模型
│   │   ├── usage_stats.py          # 使用统计模型
│   │   ├── model.py                # 模型信息
│   │   └── chat_history.py         # 聊天历史记录
│   ├── routes/                     # 路由控制器
│   │   ├── __init__.py
│   │   ├── key_routes.py           # Key管理路由
│   │   ├── model_routes.py         # 模型管理路由
│   │   ├── chat_routes.py          # 聊天功能路由
│   │   └── stats_routes.py         # 统计数据路由
│   ├── services/                   # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── key_service.py          # Key管理服务
│   │   ├── openai_service.py       # OpenAI API服务
│   │   ├── stats_service.py        # 统计服务
│   │   └── model_service.py        # 模型服务
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   ├── key_rotation.py         # Key轮询工具
│   │   ├── database.py             # 数据库连接工具
│   │   └── helpers.py              # 通用辅助函数
│   └── static/                     # 静态文件
│       ├── css/
│       │   ├── style.css           # 主样式文件
│       │   ├── key_management.css  # Key管理页面样式
│       │   ├── stats.css           # 统计页面样式
│       │   └── model_management.css # 模型管理页面样式
│       ├── js/
│       │   ├── main.js             # 主JavaScript文件
│       │   ├── key_management.js    # Key管理页面脚本
│       │   ├── stats.js            # 统计页面脚本
│       │   └── model_management.js # 模型管理页面脚本
│       └── images/                 # 图片资源
│           └── favicon.ico
├── templates/                       # HTML模板
│   ├── base.html                   # 基础模板
│   ├── index.html                  # 首页
│   ├── key_management.html         # Key管理页面
│   ├── stats.html                  # 统计页面
│   └── model_management.html       # 模型管理页面
├── requirements.txt                # Python依赖
├── Dockerfile                      # Docker配置文件
├── docker-compose.yml              # Docker Compose配置（可选）
├── .env                            # 环境变量
├── .gitignore                      # Git忽略文件
├── README.md                       # 项目说明文档
└── run.py                          # 应用启动文件
```

## 文件说明

### 应用核心文件

- **`app/__init__.py`**: Flask应用初始化文件，包含应用实例创建和配置
- **`app/config.py`**: 应用配置文件，包含数据库配置、OpenAI API配置等
- **`run.py`**: 应用启动文件，用于启动Flask应用

### 数据模型

- **`app/models/key.py`**: 定义Key数据模型，包含Key的基本信息和状态
- **`app/models/usage_stats.py`**: 定义使用统计数据模型，记录Key的使用情况
- **`app/models/model.py`**: 定义模型信息数据模型，存储OpenAI模型信息
- **`app/models/chat_history.py`**: 定义聊天历史记录模型，存储聊天请求和响应

### 路由控制器

- **`app/routes/key_routes.py`**: Key管理相关路由，处理Key的增删查改请求
- **`app/routes/model_routes.py`**: 模型管理相关路由，处理模型列表和模型信息请求
- **`app/routes/chat_routes.py`**: 聊天功能相关路由，处理聊天请求和响应
- **`app/routes/stats_routes.py`**: 统计数据相关路由，处理使用统计和监控数据请求

### 业务逻辑服务

- **`app/services/key_service.py`**: Key管理业务逻辑，处理Key的增删查改操作
- **`app/services/openai_service.py`**: OpenAI API服务，处理与OpenAI API的交互
- **`app/services/stats_service.py`**: 统计服务，处理使用统计数据的生成和查询
- **`app/services/model_service.py`**: 模型服务，处理模型信息的获取和管理

### 工具函数

- **`app/utils/key_rotation.py`**: Key轮询工具，实现Key的轮询选择算法
- **`app/utils/database.py`**: 数据库连接工具，处理数据库连接和会话管理
- **`app/utils/helpers.py`**: 通用辅助函数，包含各种工具函数

### 前端文件

- **`templates/base.html`**: 基础HTML模板，包含导航栏和公共部分
- **`templates/index.html`**: 首页模板，展示系统概览和主要功能入口
- **`templates/key_management.html`**: Key管理页面模板，包含Key的增删查改界面
- **`templates/stats.html`**: 统计页面模板，展示Key使用情况和统计图表
- **`templates/model_management.html`**: 模型管理页面模板，展示模型列表和聊天功能

### 静态资源

- **`app/static/css/`**: CSS样式文件，包含各页面的样式定义
- **`app/static/js/`**: JavaScript文件，包含各页面的交互逻辑
- **`app/static/images/`**: 图片资源，包含图标和其他图片

### 配置和部署文件

- **`requirements.txt`**: Python依赖文件，列出项目所需的Python包
- **`Dockerfile`**: Docker配置文件，定义容器构建规则
- **`docker-compose.yml`**: Docker Compose配置文件，用于多容器部署（可选）
- **`.env`**: 环境变量文件，存储敏感信息和配置
- **`.gitignore`**: Git忽略文件，指定不需要版本控制的文件和目录
- **`README.md`**: 项目说明文档，包含项目介绍、安装和使用说明

## 数据库表结构

### Keys表
```sql
CREATE TABLE keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_value TEXT NOT NULL UNIQUE,
    name TEXT,
    status TEXT DEFAULT 'active',  -- active, inactive, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);
```

### Usage Stats表
```sql
CREATE TABLE usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER,
    model TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    total_tokens INTEGER DEFAULT 0,
    FOREIGN KEY (key_id) REFERENCES keys (id)
);
```

### Models表
```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL UNIQUE,
    description TEXT,
    capabilities TEXT,  -- JSON格式存储模型能力
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat History表
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER,
    model TEXT,
    request TEXT,  -- JSON格式存储请求内容
    response TEXT,  -- JSON格式存储响应内容
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER DEFAULT 0,
    FOREIGN KEY (key_id) REFERENCES keys (id)
);
```

## API接口设计

### Key管理接口
- `GET /api/keys` - 获取所有Key列表
- `POST /api/keys` - 添加新Key
- `PUT /api/keys/<id>` - 更新Key信息
- `DELETE /api/keys/<id>` - 删除Key
- `GET /api/keys/<id>/stats` - 获取Key使用统计

### 模型管理接口
- `GET /api/models` - 获取模型列表
- `GET /api/models/<model_name>` - 获取特定模型信息
- `GET /api/models/<model_name>/stats` - 获取模型使用统计

### 聊天接口
- `POST /api/chat` - 发送聊天请求
- `GET /api/chat/history` - 获取聊天历史

### 统计接口
- `GET /api/stats/overview` - 获取系统概览统计
- `GET /api/stats/usage` - 获取使用统计
- `GET /api/stats/keys` - 获取Key统计
- `GET /api/stats/models` - 获取模型统计