# 更新日志

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

## [未发布]

### 新增
- 初始版本开发

## [1.0.0] - 2025-08-01

### 新增
- 完整的OpenAI代理服务功能
- Key管理系统（增删查改、测试）
- Key轮询机制（轮询、随机、最少使用策略）
- 模型管理系统（从OpenAI API获取、手动添加编辑）
- 聊天功能（与OpenAI模型交互）
- 统计分析功能（Key和模型使用情况、图表展示）
- Web界面（响应式设计、直观操作）
- Docker部署支持
- 完整的API文档

### 技术栈
- 后端：Python 3.10, Flask, SQLAlchemy
- 前端：HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- 数据库：SQLite
- 部署：Docker, Docker Compose

### 文档
- README.md：项目介绍和使用说明
- docker-deployment.md：Docker部署指南
- API文档：所有API接口的详细说明
- 开发指南：项目结构和开发流程