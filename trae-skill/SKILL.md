---
name: "thesis-architect"
version: "2.1"
description: "研究生开题阶段智能体技能，提供谱系解析、四维创意涌现、硬约束自动修复与开题报告直出。当用户需要生成论题提案或开题报告时调用。"
---

# ThesisArchitect — 研究生开题智能体技能（元数据层）

ThesisArchitect 是面向研究生开题阶段的无状态智能体技能，承载谱系解析、四维创意涌现、硬约束自动修复与开题报告直出四大能力。本文件仅作为元数据层，供 Trae IDE 调度系统快速匹配与加载；具体工作流决策规则、I/O 接口规范与自愈兜底逻辑见指令层。技能不维护多轮对话状态，不管理上下文窗口与 Token 账单，这些由底层 Agent 运行时原生托管。

## 三层结构

本 Skill 采用三层物理结构，职责分明、按需加载：

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| 元数据层 | `SKILL.md`（本文件） | 唯一标识、版本、触发条件，供调度系统快速匹配 |
| 指令层 | `./INSTRUCTION.md` | 工作流决策规则、I/O 接口规范、自愈兜底、Prompt 约束 |
| 资源层 | `../core/` | 可执行脚本、静态参考数据、I/O Schema，按需加载 |

## 部署路径

将 `trae-skill/` 目录内容复制到 Trae IDE 工作区 Skill 目录，`core/` 复制到项目根目录：

```
<项目根目录>/
├── .trae/skills/thesis-architect/
│   ├── SKILL.md              # 元数据层
│   └── INSTRUCTION.md        # 指令层
└── core/                     # 资源层（共享）
    ├── scripts/              # 4 个可执行脚本
    ├── references/           # 4 个静态参考数据
    └── schema/               # 2 个 I/O Schema
```

## 资源指针

- **指令层**：`./INSTRUCTION.md`
- **资源层脚本**：`../core/scripts/`（lineage_parser.py、idea_generator.py、constraint_checker.py、report_generator.py，共 4 个）
- **资源层参考数据**：`../core/references/`（constraints.json、scoring_weights.json、report_template.md、prompt_templates.json，共 4 个）
- **I/O Schema**：`../core/schema/`（input_schema.json、output_schema.json，共 2 个）
