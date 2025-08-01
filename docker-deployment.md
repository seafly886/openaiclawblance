# Docker部署说明

## 快速开始

### 使用Docker Compose（推荐）

1. 确保已安装Docker和Docker Compose
2. 克隆项目代码
3. 在项目根目录下运行：

```bash
docker-compose up -d
```

这将构建镜像并启动容器。应用将在 http://localhost:5000 上运行。

### 使用Docker命令

1. 构建镜像：

```bash
docker build -t openai-proxy .
```

2. 运行容器：

```bash
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name openai-proxy openai-proxy
```

## 配置

### 环境变量

可以通过环境变量配置应用：

```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_ENV=production \
  -e OPENAI_API_BASE_URL=https://api.openai.com/v1 \
  --name openai-proxy \
  openai-proxy
```

### 数据持久化

默认情况下，SQLite数据库文件存储在容器内的 `/app/data` 目录。为了持久化数据，建议将主机目录挂载到容器：

```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name openai-proxy \
  openai-proxy
```

## 健康检查

应用包含健康检查端点 `/health`，Docker Compose配置中已包含健康检查。

## 日志

查看容器日志：

```bash
docker logs openai-proxy
```

实时查看日志：

```bash
docker logs -f openai-proxy
```

## 停止和删除容器

停止容器：

```bash
docker stop openai-proxy
```

删除容器：

```bash
docker rm openai-proxy
```

使用Docker Compose：

```bash
docker-compose down
```

## 更新应用

当有新的代码更新时，重新构建镜像并运行：

```bash
docker-compose build
docker-compose up -d
```

## 故障排除

### 容器启动失败

1. 检查容器日志：

```bash
docker logs openai-proxy
```

2. 确保端口5000未被占用：

```bash
netstat -tulpn | grep :5000
```

### 数据库问题

如果数据库文件损坏，可以删除数据目录并重新启动容器：

```bash
rm -rf data/*
docker-compose restart
```

### 权限问题

确保数据目录有正确的权限：

```bash
mkdir -p data
chmod 755 data
```

## 生产环境建议

1. 使用反向代理（如Nginx）处理HTTPS和静态文件
2. 设置环境变量 `FLASK_ENV=production`
3. 使用外部数据库（如PostgreSQL）替代SQLite
4. 配置日志轮转
5. 设置资源限制

## 反向代理配置

可以使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://openai-proxy:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /app/static;
        expires 30d;
    }
}
```

然后更新docker-compose.yml以包含Nginx服务。