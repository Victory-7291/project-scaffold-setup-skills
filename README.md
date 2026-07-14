# Project Scaffold Setup Skills

这个仓库用于维护一组面向 agent 的项目脚手架 skills，目标是让 Codex/Claude/其他支持 skills 的 agent 能够从零快速搭建结构清晰、工具链明确、可验证的工程项目。

仓库里的每个 skill 都聚焦一个项目类型，包含：

- 面向 agent 的 `SKILL.md` 操作说明
- 可重复运行的脚手架生成脚本
- 项目结构、工具链和质量门禁参考文档
- 可选的 agent/界面元数据

## 已有 Skills

| Skill | 用途 | 入口 |
| --- | --- | --- |
| `cpp-project-setup` | 创建或现代化 C++/CMake/vcpkg 项目，包含 VS Code、CMake Presets、GoogleTest、clangd、clang-format、clang-tidy、Doxygen 等基础设施。 | `skills/cpp-project-setup/SKILL.md` |
| `embedded-project-setup` | 创建或现代化 STM32/Cortex-M 嵌入式 C 项目，包含 CMake、Ninja、arm-none-eabi、OpenOCD、Cortex-Debug、固件产物和基础 CI 结构。 | `skills/embedded-project-setup/SKILL.md` |
| `template-skill` | 新 skill 的最小模板。 | `template/SKILL.md` |

## 仓库结构

```text
.
├── README.md
├── AGENTS.md
├── template/
│   └── SKILL.md
└── skills/
    ├── cpp-project-setup/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   ├── references/
    │   │   └── cpp-project-blueprint.md
    │   └── scripts/
    │       └── scaffold_cpp_project.py
    └── embedded-project-setup/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   └── embedded-project-blueprint.md
        └── scripts/
            └── scaffold_embedded_project.py
```

## Skill 目录约定

每个正式 skill 放在 `skills/<skill-name>/` 下，并尽量使用以下结构：

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── <domain>-blueprint.md
└── scripts/
    └── scaffold_<domain>_project.py
```

`SKILL.md` 必须包含 YAML frontmatter：

```yaml
---
name: skill-name
description: Clear trigger description for when an agent should use this skill.
---
```

`description` 要写清楚触发场景、项目类型、核心工具链和 agent 应该使用它的时机。主体内容建议包含：

- Overview：这个 skill 解决什么问题
- Workflow：agent 应该如何判断、生成或改造项目
- Validation：本地可执行的验证命令
- References：需要读取哪些参考文档或脚本

## 使用脚手架脚本

脚本默认用 Python 标准库实现，方便 agent 在干净环境里直接运行。

创建 C++ 项目：

```bash
python3 skills/cpp-project-setup/scripts/scaffold_cpp_project.py \
  --name my_app \
  --out /tmp/my_app
```

创建嵌入式项目：

```bash
python3 skills/embedded-project-setup/scripts/scaffold_embedded_project.py \
  --name firmware \
  --out /tmp/firmware
```

生成到真实工作区前，建议先输出到临时目录检查文件结构和默认配置。

## 新增 Skill 流程

1. 从 `template/SKILL.md` 复制出新的 `skills/<skill-name>/SKILL.md`。
2. 写清楚 frontmatter 中的 `name` 和 `description`。
3. 在 `SKILL.md` 中定义 agent 的判断逻辑、默认方案、生成流程和验证步骤。
4. 如需生成项目文件，添加 `scripts/` 下的脚手架脚本，并保持可重复、可参数化。
5. 如需长篇背景、架构蓝图或命令细节，放入 `references/`，不要把所有细节塞进 `SKILL.md`。
6. 如需在支持的界面里显示 skill 信息，添加 `agents/openai.yaml`。
7. 用临时目录运行脚本，确认生成结果可用，再提交修改。

## 维护原则

- skills 应该描述“agent 如何可靠完成任务”，不是只写人类教程。
- 生成脚本要偏保守：默认创建清晰的最小可用项目，不假设全局机器状态。
- 参考文档可以详细，`SKILL.md` 要可快速执行。
- 改已有 skill 前先读它的 `SKILL.md`、`references/` 和 `scripts/`。
- 验证失败或依赖缺失时，在结果中明确说明跳过了什么、为什么跳过。
