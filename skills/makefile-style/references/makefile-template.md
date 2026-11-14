---
name: makefile-template
description: 可直接复制的 Makefile 骨架，含编号分类、总命令聚合、变量区与自动 help
---

# Makefile 模板

复制整段到项目根目录，删掉不需要的分类并重排序号。recipe 行是 Tab，不要转成空格。

骨架只演示结构，命令以 npm 为例；换成你的技术栈即可（`uv run`、`go build`、`cargo`、`mvn` 等），规则不变。

## 完整骨架

```makefile
# ============================================================
# myapp — 统一命令入口
# 用法: make <target>      列表: make help
# ============================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ---------- 可调参数 ----------
# 统一用 ?=，命令行可覆盖：make docker-up PORT=8080
# PKG 只是占位：npm / pnpm / yarn / bun 填包管理器，Python 同理换成 uv
PKG      ?= npm
APP_IMG  ?= myapp
APP_TAG  ?= latest
PORT     ?= 3000
DATA_DIR ?= ./data
COMPOSE  ?= docker compose

# ---------- 派生变量 ----------
# 终端输出颜色（printf %b 解释 \033；BSD echo 不解释转义，所以统一用 printf）
C_RESET := \033[0m
C_BOLD  := \033[1m
C_DIM   := \033[2m

# ---------- export ----------
# 变量名必须与上面的定义完全一致，否则子进程只会拿到空值
export PORT

# ============================================================
# 1. 依赖
# ============================================================
.PHONY: install update-deps

install: ## 安装依赖
	$(PKG) install

update-deps: ## 升级依赖
	$(PKG) update

# ============================================================
# 2. 本地开发
# ============================================================
.PHONY: dev serve

dev: ## 启动开发服务器 (http://localhost:3000)
	$(PKG) run dev

serve: build ## 构建后启动独立服务
	node apps/server/index.mjs

# ============================================================
# 3. 构建
# ============================================================
.PHONY: build build-lib build-app

build: build-lib build-app ## 构建全部 (库 + 应用)

build-lib: ## 构建库 (→ dist/)
	$(PKG) run build:lib

build-app: ## 构建应用 (→ dist-app/)
	$(PKG) run build:app

# ============================================================
# 4. 质量检查
# ============================================================
.PHONY: check lint typecheck test

check: lint typecheck test ## 提交前全套检查

lint: ## 代码风格检查
	$(PKG) run lint

typecheck: ## 类型检查
	$(PKG) run typecheck

test: ## 运行测试
	$(PKG) test

# ============================================================
# 5. 部署
# ============================================================
.PHONY: deploy

# 打包发布：与容器操作分章，避免 help 里两类命令混在一起
deploy: ## 打包产物并托管
	$(PKG) run build

# ============================================================
# 6. 容器
# ============================================================
.PHONY: docker-build docker-up docker-down docker-logs

# docker-build 即本章默认入口（完整流程），不必再写 docker: docker-build 这种纯转发别名

docker-build: ## 默认入口：拉取最新代码并构建部署镜像
	@echo ""
	@echo "  ⬇️  [1/2] 拉取最新代码"
	git pull
	@echo "  ✅ 代码已更新"
	@echo ""
	@echo "  🐳 [2/2] 构建镜像 $(APP_IMG):$(APP_TAG)"
	docker build -t $(APP_IMG):$(APP_TAG) .
	@echo ""
	@echo "  ✅ 镜像构建完成: $(APP_IMG):$(APP_TAG)"
	@echo "     下一步: make docker-up"
	@echo ""

docker-up: ## 后台启动容器
	$(COMPOSE) up -d --build
	@echo ""
	@echo "  ✅ 容器已在后台启动 (restart: unless-stopped)"
	@echo "     访问    : http://localhost:$(PORT)"
	@echo "     查看日志: make docker-logs"
	@echo "     停止容器: make docker-down"
	@echo ""

docker-down: ## 停止并移除容器
	$(COMPOSE) down
	@echo ""
	@echo "  🛑 容器已停止并移除"
	@echo "     重新启动: make docker-up"
	@echo ""

docker-logs: ## 跟踪容器日志
	docker logs -f $(APP_IMG)

# ============================================================
# 7. 清理
# ============================================================
.PHONY: clean clean-all

clean: ## 删除构建产物
	rm -rf dist dist-app

clean-all: clean ## 删除构建产物 + node_modules
	rm -rf node_modules

# ============================================================
# 8. 运维
# ============================================================
.PHONY: data-path data-init

data-path: ## 打印当前生效的数据目录
	@echo "数据目录: $(DATA_DIR)"

data-init: ## 创建数据目录（幂等）
	@mkdir -p $(DATA_DIR)

# ============================================================
# 9. 帮助
# ============================================================
.PHONY: help

help: ## 按分类显示所有命令
	@printf '%b\n' "  $(C_BOLD)myapp — 统一命令入口$(C_RESET)"
	@printf '%b\n' "  $(C_DIM)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(C_RESET)"
	@printf '%b\n' ""
	@awk 'BEGIN {FS = "## "} \
	  /^# [0-9]+\./ { sub(/^# [0-9]+\. /, ""); if (c++) printf "\n"; printf "  \033[1m%s\033[0m\n", $$0 } \
	  /^[a-zA-Z0-9_-]+:.*## ?/ { n=$$1; sub(/:.*/, "", n); printf "    \033[1;32m%-15s\033[0m%s\n", n, $$2 }' $(MAKEFILE_LIST)
	@printf '%b\n' ""
```

