# 多平台 Skill 产出 Spec

## Why
项目根目录已存在一份平台无关的 `ThesisMinerSkills设计文档.md`（ThesisArchitect v2.0），描述了研究生开题阶段的智能体技能设计。但该设计文档无法被任何具体 AI 运行时直接加载执行。需要将其转译为各主流 AI 平台原生可识别的 Skill / 规则格式，使同一套 ThesisArchitect 能力可在 Claude、OpenAI 及其他主流运行时中即插即用，避免用户手工二次适配。

## What Changes
- 初始化项目 Git 仓库（当前项目未纳入版本控制），将设计文档与产出纳入管理。
- 基于根目录 `ThesisMinerSkills设计文档.md`，在**独立文件夹**中分别产出以下 Skill 产物：
  - **Claude Skill**（Anthropic 原生 SKILL.md 格式，含 frontmatter）
  - **OpenAI Skill**（Custom GPT 指令格式：`gpt-instructions.md` + 可选 `actions` 描述）
- 同时产出**其他主流格式**的 Skill（满足"如果还有其他格式的 Skill 也要产出"）：
  - **Cursor Rules**（`.mdc` 规则文件）
  - **Trae Skill**（`.trae/skills/<name>/SKILL.md` 格式）
  - **GitHub Copilot Instructions**（`.github/copilot-instructions.md`）
- 生成项目架构 `README.md`（按 `架构readmeV3.0` 命令模板要求）。
- 所有 Skill 产物**内容等价**：均完整承载设计文档中的谱系解析、四维创意引擎、硬约束修复、开题直出、I/O 多态自适应五大核心能力，仅在外层格式/触发语法上做平台适配。

## Impact
- Affected specs: 无（首个 spec）
- Affected code: 
  - 新增 `claude-skill/` 目录及 `SKILL.md`
  - 新增 `openai-skill/` 目录及 `gpt-instructions.md`、`config.json`
  - 新增 `cursor-skill/` 目录及 `thesis-architect.mdc`
  - 新增 `trae-skill/` 目录及 `SKILL.md`
  - 新增 `copilot-skill/` 目录及 `copilot-instructions.md`
  - 新增 `README.md`（项目架构文档）
  - 新增 `.gitignore`、初始化 Git 仓库
  - 不修改既有 `ThesisMinerSkills设计文档.md`

## ADDED Requirements

### Requirement: Git 仓库初始化
系统 SHALL 在项目根目录初始化 Git 仓库，使所有 Skill 产物与设计文档纳入版本控制。

#### Scenario: 首次初始化
- **WHEN** 执行 `git init` 后
- **THEN** 项目根目录存在 `.git` 目录，且 `.gitignore` 排除运行时产物（`/output/`、`/input/`、`__pycache__/`、`.DS_Store`）

### Requirement: Claude Skill 产出
系统 SHALL 在独立目录 `claude-skill/` 中产出符合 Anthropic Claude Skill 规范的 `SKILL.md`。

#### Scenario: Claude Skill 可加载
- **WHEN** 将 `claude-skill/` 内容置于 Claude 运行时 skills 目录
- **THEN** 运行时能识别 frontmatter 中的 `name` 与 `description`，并按正文指令执行 ThesisArchitect 工作流

#### Scenario: 内容完整承载
- **GIVEN** Claude `SKILL.md` 正文
- **THEN** 必须包含：I/O 多态路由说明、谱系解析器、四维创意引擎（含自评分）、硬约束校验与自动修复器、开题报告直出模板、Prompt 约束模板

### Requirement: OpenAI Skill 产出
系统 SHALL 在独立目录 `openai-skill/` 中产出 OpenAI Custom GPT 可用的指令文件 `gpt-instructions.md` 与配置 `config.json`。

#### Scenario: OpenAI GPT 可导入
- **WHEN** 将 `gpt-instructions.md` 内容粘贴至 Custom GPT 的 Instructions 字段
- **THEN** GPT 能按指令执行四维创意生成与开题报告直出

#### Scenario: 配置可读
- **GIVEN** `openai-skill/config.json`
- **THEN** 包含 `name`、`description`、`capabilities`、`suggested_starters` 字段

### Requirement: 其他平台格式产出
系统 SHALL 额外产出 Cursor Rules、Trae Skill、GitHub Copilot Instructions 三种格式的 Skill，各自位于独立目录。

#### Scenario: Cursor 规则可识别
- **WHEN** 将 `cursor-skill/thesis-architect.mdc` 置于 `.cursor/rules/`
- **THEN** Cursor 编辑器能加载该规则并在论文开题场景触发

#### Scenario: Trae Skill 可识别
- **WHEN** 将 `trae-skill/` 内容置于 `.trae/skills/thesis-architect/`
- **THEN** Trae IDE 能通过 Skill 发现机制加载该技能

#### Scenario: Copilot 指令可识别
- **WHEN** 将 `copilot-skill/copilot-instructions.md` 置于 `.github/`
- **THEN** GitHub Copilot Chat 能读取该指令作为上下文

### Requirement: 内容等价性
所有平台产出的 Skill SHALL 在能力层面等价，差异仅限于格式包装与触发语法。

#### Scenario: 跨平台能力对齐
- **GIVEN** 任一平台 Skill 产物
- **THEN** 必须能完成：谱系解析 → 四维创意（含自评分过滤）→ 硬约束修复 → 开题报告直出 的完整链路

### Requirement: 项目架构 README
系统 SHALL 在项目根目录生成 `README.md`，按 `架构readmeV3.0` 模板覆盖项目概述、技术栈、文件结构、核心机制、API/接口清单。

#### Scenario: README 完整性
- **GIVEN** 根目录 `README.md`
- **THEN** 包含：项目概述、文件结构与职责、技术栈、核心机制与架构设计、Skill 接口/调用清单、配置与环境变量、部署与运行、扩展性设计

### Requirement: 平台格式规范遵循
每个 Skill 产物 SHALL 严格遵循目标平台的原生格式规范，不混用格式。

#### Scenario: Claude frontmatter 合规
- **GIVEN** `claude-skill/SKILL.md`
- **THEN** 顶部为 YAML frontmatter，包含 `name` 与 `description` 字段，`description` 不超过 200 字符且说明"做什么 + 何时触发"

#### Scenario: OpenAI 指令无 frontmatter
- **GIVEN** `openai-skill/gpt-instructions.md`
- **THEN** 为纯 Markdown 指令文本，无 YAML frontmatter（Custom GPT Instructions 字段不解析 frontmatter）
