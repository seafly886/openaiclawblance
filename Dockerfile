# 使用Python 3.10作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 创建数据目录并设置权限
RUN mkdir -p /data && chmod 777 /data

# 安装系统依赖
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
# 复制所需文件到容器中
COPY ./requirements.txt /app

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY ./app /app/app

# 创建非root用户
# RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# USER appuser

# 暴露端口
EXPOSE 5000

# 声明数据卷
VOLUME ["/data"]

# 设置环境变量
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:////data/app.db

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]