## 终端反馈写法

多步骤 target 的输出按「阶段开始 → 阶段结果 → 最终结果 + 下一步」组织：

```makefile
docker-build: ## 拉取最新代码并构建部署镜像
	@echo ""
	@echo "  ⬇️  [1/2] 拉取最新代码"
	git pull
	@echo "  ✅ 代码已更新"
	@echo ""
	@echo "  🐳 [2/2] 构建镜像 $(APP_IMG):$(APP_TAG)"
	docker build -t $(APP_IMG):$(APP_TAG) .
	@echo ""
	@echo "  ✅ 镜像构建完成: $(APP_IMG):$(APP_TAG)"
	@echo "     下一步: make docker-up"
	@echo ""
```

要点：

- 提示行用 `@echo`，`@` 抑制命令回显，终端只看到提示本身；要带颜色就用 `@printf '%b\n'`（BSD echo 不解释 `\033`）。
- 阶段编号 `[1/2]` 让人知道还要等多久；阶段结果紧跟对应命令之后。**增删阶段后同步所有编号**：追加第 4 步时，前三步要一起改成 `[1/4]`～`[3/4]`。
- 结束提示固定给「结果 + 关键值 + 下一步」，成对命令互相指路（`up` 提示 `down`，`down` 提示 `up`）。
- 提示整段前后各一个 `@echo ""`；关键值第二行缩进对齐。
- 前台常驻命令（`dev`、`serve`、`deploy`）要在提示里写明「前台运行，Ctrl+C 退出」。
- 失败提示不手写：命令非零退出时 make 自动中止并打印错误。

## 为什么不手写 help

`help` 用 awk 扫描 Makefile 自身，章节标题和行尾 `##` 就是目录的唯一来源：

- 新增命令时只改一行，help 自动出现，不会漏。
- `FS = "## "` 按行尾注释把描述切出来，`sub(/:.*/, "", n)` 再去掉 target 名后的冒号与依赖——带依赖的总命令（如 `build: a b ## ...`）也能正确取到 target 名。刻意不用 `.*?` 非贪婪：mawk（Debian/Ubuntu 默认 awk）不支持非贪婪，描述里出现第二个 `##` 会切错；本写法在 gawk / mawk / BSD awk / macOS awk 上行为一致。
- 匹配 target 的正则含数字 `[a-zA-Z0-9_-]+`，否则 `test-2` 这类命令会被漏掉。
- `^# [0-9]+\.` 负责打印分类标题，`sub` 去掉编号——编号只用于源文件排序定位，help 里只显示分类名。
- 分类之间用 `c++` 计数控制空行，第一个标题前不空行。

help 描述的两条铁律（违反就会在目录里出问题）：

- **必须写在 target 同一行的行尾**：target 上方的 `##` / `#` 只是普通注释，不会被提取。长说明放上方可以，但行尾仍要补一句简短描述。
- **不要写 `$(VAR)`**：awk 读的是 Makefile 原文，不会展开 make 变量，会原样显示 `$(PORT)`。变量值要在运行时 recipe 的 `@echo` 里输出。

## 输出形态

```text
  myapp — 统一命令入口
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  依赖
    install         安装依赖
    update-deps     升级依赖

  本地开发
    dev             启动开发服务器 (http://localhost:3000)
    serve           构建后启动独立服务

  容器
    docker          默认入口：更新并重建容器
    docker-build    拉取最新代码并构建部署镜像
    docker-up       后台启动容器
    docker-down     停止并移除容器
```

视觉层级固定为：标题粗体、下面一条暗色分隔线、分类名粗体无色、命令名加粗亮绿、描述默认色、分类之间空一行。末尾不加用法或变量覆盖提示。

## 检查清单

- [ ] `make help` 分组正确、分类名不带序号、名称与描述列对齐
- [ ] 每个分类都有聚合总命令，且能独立跑通；同前缀命令组里有一个语义完整的默认命令，而不是靠 `docker: docker-build` 这类纯转发别名充数
- [ ] 分类按操作对象划分，打包发布与容器操作没有被塞进同一章
- [ ] 所有可调参数是 `?=`，`make <target> VAR=value` 能覆盖
- [ ] 多步骤命令有阶段提示，结束时给出下一步；阶段编号全局一致
- [ ] 前台常驻命令的提示写明「Ctrl+C 退出」
- [ ] 成对命令（up/down）输出互相指路，实现保持一行
- [ ] `export` 的变量名与定义一致
- [ ] 每个 target 都在 `make help` 输出里可见（跑完对照一遍，漏写行尾 `##` 的会消失）
- [ ] 兼容别名没有写行尾 `##`，不会在 help 里重复出现
- [ ] 行尾 `##` 描述未使用 `$(VAR)`，全是静态文本
