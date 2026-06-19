---
name: thesis-architect
version: "2.1"
description: 研究生开题论题生成技能。当用户需生成论文选题、开题报告或分析导师项目谱系与同门论文时调用。
---

# ThesisArchitect — 研究生开题论题生成技能

## 技能概述

ThesisArchitect 是面向研究生开题阶段的高阶智能体技能，通过学术谱系解析、四维创意引擎与硬约束自动修复，生成符合学术生存法则的实战论题并直出开题报告素材。本技能采用无状态执行与 I/O 多态自适应设计，作为底层大模型运行时的即插即用插件运行。

## 三层结构说明

本技能采用三层物理结构，职责分明、按需加载：

- **元数据层（本文件 `SKILL.md`）**：仅含唯一标识、版本与触发条件，供调度系统快速匹配，不含工作流细节。
- **指令层（`./INSTRUCTION.md`）**：定义工作流决策规则、I/O 接口规范、自愈兜底与渐进式披露原则，是技能的"灵魂"。
- **资源层（`../core/`）**：承载可执行脚本、静态参考数据与 I/O Schema，仅在执行到对应步骤时按需加载，不在激活时全量注入上下文。

## 部署路径

将 `claude-skill/` 与 `core/` 两个目录一同置于 Claude 运行时的 `/skills/` 目录下，保持两者同级（`core/` 为 `claude-skill/` 的同级目录，确保 `../core/` 相对路径有效）。以 Claude Code 为例：`claude-skill/` 置于 `~/.claude/skills/thesis-architect/`，`core/` 置于同级 `~/.claude/skills/core/`。

## 资源指针

- **指令层**：`./INSTRUCTION.md`
- **资源层脚本**：`../core/scripts/`
  - `lineage_parser.py`（谱系解析，`parse_lineage()`）
  - `idea_generator.py`（四维创意，`generate_ideas()`）
  - `constraint_checker.py`（约束校验与修复，`check_and_repair()`）
  - `report_generator.py`（开题报告直出，`generate_report()`）
- **资源层参考数据**：`../core/references/`
  - `constraints.json`（硬约束规则）
  - `scoring_weights.json`（候选自评分权重）
  - `report_template.md`（开题报告模板）
  - `prompt_templates.json`（Prompt 约束模板）
- **I/O Schema**：`../core/schema/`
  - `input_schema.json`（输入校验）
  - `output_schema.json`（输出结构）
