# ThesisMinerSkill — 多平台开题智能体 Skill 集合

> **版本**：V1.0
> **日期**：2026-06-19
> **设计底座**：ThesisArchitect v2.0 (Skill-Native & I/O Agnostic Edition)
> **设计理念**：无状态执行 · I/O 多态自适应 · 四维创意引擎 · 硬约束自动修复 · 开题直出

---

## 目录

1. [项目概述](#1-项目概述)
2. [文件结构与职责](#2-文件结构与职责)
3. [技术栈详情](#3-技术栈详情)
4. [核心机制与架构设计](#4-核心机制与架构设计)
5. [Skill 接口/调用清单](#5-skill-接口调用清单)
6. [配置与环境变量](#6-配置与环境变量)
7. [部署与运行](#7-部署与运行)
8. [扩展性设计](#8-扩展性设计)
9. [常见问题与故障排除（FAQ）](#9-常见问题与故障排除faq)

---

## 1. 项目概述

### 1.1 项目定位

**一句话定义**：ThesisMinerSkill 是一个将平台无关的 ThesisArchitect v2.0 设计文档转译为 5 个主流 AI 平台原生 Skill 格式的多平台技能集合项目，使同一套研究生开题智能体能力可在不同 AI 运行时中即插即用。

- **目标用户**：研究生（硕士/博士）及其导师、需要协助学生完成开题阶段工作的学术辅助人员、希望在自有 AI 平台中部署开题智能体的研发团队。
- **解决的核心问题**：原始设计文档无法被任何具体 AI 运行时直接加载执行；不同平台 Skill 格式规范差异巨大，用户手工二次适配成本高。本项目通过一次性转译，让 ThesisArchitect 的谱系解析、四维创意、硬约束修复、开题直出等能力在 Claude、OpenAI、Cursor、Trae、GitHub Copilot 五大平台原生可用。

### 1.2 核心功能

| 模块 | 功能描述 |
| --- | --- |
| 谱系解析 | 鲁棒性解析非结构化文本，抽取导师项目与同门论文实体，并通过边缘探测标记"未走完的路"作为高价值切入点 |
| 四维创意引擎 | 并行调用导师项目延伸、同门成果继承、跨域联想、矛盾驱动四个策略生成候选论题，并通过自评分（可行性 40% + 创新度 30% + 谱系贴合度 30%）过滤低于 6 分的方向 |
| 硬约束修复 | 对标题格式（≤20 字、无动词前置、杜绝"基于 X 的 Y 研究"）、学术日历（硕士 ≤12 月 / 博士 ≤24 月）、文献基线（硕士 ≥30 篇 / 博士 ≥50 篇）、逻辑自洽（重合度 ≤70%）执行确定性自动修复 |
| 开题直出 | 严格对齐国内双一流高校标准开题模板，强制按"选题依据、国内外研究现状、研究内容与关键问题、研究方案与可行性、进度安排"五大模块填充并直出 Markdown 草稿 |
| I/O 多态 | 摒弃死板文件依赖，按意图识别路由输入（文件/对话/混合）与输出（文件/对话），适配各平台原生交互通道 |
| 多平台分发 | 同一套设计能力转译为 5 个平台原生格式（Claude SKILL.md、OpenAI GPT Instructions、Cursor .mdc、Trae SKILL.md、Copilot instructions.md），各自即插即用 |

### 1.3 技术底座

本项目是 **Skill 集合项目**，而非传统应用代码库。项目内不含可执行的应用源码（无 Python/JS/Go 主程序），全部产物均为面向各 AI 平台运行时的指令文本（Markdown / YAML frontmatter / JSON 配置），由底层大模型运行时加载并解释执行。

**支持的 AI 平台**：

| 平台 | 厂商 | 产物形态 |
| --- | --- | --- |
| Claude Code / Anthropic 运行时 | Anthropic | SKILL.md（YAML frontmatter + Markdown 正文） |
| OpenAI Custom GPT | OpenAI | gpt-instructions.md（纯 Markdown 指令）+ config.json |
| Cursor | Anysphere | thesis-architect.mdc（Cursor 专属 frontmatter） |
| Trae IDE | ByteDance | SKILL.md（YAML frontmatter + Markdown 正文） |
| GitHub Copilot Chat | Microsoft/GitHub | copilot-instructions.md（纯 Markdown 指令） |

---

## 2. 文件结构与职责

### 2.1 目录树

```bash
ThesisMinerSkill/
├── ThesisMinerSkills设计文档.md          # 平台无关的原始设计文档（ThesisArchitect v2.0）
├── README.md                              # 项目架构文档（本文件）
├── .gitignore                             # Git 忽略规则（排除 /output/、/input/、缓存等）
│
├── claude-skill/                          # Claude 原生 Skill 产物
│   ├── SKILL.md                           # Claude Skill 主体（YAML frontmatter + 正文）
│   └── README.md                          # Claude Skill 部署说明
│
├── openai-skill/                          # OpenAI Custom GPT 产物
│   ├── gpt-instructions.md                # Custom GPT Instructions 字段内容（纯 Markdown）
│   ├── config.json                        # GPT 元信息记录（团队协作参考，非官方导入文件）
│   └── README.md                          # OpenAI Skill 部署说明
│
├── cursor-skill/                          # Cursor Rules 产物
│   ├── thesis-architect.mdc               # Cursor 规则文件（专属 frontmatter）
│   └── README.md                          # Cursor Skill 部署说明
│
├── trae-skill/                            # Trae IDE Skill 产物
│   ├── SKILL.md                           # Trae Skill 主体（YAML frontmatter + 正文）
│   └── README.md                          # Trae Skill 部署说明
│
├── copilot-skill/                         # GitHub Copilot Chat 指令产物
│   ├── copilot-instructions.md            # Copilot 自定义指令（纯 Markdown）
│   └── README.md                          # Copilot Skill 部署说明
│
└── .trae/
    └── specs/
        └── multi-platform-skills/
            ├── spec.md                    # 多平台 Skill 产出规格（Why/What/Requirements）
            ├── tasks.md                   # 任务拆解
            └── checklist.md               # 验收清单
```

### 2.2 核心文件职责说明

| 文件 | 职责唯一性说明 |
| --- | --- |
| `ThesisMinerSkills设计文档.md` | 唯一的平台无关设计源，定义 ThesisArchitect v2.0 的全部能力与工作流，是所有平台 Skill 产物的转译源头，不被任何运行时直接加载 |
| `claude-skill/SKILL.md` | 唯一面向 Anthropic Claude 运行时的 Skill 产物，以 YAML frontmatter（`name` + `description`）声明触发条件，正文承载完整能力 |
| `openai-skill/gpt-instructions.md` | 唯一面向 OpenAI Custom GPT 的 Instructions 字段内容，纯 Markdown 无 frontmatter，将 SYSTEM/USER 分离模板内化为行为准则 |
| `openai-skill/config.json` | 唯一的 GPT 元信息记录文件（非官方导入文件），供团队协作时统一 Name/Description/Conversation starters 口径 |
| `cursor-skill/thesis-architect.mdc` | 唯一面向 Cursor 编辑器的规则文件，使用 Cursor 专属 frontmatter（`description` + `globs` + `alwaysApply`）控制按需触发 |
| `trae-skill/SKILL.md` | 唯一面向 Trae IDE 的 Skill 产物，由 Trae 启动时扫描 `.trae/skills/` 自动加载 |
| `copilot-skill/copilot-instructions.md` | 唯一面向 GitHub Copilot Chat 的项目级自定义指令，纯 Markdown 无 frontmatter，由 Copilot 自动注入为系统上下文 |
| `.trae/specs/multi-platform-skills/spec.md` | 唯一的项目规格文档，定义多平台 Skill 产出的 Why/What/Requirements/Scenarios，是项目验收依据 |
| `README.md` | 唯一的项目架构文档，面向开发者说明项目定位、文件结构、技术栈、核心机制与部署方式 |
| `.gitignore` | 唯一的 Git 忽略规则，排除 `/output/`、`/input/` 运行时产物与 Python/IDE/OS 缓存 |

---

## 3. 技术栈详情

本项目不含传统编程语言技术栈，全部产物为面向各 AI 平台的指令文本。各平台 Skill 的格式规范如下：

| 平台 | 产物文件 | 格式规范 | Frontmatter 要求 | 触发机制 |
| --- | --- | --- | --- | --- |
| Claude | `SKILL.md` | Markdown + YAML frontmatter | 必需，含 `name`、`description`（≤200 字符，说明"做什么 + 何时触发"） | 运行时按 `description` 语义匹配自动激活 |
| OpenAI Custom GPT | `gpt-instructions.md` | 纯 Markdown 指令文本 | 不支持（Custom GPT Instructions 字段不解析 frontmatter） | 用户在 ChatGPT 中与 GPT 对话即触发 |
| Cursor | `thesis-architect.mdc` | Markdown + Cursor 专属 frontmatter | 必需，含 `description`、`globs`、`alwaysApply` | 按 `description` 语义 + `globs` 文件模式匹配，`alwaysApply: false` 按需触发 |
| Trae IDE | `SKILL.md` | Markdown + YAML frontmatter | 必需，含 `name`、`description` | Trae 启动时扫描 `.trae/skills/` 自动加载，按语义触发 |
| GitHub Copilot | `copilot-instructions.md` | 纯 Markdown 指令文本 | 不支持（Copilot 不解析 frontmatter） | 工作区存在 `.github/copilot-instructions.md` 时自动注入为系统上下文 |

**通用约定**：所有平台产物在能力层面等价，均完整承载谱系解析、四维创意引擎、硬约束修复、开题直出、I/O 多态自适应五大核心能力，差异仅在外层格式包装与触发语法。

---

## 4. 核心机制与架构设计

### 4.1 系统架构分层图

```text
┌─────────────────────────────────────────────────────────────────┐
│                    设计文档层（平台无关）                          │
│                                                                 │
│   ThesisMinerSkills设计文档.md  (ThesisArchitect v2.0)          │
│   ─────────────────────────────────────────────                 │
│   定义：谱系解析 / 四维创意 / 硬约束修复 / 开题直出 / I/O 多态     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │  一次性转译（保留能力等价性）
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    多平台转译层                                   │
│                                                                 │
│   按各平台原生格式规范包装：frontmatter / 纯 Markdown / .mdc      │
│   适配各平台触发语法与 I/O 通道（文件系统 / 对话框 / 上传文件）    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │  分发到 5 个独立目录
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                各平台 Skill 产物层                                │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ claude-skill │ │ openai-skill │ │ cursor-skill │            │
│  │  SKILL.md    │ │gpt-instruct. │ │thesis-arch.  │            │
│  │              │ │md+config.json│ │.mdc          │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐                              │
│  │  trae-skill  │ │copilot-skill │                              │
│  │  SKILL.md    │ │copilot-      │                              │
│  │              │ │instructions  │                              │
│  └──────────────┘ └──────────────┘                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │  部署到各平台运行时
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                AI 平台运行时层                                    │
│                                                                 │
│  Claude Code | ChatGPT | Cursor | Trae IDE | GitHub Copilot     │
│  （由运行时原生托管：多轮对话状态、上下文窗口、Token 账单）        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 核心业务流程

ThesisArchitect 的核心业务流程为无状态六步工作流，所有平台产物均按此顺序执行：

1. **I/O 意图识别**：解析用户指令，确定输入源（文件/对话/混合）与输出目标（文件/对话）。若关键信息（学位、导师项目或同门基础）缺失，先以简短提问补齐，不凭空假设。
2. **上下文加载与谱系解析**：读取并解析学位、学科、导师项目与同门基础信息，构建内部 `LineageGraph`。执行实体抽取（导师项目名称/目标/技术路线、同门论文标题/方法/局限性）与边缘探测（标记"未来工作""受限于算力/数据未展开"等高价值切入点）。
3. **四维创意发散**：并行调用四个策略（导师项目延伸、同门成果继承、跨域联想、矛盾驱动）生成原始候选，执行自评分，丢弃 < 6 分的方向，保留 Top 3–5 个方向。
4. **结构化精炼**：针对每个保留候选，填充 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline` 等字段。
5. **硬约束拦截与修复**：执行标题格式、学术日历、文献基线、逻辑自洽四类校验，对不达标项执行确定性自动修复，无法修复的标记 `WARNING`。
6. **多态输出**：若用户要求开题报告，提取最优提案按五大模块模板直出完整 Markdown；若只要候选提案，按字段结构化输出 Top 3–5；若要求文件输出，序列化为 JSON 与 Markdown 写入 `output/` 目录并回复路径摘要。

### 4.3 I/O 多态自适应

#### 输入路由（按优先级）

| 优先级 | 输入模式 | 触发条件 | 处理方式 |
| --- | --- | --- | --- |
| 1 | 文件输入 | 用户指令含 `@input/` 或运行时检测到 `/input/profile.json` 与 `/input/lineage.md` | 优先读取文件内容作为基础上下文 |
| 2 | 对话输入 | 未提供文件 | 通过对话引导获取学位、学科、导师项目、同门论文摘要 |
| 3 | 混合输入 | 文件 + 对话追加指令 | 以文件为背景底座，叠加对话中的临时修正（如"换方向做大模型"） |
| 4 | 缺失信息引导 | 关键信息缺失 | 在生成提案前用简短提问补齐，不凭空假设 |

#### 输出路由

| 输出模式 | 触发条件 | 产物 |
| --- | --- | --- |
| 对话输出（默认） | 默认模式或用户未明确要求保存 | 高可读性 Markdown 直接打印在对话框 |
| 文件输出 | 用户指令含"保存""生成文件""输出到本地""写入"等意图 | `output/proposals_<timestamp>.json` 与 `output/draft_<timestamp>.md`，并在对话回复路径摘要 |

### 4.4 四维创意引擎

#### 四个策略

| 策略 | 核心思路 | 示例 |
| --- | --- | --- |
| 导师项目延伸 | 将大项目拆解为可在规定学制内完成的子课题 | "医疗大模型研发" → "特定科室的问询微调" |
| 同门成果继承 | 基于边缘探测的局限点，引入新变量或迁移至新场景 | 同门在英文问诊做微调 → 继承到中文小样本场景 |
| 跨域联想 | 识别多个不相关学科概念，生成"A 领域方法解 B 领域问题"候选 | 用强化学习反馈机制优化医疗问诊的安全对齐 |
| 矛盾驱动挖掘 | 检测"现有方法能力边界"与"实际需求"的语义矛盾，基于矛盾生成论题 | 需要高精度但现有方法在噪声下失效 → 噪声鲁棒性论题 |

#### 自评分机制

每个候选生成后，按以下公式打分（满分 10 分）：

```text
总分 = 可行性 × 0.4 + 创新度 × 0.3 + 谱系贴合度 × 0.3
```

- **可行性**：学制内可完成度、数据/算力可获得性、技术成熟度
- **创新度**：与同门已有工作的差异化程度、方法新颖性
- **谱系贴合度**：与导师项目目标的对齐程度、对边缘点的承接程度

**过滤规则**：总分低于 6 分的候选直接丢弃，不向用户展示；最终保留 Top 3–5 个方向。

### 4.5 硬约束校验与自动修复

| 约束类型 | 约束规则 | 自动修复方式 |
| --- | --- | --- |
| 标题格式 | ≤20 字（中文按 1 字计）；不以"研究/分析/探讨/设计/构建/实现"等主动动词开头；不匹配"基于 X 的 Y 研究"套路 | 超长标题执行依存句法截取核心名词短语；动词前置结构转换为名词性短语（"研究 X" → "X 的研究"）；"基于 X 的 Y 研究"模式改写为突出核心贡献的名词短语 |
| 学术日历 | 研究周期硕士 ≤12 个月，博士 ≤24 个月 | 超期不熔断，在"研究内容"中自动注入"分阶段并行执行"的降级策略提示，并调整进度安排 |
| 文献基线 | 综述大纲至少规划硕士 30 篇 / 博士 50 篇文献的检索方向 | 规划不足时自动补充子方向检索词与数据库建议，直至达到基线 |
| 逻辑自洽 | "研究内容"与"研究目标"语义重合度 ≤70% | 重合度 > 70% 时标记 `WARNING: 内容与目标重合度过高`，提示用户区分"做什么"与"达成什么" |

---

## 5. Skill 接口/调用清单

### 5.1 五平台 Skill 总览

| 平台 | 产物路径 | 格式规范 | 部署位置 | 触发方式 |
| --- | --- | --- | --- | --- |
| Claude | `claude-skill/SKILL.md` | YAML frontmatter（`name` + `description`）+ Markdown 正文 | `~/.claude/skills/thesis-architect/SKILL.md` 或项目级 `.claude/skills/thesis-architect/SKILL.md` | 运行时按 `description` 语义匹配自动激活 |
| OpenAI Custom GPT | `openai-skill/gpt-instructions.md` + `openai-skill/config.json` | 纯 Markdown 指令（无 frontmatter）+ JSON 元信息 | ChatGPT → Explore GPTs → + Create → GPT Builder 的 Instructions 字段 | 用户在 ChatGPT 中与 GPT 对话即触发 |
| Cursor | `cursor-skill/thesis-architect.mdc` | Cursor 专属 frontmatter（`description` + `globs` + `alwaysApply`）+ Markdown 正文 | 项目根目录 `.cursor/rules/thesis-architect.mdc` | 按 `description` 语义 + `globs` 文件模式匹配，`alwaysApply: false` 按需触发 |
| Trae IDE | `trae-skill/SKILL.md` | YAML frontmatter（`name` + `description`）+ Markdown 正文 | `<项目根目录>/.trae/skills/thesis-architect/SKILL.md` | Trae 启动时扫描 `.trae/skills/` 自动加载，按语义触发 |
| GitHub Copilot | `copilot-skill/copilot-instructions.md` | 纯 Markdown 指令（无 frontmatter） | 项目根目录 `.github/copilot-instructions.md` | 工作区存在该文件时，Copilot Chat 自动注入为系统上下文 |

### 5.2 各平台调用示例

#### Claude（Claude Code 运行时）

```text
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
SKILL 动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
SKILL 动作：读取 /input/ 文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
SKILL 动作：读取文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 /output/proposals_<timestamp>.json 与 draft_<timestamp>.md，回复"已保存至该路径"。
```

#### OpenAI Custom GPT（ChatGPT）

```text
用户：我是硕士生，导师在做医疗大模型，帮我生成3个论题。
GPT 动作：解析对话提取谱系 → 执行四维创意 → 对话框输出 3 个结构化提案。

用户：读取我上传的导师项目书和同门论文，生成开题报告草稿。
GPT 动作：读取上传文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告（若启用 Code Interpreter 可生成可下载文件）。

用户：基于我粘贴的谱系信息，用跨域联想策略生成5个提案并保存为文件。
GPT 动作：解析粘贴谱系 → 跨域联想生成 5 个提案 → 通过 Code Interpreter 生成 proposals_<timestamp>.json 供下载。
```

#### Cursor（编辑器内对话）

```text
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
规则动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
规则动作：读取工作区文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
规则动作：读取工作区文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 output/proposals_<日期>.json 与 output/draft_<日期>.md，回复"已保存至该路径"。
```

#### Trae IDE（编辑器内对话）

```text
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
技能动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
技能动作：读取文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
技能动作：读取文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 /output/proposals_<timestamp>.json，回复"已保存至该路径"。
```

#### GitHub Copilot Chat

```text
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
Copilot 动作：解析对话提取谱系 → 执行四维创意 → Chat 中直接输出 3 个结构化提案。

用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
Copilot 动作：读取工作区文件解析谱系 → 生成提案并选最优 → Chat 中直出完整 Markdown 开题报告。

用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
Copilot 动作：读取工作区文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 output/proposals_YYYYMMDD.md，回复"已保存至该路径"。
```

---

## 6. 配置与环境变量

本项目不含传统环境变量配置（无 `.env`、无运行时配置文件）。各平台 Skill 的配置方式如下：

### 6.1 OpenAI Custom GPT — `config.json`

`openai-skill/config.json` 是 GPT 元信息记录文件（**非 OpenAI 官方导入文件**，Custom GPT Builder 不提供 JSON 批量导入入口），供团队协作时统一配置口径。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | GPT 名称（如 `ThesisArchitect`） |
| `description` | string | 简短描述（粘贴至 GPT Builder 的 Description 字段） |
| `capabilities` | string[] | 能力清单：`谱系解析`、`四维创意生成`、`硬约束校验`、`开题报告直出` |
| `suggested_starters` | string[] | 3–5 个建议开场白，可粘贴至 Conversation starters |

### 6.2 Cursor Rules — frontmatter 字段

`cursor-skill/thesis-architect.mdc` 顶部 frontmatter 字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `description` | string | 规则用途与触发场景描述，Cursor 据此做语义匹配 |
| `globs` | string | 文件模式匹配（本项目设为 `**/*.md`） |
| `alwaysApply` | boolean | 是否每次对话强制注入（本项目设为 `false`，按需触发） |

### 6.3 Claude / Trae — frontmatter 字段

`claude-skill/SKILL.md` 与 `trae-skill/SKILL.md` 顶部 frontmatter 字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | Skill 唯一标识（如 `thesis-architect`） |
| `description` | string | 能力描述与触发条件（Claude 要求 ≤200 字符，说明"做什么 + 何时触发"） |

### 6.4 运行时目录约定（非配置文件）

各平台 Skill 在运行时依赖以下约定目录（由用户在使用时创建，已纳入 `.gitignore` 忽略）：

| 目录 | 用途 | 创建时机 |
| --- | --- | --- |
| `/input/` | 放置谱系输入文件（`profile.json`、`lineage.md`） | 用户按需创建 |
| `/output/` | 文件输出落盘目录（`proposals_<timestamp>.json`、`draft_<timestamp>.md`） | Skill 在文件输出模式下自动创建 |

---

## 7. 部署与运行

### 7.1 Claude Skill 部署

1. 将 `claude-skill/` 目录下的全部内容（即 `SKILL.md`）复制到 Claude 运行时的 `/skills/` 目录下：
   - 用户级：`~/.claude/skills/thesis-architect/SKILL.md`
   - 项目级：`<项目根目录>/.claude/skills/thesis-architect/SKILL.md`
2. 重启 Claude 运行时，使其在启动时自动加载该 Skill 的 frontmatter（`name` 与 `description`）及正文指令。
3. 加载成功后，当用户请求涉及"生成论文选题 / 开题报告 / 分析导师项目谱系 / 同门论文"等意图时，Claude 将按 `description` 中的触发条件自动激活本技能。

### 7.2 OpenAI Custom GPT 部署

1. 登录 ChatGPT，进入 **Explore GPTs** → **+ Create** 进入 GPT Builder。
2. 在 **Configure** 标签页填写：
   - **Name**：`ThesisArchitect`
   - **Description**：`研究生开题智能导师，解析谱系、四维创意、硬约束修复、开题直出`
3. 将 `gpt-instructions.md` 的**全部内容**复制粘贴至 **Instructions** 文本框（本文件已是纯 Markdown 指令，可直接粘贴）。
4. **Conversation starters**：从 `config.json` 的 `suggested_starters` 字段中挑选 3–5 条粘贴进去。
5. 若需要文件读写能力，在 **Actions** 中按需配置文件服务 OpenAPI；若仅需生成可下载文件，启用 **Code Interpreter** 即可。
6. 点击 **Save** → 选择发布范围（Only me / Anyone with link / Public）。

### 7.3 Cursor Rules 部署

1. 在目标项目中创建（或确认已存在）`.cursor/rules/` 目录。
2. 将 `thesis-architect.mdc` 复制到 `.cursor/rules/thesis-architect.mdc`。
3. 重启 Cursor 或等待其自动加载规则文件。规则加载后会在状态栏 / Rules 面板中可见。
4. 因 `alwaysApply: false`，规则按需触发，不会在每次对话都强制注入，避免污染无关代码任务。

### 7.4 Trae Skill 部署

1. 将 `trae-skill/` 目录下的全部内容复制到 Trae IDE 工作区的 Skill 目录：
   ```
   <项目根目录>/.trae/skills/thesis-architect/SKILL.md
   ```
2. **自动加载**：Trae IDE 在启动时会扫描 `.trae/skills/` 目录，自动加载其中的 `SKILL.md`，解析 frontmatter 中的 `name` 与 `description` 字段，并将正文指令注入到底层大模型运行时的上下文中。无需手动注册或重启编辑器之外的步骤。
3. **验证加载**：启动 Trae IDE 后，在对话窗口中输入与开题相关的指令（如"帮我生成3个论题"），若技能被正确加载，模型会按 ThesisArchitect 工作流执行。

### 7.5 GitHub Copilot Chat 部署

**方式一：项目级自定义指令（推荐）**

1. 在项目根目录创建 `.github/` 目录（若不存在）。
2. 将 `copilot-instructions.md` 的全部内容复制到 `.github/copilot-instructions.md`。
3. GitHub Copilot Chat 会**自动读取**该文件作为项目级自定义指令，无需任何额外配置。
4. 在 Copilot Chat 中讨论论文选题/开题时，ThesisArchitect 行为自动激活。

**方式二：VS Code 设置级指令**

若希望指令在所有项目中生效，可通过 VS Code 设置配置：

1. 打开 VS Code 设置（`Ctrl+,` / `Cmd+,`）。
2. 搜索 `github.copilot.chat.codeGeneration.instructions`。
3. 点击"在 settings.json 中编辑"，按以下格式添加指令项：

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "<将 copilot-instructions.md 全文粘贴于此>"
    }
  ]
}
```

---

## 8. 扩展性设计

### 8.1 如何添加新平台 Skill 格式

当需要将 ThesisArchitect 能力扩展到新的 AI 平台（如 Windsurf、Continue、Cline 等）时，按以下步骤操作：

1. **创建独立目录**：在项目根目录创建 `<平台名>-skill/` 目录（如 `windsurf-skill/`），与现有 5 个平台目录平级。
2. **研究目标平台格式规范**：确认该平台 Skill 的原生格式要求（是否需要 frontmatter、frontmatter 字段名、文件命名约定、部署路径）。
3. **转译能力正文**：以 `ThesisMinerSkills设计文档.md` 为唯一能力源头，将五大核心能力（谱系解析、四维创意引擎、硬约束修复、开题直出、I/O 多态自适应）转译为目标平台格式，保持能力等价性。
4. **适配 I/O 通道**：根据目标平台原生交互能力调整 I/O 路由描述（如该平台是否支持文件读写、是否支持上传文件）。
5. **编写部署说明**：在 `<平台名>-skill/README.md` 中说明部署路径、触发机制与调用示例。
6. **更新本 README**：在第 2.1 节目录树、第 3 节技术栈表格、第 5.1 节 Skill 总览表格中补充新平台条目。
7. **更新 spec**：在 `.trae/specs/multi-platform-skills/spec.md` 中补充新平台的 Requirement 与 Scenario。

### 8.2 如何更新核心能力

当需要修改 ThesisArchitect 的核心能力（如新增创意策略、调整硬约束规则、修改开题模板）时，按以下顺序操作，确保所有平台产物同步演进：

1. **修改设计文档**：在 `ThesisMinerSkills设计文档.md` 中更新能力定义（这是唯一的能力源头）。
2. **逐平台重新转译**：依次更新 5 个平台目录下的 Skill 产物（`claude-skill/SKILL.md`、`openai-skill/gpt-instructions.md`、`cursor-skill/thesis-architect.mdc`、`trae-skill/SKILL.md`、`copilot-skill/copilot-instructions.md`），保持能力等价性。
3. **更新平台 README**：若能力变化影响部署或调用示例，同步更新各平台目录下的 `README.md`。
4. **更新本 README**：在第 4 节核心机制、第 5 节调用示例中同步更新。
5. **更新 spec 验收清单**：在 `.trae/specs/multi-platform-skills/` 下更新对应 Requirement 与 Scenario，确保验收依据与实际能力一致。

> **关键原则**：任何能力变更必须先改设计文档，再同步转译到所有平台产物，禁止直接修改单个平台产物而绕过设计文档，以避免跨平台能力漂移。

---

## 9. 常见问题与故障排除（FAQ）

| 问题 | 可能原因 | 解决方案 |
| --- | --- | --- |
| Claude 运行时未识别 Skill | `SKILL.md` 未放置在 `/skills/` 目录下，或 frontmatter 缺少 `name`/`description` 字段 | 确认部署路径为 `~/.claude/skills/thesis-architect/SKILL.md` 或项目级 `.claude/skills/thesis-architect/SKILL.md`；检查 frontmatter 字段完整且 `description` ≤200 字符 |
| OpenAI Custom GPT 粘贴 Instructions 后格式错乱 | 误将 YAML frontmatter 一起粘贴进 Instructions 字段 | `gpt-instructions.md` 已是纯 Markdown 指令，无 frontmatter，直接全文粘贴即可；不要粘贴 `config.json` 内容到 Instructions |
| Cursor 规则不触发 | `alwaysApply: false` 导致按需触发未命中，或 `globs` 模式不匹配当前文件 | 确认用户指令涉及开题话题（论文选题/导师项目/同门论文等）；确认当前工作文件匹配 `**/*.md`；若需强制触发可临时改为 `alwaysApply: true` 测试 |
| Trae IDE 未加载 Skill | `SKILL.md` 未放置在 `.trae/skills/thesis-architect/` 路径下 | 确认最终路径为 `<项目根目录>/.trae/skills/thesis-architect/SKILL.md`；重启 Trae IDE 触发重新扫描 |
| Copilot Chat 未生效 | `.github/copilot-instructions.md` 路径错误或文件名拼写错误 | 确认路径为项目根目录 `.github/copilot-instructions.md`（注意是 `.github` 不是 `github`）；确认文件无 YAML frontmatter |
| 生成的论题标题超过 20 字 | 硬约束自动修复未执行或运行时未按指令执行 | 检查用户指令是否明确触发 ThesisArchitect 行为；确认 Skill 已正确加载；标题超长时应由依存句法截取核心名词短语自动修复 |
| 候选论题未给自评分 | 运行时未按四维创意引擎工作流执行 | 确认 Skill 正文已加载；自评分为内部步骤，每个候选必须给出 `score` 字段（满分 10 分，<6 分过滤） |
| 文件输出未生成 | 用户未明确表达"保存/生成文件/输出到本地"意图，或 `output/` 目录无写入权限 | 文件输出需用户指令包含明确保存意图；确认运行时有文件写入能力（Claude/Cursor/Trae/Copilot 工作区原生支持，OpenAI 需启用 Code Interpreter） |
| 跨平台能力不一致 | 直接修改了单个平台产物而绕过设计文档 | 任何能力变更必须先改 `ThesisMinerSkills设计文档.md`，再同步转译到所有平台产物；参见第 8.2 节 |
| 文献综述出现伪造引用 | 运行时未遵守"不伪造文献"约束 | 文献综述只规划"检索方向"与"数量基线"（硕士 ≥30 / 博士 ≥50），不伪造具体作者、年份、期刊；若需真实文献需接入学术搜索 API（如 Semantic Scholar、arXiv） |
| 学位信息缺失时默认硕士 | 运行时未执行"缺失信息引导"步骤 | 学位信息缺失时必须先提问补齐，不得默认硕士；确认 Skill 已正确加载并按工作流第 1 步执行 |
