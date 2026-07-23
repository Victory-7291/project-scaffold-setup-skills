# AGENTS.md

本文件面向维护这个仓库的 agent。当前仓库专门保存项目脚手架类 skills，用来帮助 agent 从零快速构建不同类型的工程项目。

## 工作范围

- 主要内容在 `skills/<skill-name>/`。
- 每个 skill 至少包含 `SKILL.md`，通常还会包含 `scripts/`、`references/` 和 `agents/`。
- `template/` 是新 skill 的起点，保持轻量，不要塞入某个具体技术栈的实现细节。

## 维护规则

- 修改某个 skill 前，先完整阅读该 skill 的 `SKILL.md`。
- 如果 `SKILL.md` 指向 `references/` 或脚本，先读相关文件再动手。
- 保持每个 skill 的触发说明准确：`description` 应该说明适用场景，而不是只写一句泛泛介绍。
- 脚手架脚本优先使用 Python 标准库，避免引入不必要的运行时依赖。
- 生成脚本应支持明确的 `--name` 和 `--out` 参数，必要时支持 `--force`，但不要默认覆盖用户文件。
- 不要把大段生成模板复制进多个地方；如果逻辑复杂，优先集中在脚本或参考文档里维护。
- 不要提交生成出来的示例项目，除非它们是明确需要长期维护的 fixture。

## 文档风格

- README 面向使用者和贡献者，说明这个仓库是什么、有哪些 skills、如何新增和验证。
- `SKILL.md` 面向 agent，写可执行的判断和操作流程。
- `references/*.md` 面向复杂背景和蓝图，可以比 `SKILL.md` 更详细。
- 命令示例要能直接复制运行，路径尽量使用仓库相对路径。
- 避免只写抽象建议；需要给出默认工具链、目录结构、验证命令和失败处理方式。

## 新增或修改 Skill 的检查清单

1. `SKILL.md` 有合法 frontmatter：`name` 和 `description`。
2. `description` 覆盖触发词、项目类型、核心工具链和使用时机。
3. `Workflow` 说明 greenfield 和 existing project 两种路径。
4. `Validation` 给出本地可以执行的验证命令。
5. 脚本可通过 `python3 <script> --help`。
6. 脚本生成结果建议先放到 `/tmp/<name>` 或其他临时目录检查。
7. 如果新增 `agents/openai.yaml`，确保展示名、短描述和默认提示与 skill 名称一致。

## 推荐验证命令

检查 Python 脚本语法：

```bash
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile skills/*/scripts/*.py
```

查看脚手架脚本参数：

```bash
python3 skills/cpp-project-setup/scripts/scaffold_cpp_project.py --help
python3 skills/embedded-project-setup/scripts/scaffold_embedded_project.py --help
python3 skills/python-fastapi-setup/scripts/scaffold_fastapi_project.py --help
```

生成临时项目做烟测：

```bash
rm -rf /tmp/codex-skill-smoke
mkdir -p /tmp/codex-skill-smoke

python3 skills/cpp-project-setup/scripts/scaffold_cpp_project.py \
  --name smoke_cpp \
  --out /tmp/codex-skill-smoke/smoke_cpp

python3 skills/embedded-project-setup/scripts/scaffold_embedded_project.py \
  --name smoke_fw \
  --out /tmp/codex-skill-smoke/smoke_fw

python3 skills/python-fastapi-setup/scripts/scaffold_fastapi_project.py \
  --name smoke_api \
  --out /tmp/codex-skill-smoke/smoke_api
```

如果本机缺少 Python、CMake、vcpkg、交叉编译器、OpenOCD、硬件或 Docker 能力，不要伪造验证结果；说明依赖缺失，并保留可复现命令。

## 提交前注意

- 保留用户已有改动，不要重置或清理与任务无关的文件。
- 新增文件尽量保持小而清晰。
- 如果修改脚本，至少运行 `python3 -m py_compile` 和对应 `--help`。
- 如果修改生成模板，至少生成一次临时项目并检查关键文件是否存在。
