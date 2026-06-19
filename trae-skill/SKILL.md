---
name: "thesis-architect"
version: "4.0"
description: "研究生开题全生命周期导航技能。提供信息确权、谱系解析、四维创意、重复度评估、多粒度生成、降重脱敏与深度辅助（文献精读/实验预研/答辩模拟）。当用户需生成论文选题、开题报告或分析导师项目谱系时调用。"
---

# ThesisArchitect — 研究生开题智能体技能（元数据层）

ThesisArchitect 是面向研究生开题阶段的无状态智能体技能，承载信息确权、谱系解析、四维创意涌现、重复度评估、多粒度生成、降重脱敏与深度辅助七大能力，提供开题全生命周期导航。V4.0 采用五阶段闭环导航流（信息确权→谱系解析与四维创意→重复度评估与硬约束修复→多粒度生成与降重脱敏→深度辅助闭环）。本文件仅作为元数据层，供 Trae IDE 调度系统快速匹配与加载；具体工作流决策规则、I/O 接口规范与自愈兜底逻辑见指令层。技能不维护多轮对话状态，不管理上下文窗口与 Token 账单，这些由底层 Agent 运行时原生托管。

## 三层结构

本 Skill 采用三层物理结构，职责分明、按需加载：

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| 元数据层 | `SKILL.md`（本文件） | 唯一标识、版本、触发条件，供调度系统快速匹配 |
| 指令层 | `./INSTRUCTION.md` | V4.0 五阶段闭环导航流、Rule 7-10 阻断性规则、I/O 接口规范、自愈兜底、Prompt 约束 |
| 资源层 | `../core/` | 可执行脚本、静态参考数据、I/O Schema，按需加载 |

## 部署路径

将 `trae-skill/` 目录内容复制到 Trae IDE 工作区 Skill 目录，`core/` 复制到项目根目录：

```
<项目根目录>/
├── .trae/skills/thesis-architect/
│   ├── SKILL.md              # 元数据层
│   └── INSTRUCTION.md        # 指令层
└── core/                     # 资源层（共享）
    ├── scripts/              # 6 个可执行脚本
    ├── references/           # 7 个静态参考数据
    └── schema/               # 2 个 I/O Schema
```

## 资源指针

- **指令层**：`./INSTRUCTION.md`
- **资源层脚本**：`../core/scripts/`（lineage_parser.py、idea_generator.py、constraint_checker.py、report_generator.py、style_normalizer.py、deep_helper.py，共 6 个）
  - `lineage_parser.py`（谱系解析，`parse_lineage()`）
  - `idea_generator.py`（四维创意，`generate_ideas()`）
  - `constraint_checker.py`（约束校验与修复，`check_and_repair()`、`check_novelty()`）
  - `report_generator.py`（开题报告直出，`generate_report()`）
  - `style_normalizer.py`（去 AI 痕迹，`remove_ai_traces()`）
  - `deep_helper.py`（深度辅助三件套，`literature_deep_reader()` / `experiment_designer()` / `thesis_defense_simulator()`）
- **资源层参考数据**：`../core/references/`（constraints.json、scoring_weights.json、report_template.md、prompt_templates.json、search_strategies.json、forbidden_ai_phrases.json、output_granularity.yaml，共 7 个）
  - `constraints.json`（硬约束规则）
  - `scoring_weights.json`（候选自评分权重）
  - `report_template.md`（开题报告模板）
  - `prompt_templates.json`（Prompt 约束模板）
  - `search_strategies.json`（检索式模板与时间窗）
  - `forbidden_ai_phrases.json`（AI 化术语映射表）
  - `output_granularity.yaml`（多粒度配置）
- **I/O Schema**：`../core/schema/`（input_schema.json、output_schema.json，共 2 个）
