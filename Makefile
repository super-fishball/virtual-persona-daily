# 根级入口：一条命令跑全部 4 子项目的四道质量门。
# - TS 两个（apps/web, servers/api）走 pnpm workspace（pnpm -r）。
# - Python 两个（generation-service, ai-gateway）走各自 Makefile（uv）。
# CI 与 verification-loop 用 `make check`。

PY_DIRS := servers/generation-service servers/ai-gateway

.PHONY: check install build test lint typecheck clean

## 全部四道门（lint + typecheck + test + build），跨 4 子项目
check: lint typecheck test build
	@echo "==> all gates green"

## 安装所有依赖（pnpm workspace + 各 Python 子项目 uv sync）
install:
	pnpm install
	@for d in $(PY_DIRS); do echo ">> install $$d"; $(MAKE) -C $$d install || exit 1; done

build:
	pnpm -r run build
	@for d in $(PY_DIRS); do echo ">> build $$d"; $(MAKE) -C $$d build || exit 1; done

test:
	pnpm -r run test
	@for d in $(PY_DIRS); do echo ">> test $$d"; $(MAKE) -C $$d test || exit 1; done

lint:
	pnpm -r run lint
	@for d in $(PY_DIRS); do echo ">> lint $$d"; $(MAKE) -C $$d lint || exit 1; done

typecheck:
	pnpm -r run typecheck
	@for d in $(PY_DIRS); do echo ">> typecheck $$d"; $(MAKE) -C $$d typecheck || exit 1; done

clean:
	rm -rf node_modules apps/web/node_modules servers/api/node_modules apps/web/dist servers/api/dist
	@for d in $(PY_DIRS); do $(MAKE) -C $$d clean || true; done
