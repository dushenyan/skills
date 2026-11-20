.PHONY: help install skills skill link skills-dry skills-copy skills-uninstall lint lint-fix typecheck check

# install.ts 的额外参数，例如 make skills ARGS="--copy --target=claude"
ARGS ?=

# 显示所有可用命令
help:
	@echo "可用命令："
	@echo "  make install          - 安装依赖"
	@echo "  make skills           - 全量对齐：所有技能软链接到本地各编辑器，并清理已删除的残留"
	@echo "  make skill            - 终端速览技能清单（名称 + 一句话用途）"
	@echo "  make link             - 用 pnpm link --global 注册全局 skill 命令"
	@echo "  make skills-dry       - 预演安装，不落盘"
	@echo "  make skills-copy      - 复制文件安装，不使用软链接"
	@echo "  make skills-uninstall - 从各编辑器移除本仓库的技能"
	@echo "  make lint             - 检查代码风格"
	@echo "  make lint-fix         - 自动修复代码风格"
	@echo "  make typecheck        - 类型检查"
	@echo "  make check            - lint + typecheck"
	@echo ""
	@echo "自定义参数：make skills ARGS=\"--target=claude --skill=cli\""

# 安装依赖
install:
	pnpm install

# 把 skills/ 下的技能安装到本地已检测到的编辑器（默认软链接）
skills:
	pnpm skills $(ARGS)

# 终端速览技能清单
skill:
	./bin/skill $(ARGS)

# 注册全局 skill 命令（make link 一键配置）
link:
	pnpm link --global

# 预演安装，只打印将要执行的操作
skills-dry:
	pnpm skills --dry-run $(ARGS)

# 复制文件安装，不使用软链接
skills-copy:
	pnpm skills --copy $(ARGS)

# 从各编辑器移除本仓库的技能
skills-uninstall:
	pnpm skills --uninstall $(ARGS)

# 检查代码风格
lint:
	pnpm lint

# 自动修复代码风格
lint-fix:
	pnpm lint:fix

# 类型检查
typecheck:
	pnpm typecheck

# 完整校验：代码风格 + 类型
check:
	pnpm lint
	pnpm typecheck
