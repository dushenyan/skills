---
name: core-dependency-and-makefile
description: uv 依赖环境与 Makefile 规范：依赖初始化、命令组织、端口清理与注释位置，初始化依赖或编写 Makefile 时读取。
---

# 依赖管理与 Makefile 规范

本文件覆盖 Skill 的「一、依赖管理：uv 环境」与「二、Makefile 规范」两部分。

## 一、依赖管理：uv 环境

项目统一使用 **uv** 进行 Python 依赖管理与虚拟环境管理。

- 使用 `uv add` 安装依赖，`uv remove` 移除依赖
- 虚拟环境通过 uv 自动管理，不手动创建 venv
- 如需运行脚本，优先使用 `uv run <command>`

---

## 二、Makefile 规范

Makefile 是项目操作的统一入口，必须满足以下要求：

### 2.1 端口自动清理

- 如果命令涉及启动服务（占用端口），在执行前必须先杀死对应端口的旧进程
- 示例：`lsof -ti :8000 | xargs kill -9 2>/dev/null || true` 放在对应 target 的第一行

### 2.2 注释格式

- 注释必须写在命令行的**上方**（作为该 target 的说明），使用 `#` 开头
- 推荐使用 `.PHONY` 标记所有非文件 target

### 2.3 Makefile 推荐结构

```makefile
.PHONY: help install dev test clean

# 显示帮助信息
help:
	@echo "可用命令："
	@echo "  make install  - 安装依赖"
	@echo "  make dev      - 启动开发服务"
	@echo "  make test     - 运行测试"
	@echo "  make clean    - 清理临时文件"

# 安装项目依赖（使用 uv）
install:
	uv sync

# 启动开发服务，启动前先杀死旧的 8000 端口进程
dev:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	uv run python -m app.main
```
