# Coze Studio 0.2.0 部署所需的完整Docker镜像列表 
 # 从 docker-compose.yml 中提取，包含所有服务的镜像配置 
 
 ## 核心服务镜像 
 1. MySQL 数据库 
    - 镜像: docker.io/library/mysql:8.4.5 
    - 容器名: coze-mysql 
 
 2. Redis 缓存 
    - 镜像: docker.io/library/redis:8.0 
    - 容器名: coze-redis 
 
 3. Elasticsearch 搜索引擎 
    - 镜像: docker.io/library/elasticsearch:8.18.0 
    - 容器名: coze-elasticsearch 
 
 4. MinIO 对象存储 
    - 镜像: docker.io/minio/minio:RELEASE.2025-06-13T11-33-47Z-cpuv1 
    - 容器名: coze-minio 
 
 5. Etcd 分布式键值存储 
    - 镜像: docker.io/bitnami/etcd:3.5 
    - 容器名: coze-etcd 
 
 6. Milvus 向量数据库 
    - 镜像: docker.io/milvusdb/milvus:v2.5.10 
    - 容器名: coze-milvus 
 
 7. NSQ 消息队列 (3个服务) 
    - nsqlookupd: docker.io/nsqio/nsq:v1.2.1 (coze-nsqlookupd) 
    - nsqd: docker.io/nsqio/nsq:v1.2.1 (coze-nsqd) 
    - nsqadmin: docker.io/nsqio/nsq:v1.2.1 (coze-nsqadmin) 
 
 8. Coze Server 核心服务 
    - 镜像: docker.io/opencoze/opencoze:latest 
    - 容器名: coze-server 
 
 ## 初始化服务镜像 
 1. Elasticsearch 初始化 
    - 镜像: docker.io/library/alpine:latest 
    - 容器名: coze-elasticsearch-setup 
 
 2. MinIO 初始化 
    - 镜像: docker.io/minio/mc:latest 
    - 容器名: coze-minio-setup 
 
 3. MySQL 架构初始化 
    - 镜像: docker.io/arigaio/atlas:0.35.0-community-alpine 
    - 容器名: coze-mysql-setup-schema 
 
 4. MySQL 数据初始化 
    - 镜像: docker.io/library/mysql:8.4.5 
    - 容器名: coze-mysql-setup-init-sql 
 
 ## 镜像拉取命令 
 # 可以使用以下命令预拉取所有镜像： 
 docker pull docker.io/library/mysql:8.4.5 
 docker pull docker.io/library/redis:8.0 
 docker pull docker.io/library/elasticsearch:8.18.0 
 docker pull docker.io/minio/minio:RELEASE.2025-06-13T11-33-47Z-cpuv1 
 docker pull docker.io/bitnami/etcd:3.5 
 docker pull docker.io/milvusdb/milvus:v2.5.10 
 docker pull docker.io/nsqio/nsq:v1.2.1 
 docker pull docker.io/library/alpine:latest 
 docker pull docker.io/minio/mc:latest 
 docker pull docker.io/arigaio/atlas:0.35.0-community-alpine 
 docker pull docker.io/opencoze/opencoze:latest