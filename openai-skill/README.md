# ThesisArchitect — OpenAI Custom GPT Skill

本目录将 ThesisArchitect（研究生开题智能导师 v2.1）转译为 OpenAI Custom GPT 可用的指令产物，采用**三层物理结构**，使同一套开题智能体能力可在 ChatGPT 中即插即用，同时复用平台无关的共享资源层 `../core/`。

## 一、三层结构

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| **元数据层** | `skill.json` | 唯一标识（name）、版本（version）、触发条件（description ≤120 字符）、触发关键词（triggers）、资源指针（resources）。供团队协作与调度参考。 |
| **指令层** | `gpt-instructions.md` | 工作流决策规则、I/O 接口规范、自愈与兜底规则、渐进式披露原则、Prompt 约束。无 YAML frontmatter，可直接粘贴至 Custom GPT Instructions 字段。 |
| **资源层** | `../core/` | 平台无关的共享资源：`scripts/`（4 个可执行 Python 脚本）、`references/`（约束/权重/模板数据）、`schema/`（输入输出 JSON Schema）。按需引用，不在开场注入。 |

另外保留 `config.json` 作为 GPT Builder 配置参考（非官方导入文件）。

### 文件清单

| 文件 | 用途 |
| --- | --- |
| `skill.json` | 元数据层：标识、版本、触发条件、资源指针（团队协作参考） |
| `gpt-instructions.md` | 指令层：Custom GPT 的 Instructions 字段内容（纯 Markdown，无 frontmatter） |
| `config.json` | GPT Builder 配置参考（名称、描述、能力清单、建议开场白） |
| `README.md` | 本说明文档 |

## 二、导入 Custom GPT 步骤

1. 登录 ChatGPT，进入 **Explore GPTs** → **+ Create** 进入 GPT Builder。
2. 在 **Configure** 标签页填写：
   - **Name**：`ThesisArchitect`
   - **Description**：可参考 `skill.json` 的 `description` 字段或 `config.json` 的 `description`。
3. 将 `gpt-instructions.md` 的**全部内容**复制粘贴至 **Instructions** 文本框。
   - 注意：Custom GPT 的 Instructions 字段不解析 YAML frontmatter，本文件已是纯 Markdown 指令，可直接粘贴。
4. **Conversation starters**：可从 `config.json` 的 `suggested_starters` 字段中挑选 3–5 条粘贴进去。
5. 若需要文件读写能力，在 **Actions** 中按需配置（可选），或启用 **Code Interpreter** 以生成可下载文件。
6. 点击 **Save** → 选择发布范围（Only me / Anyone with link / Public）。

## 三、skill.json 的用途

`skill.json` **不是 OpenAI 官方导入文件**，Custom GPT Builder 不提供 JSON 批量导入入口。它的作用是：

- 作为**元数据层**，记录 Skill 的唯一标识、版本、触发条件与资源指针，便于团队协作时统一口径。
- `triggers` 字段列出触发关键词（论文选题、开题报告、导师项目、同门论文），供调度系统或人工快速匹配使用场景。
- `resources` 字段声明对 `../core/` 资源层的引用路径，明确指令层与资源层的依赖关系。
- 作为版本化产物，纳入 Git 管理，方便追踪能力演进。

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | Skill 唯一标识（`thesis-architect`） |
| `version` | string | 版本号（`2.1`） |
| `description` | string | 简短描述（≤120 字符），说明做什么 + 何时触发 |
| `triggers` | string[] | 触发关键词数组 |
| `instruction_file` | string | 指令层文件名（`gpt-instructions.md`） |
| `resources` | object | 资源层引用路径（scripts / references / schema） |

## 四、渐进式披露与自愈机制

### 4.1 渐进式披露（Token 效率）
为控制上下文成本，指令层遵循渐进式披露原则：
- **不在开场注入**：Skill 激活时，`../core/scripts/` 与 `../core/references/` 的内容不进入上下文。
- **按需加载**：仅当确认"需要执行计算"（解析谱系、生成提案、校验约束、直出报告）时，才主动读取对应脚本与参考文件。
- **决策规则内化，死知识外置**：`gpt-instructions.md` 仅承载决策规则；约束数值、评分权重、模板文本等死知识外置于 `../core/`。

### 4.2 自愈与兜底
指令层与脚本层内置错误处理预案：
- **API 失败重试**：调用失败返回 `status: retry`，延迟 2 秒重试，最多 3 次。
- **超时中断**：单次脚本执行超过 30 秒触发超时，返回 `status: error` + "执行超时"。脚本内置 `@timeout(30)` 装饰器。
- **沙盒执行**：脚本仅允许写入 `output/` 目录，越权写入触发 `PermissionError`。
- **标准化输出**：所有脚本返回 `{status, data, error_message}` 结构，模型依据 status 自主决定继续 / 重试 / 报错。

## 五、能力等价性

本目录产物与 `claude-skill/`、`cursor-skill/`、`trae-skill/`、`copilot-skill/` 在能力层面等价，均完整承载五大核心能力（I/O 多态自适应、谱系解析、四维创意引擎、硬约束校验与自动修复、开题报告直出），并共享同一套 `../core/` 资源层。差异仅在于触发语法与指令载体适配各平台特性。

## 六、调用示例

**示例 1：纯对话输入输出（快速发散）**
> 用户："我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。"
> 行为：解析对话提取谱系 → 调用 `lineage_parser.parse_lineage` → 调用 `idea_generator.generate_ideas` → 调用 `constraint_checker.check_and_repair` → 对话框直接输出 3 个结构化提案。

**示例 2：文件输入 + 对话输出（详尽开题）**
> 用户："读取我上传的导师项目书和同门论文，生成开题报告草稿，直接发给我。"
> 行为：读取上传文件解析谱系 → 生成提案并选最优 → 调用 `report_generator.generate_report` 按 `report_template.md` 五大模块 → 对话框直出完整 Markdown 开题报告。

**示例 3：混合输入 + 文件输出（沉淀落盘）**
> 用户："基于我粘贴的谱系信息，用跨域联想策略生成5个提案并保存为文件。"
> 行为：解析粘贴谱系 → 指定 `strategy: cross_domain` 生成 5 个提案 → 硬约束修复 → 启用 Code Interpreter 生成 `proposals_<timestamp>.json` 供下载。
