---
name: 可执行命令校验
description: 教程里的命令必须复制即执行。写作与交付前按本清单核对占位符、环境错配、伪命令与前置条件。
---

# 可执行命令校验

教程里的命令是读者最先照做的东西。一条跑不通的命令，会让人怀疑整篇教程。下面七条是踩过的坑，写的时候逐条对照，交付前再扫一遍。

## 1. 不留占位符

可复制执行的代码块里，不允许出现 `...`、`xxx`、`<your-topic>` 这类省略。

**反例**

```bash
docker run -d --name kafka1 -e KAFKA_NODE_ID=1 ... apache/kafka:4.3.2
```

**正例**：参数写全；确实需要读者替换的，用注释点名替换位置。

```bash
# 9092 被旧容器占用时改成 9093，并同步修改 advertised 地址
docker run -d --name kafka -p 9093:9092 apache/kafka:4.3.2
```

同一个配置重复三遍（三节点集群）时也要写全，不要写「其余同上」——读者复制的是单条命令，不是上下文。

## 2. 单机示例不能要求集群能力

单节点环境里不能出现需要多副本、多节点的命令。

| 技术 | 单机环境 | 多节点才可用 |
|---|---|---|
| Kafka | `--replication-factor 1` | `--replication-factor 3` |
| Elasticsearch | `number_of_replicas: 0` | `number_of_replicas: >= 1` |
| Redis | 单实例 `redis-server` | `redis-cli --cluster create ...` |
| MongoDB | 单机 `mongod` | `rs.initiate()` |

**为什么**：Kafka 单节点写 3 副本会直接报 `Replication factor: 3 larger than available brokers: 1`，命令当场失败。多副本命令要么先给出多节点搭建步骤，要么明确标注「以下命令需要三节点集群」。

## 3. 连接地址要匹配执行位置

同一条客户端命令，在宿主机和容器里指向不同地址。

| 部署 | 命令在哪执行 | 该用的地址 |
|---|---|---|
| 单节点 Docker，宿主机端口与容器端口一致 | 宿主机 / 容器内 | 两边都可以 `localhost:9092` |
| 多节点 Docker，宿主机端口各不相同 | 容器内（`docker exec`） | 容器网络内部地址，如 `kafka1:9094` |
| 多节点 Docker，宿主机端口各不相同 | 宿主机客户端 | 映射后的地址，如 `localhost:9092,localhost:9093,localhost:9094` |

**为什么**：客户端第一次连的是 bootstrap 地址，之后 Broker 返回的是 `advertised.listeners` 里的地址。容器里没有宿主机的映射端口，用错会报 `Timed out waiting for a node assignment`，看起来像集群坏了。

## 4. 每节点不同的配置要逐台改

`node.id`、`advertised.listeners`、`broker.rack` 这类值，必须在注释里写明「每台改成自己的」。

三台都照抄 `kafka1` 的 `advertised.listeners`，客户端会全部被引到第一台，负载均衡形同虚设，这台挂了整个集群对外不可用。

## 5. 命令与部署方式必须一致

- 二进制部署章节：用 `bin/kafka-server-start.sh`、`bin/kafka-server-stop.sh`
- Docker 部署章节：用 `docker run`、`docker stop`

不能在二进制部署章节里突然出现 `docker stop kafka2`。两种方式都要讲时，分成两段并标注适用场景，不要让读者猜自己属于哪一种。

## 6. 禁止伪命令

- **不存在的入口**：Kafka 没有 `kafka.jar`，不能 `java -jar` 启动；JMX agent 要通过 `KAFKA_OPTS` 挂到启动脚本上。
- **未定义的变量**：`$KAFKA_BIN`、`$BOOTSTRAP` 必须在第一次使用前赋值。
- **示例 ID 当参数**：`cluster-id`、`token`、`topic-id` 要提示「换成上一步的输出」。
- **容器连宿主机服务**：用 `host.docker.internal`（macOS / Windows），不要用只在宿主机 `/etc/hosts` 里存在的主机名。

## 7. 前置条件写在命令旁边

- 多节点用主机名：说明 `kafka1/2/3` 要写入 `/etc/hosts` 或内网 DNS。
- 端口可能被占用：说明先停掉旧容器（`docker stop kafka && docker rm kafka`）。
- 需要特定 JDK、管理员权限、较大镜像体积的：在命令前一句交代，不要等读者执行失败再解释。

## 交付前自检

对每个 `bash` 代码块问四个问题：

1. 复制到干净终端，缺不缺参数？
2. 当前章节的环境（宿主机 / 单节点容器 / 多节点集群）能跑通吗？
3. 地址、端口、副本数、主机名是否与这一章的环境一致？
4. 有没有依赖上一步输出、却没说明要替换的值？

能实测的尽量实测（Docker、kubectl、CLI 工具），本地跑一遍再交付。不能实测的（付费云服务、生产专属工具），在命令旁标注前置条件与预期输出。

## 要点

- 命令块是教程的可执行契约，占位符等于违约
- 环境声明（宿主机 / 容器内 / 集群）要和地址、副本数一起核对
- 写完先跑脚本扫占位符，再人工过一遍上面四个问题
