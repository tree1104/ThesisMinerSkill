# ThesisArchitect — GitHub Copilot Chat 自定义指令（三层结构）

本目录提供 ThesisArchitect（研究生开题阶段智能体技能）的 GitHub Copilot Chat 适配版本，采用**三层物理结构**，能力与 Claude / OpenAI / Cursor / Trae 版本等价，仅在外层格式与触发语法上做 Copilot 适配。

## 三层结构

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| **元数据层** | `skill.json` | 唯一标识（name）、版本（version）、触发条件（description ≤120 字符 + triggers）、资源路径映射。不含工作流细节。 |
| **指令层** | `copilot-instructions.md` | 纯 Markdown 指令文本，**无 YAML frontmatter**（Copilot 不解析）。定义工作流决策规则、I/O 接口规范、自愈兜底、渐进式披露、Prompt 约束，引用 `../core/` 资源而非内联死知识。 |
| **资源层** | `../core/` | 平台无关的共享资源：`scripts/`（可执行 Python 脚本）、`references/`（静态约束/权重/模板数据）、`schema/`（I/O JSON Schema）。按需加载，不在 Skill 激活时全量注入。 |

```
copilot-skill/
├── skill.json                  ← 元数据层
├── copilot-instructions.md     ← 指令层（部署到 .github/）
└── ../core/                    ← 资源层（共享）
    ├── scripts/                lineage_parser.py / idea_generator.py / constraint_checker.py / report_generator.py
    ├── references/             constraints.json / scoring_weights.json / report_template.md / prompt_templates.json
    └── schema/                 input_schema.json / output_schema.json
```

## 部署方式

### 方式一：项目级自定义指令（推荐）

1. 在项目根目录创建 `.github/` 目录（若不存在）。
2. 将 `copilot-instructions.md` 的全部内容复制到 `.github/copilot-instructions.md`。
3. GitHub Copilot Chat 会**自动读取**该文件作为项目级自定义指令，无需任何额外配置。
4. 在 Copilot Chat 中讨论论文选题/开题时，ThesisArchitect 行为自动激活。

> 注：仅 `copilot-instructions.md` 需要复制到 `.github/`。`skill.json` 与 `../core/` 资源层保留在本仓库中作为团队协作参考与脚本来源；指令层通过相对路径 `../core/` 引用资源，部署时请保持 `core/` 目录与 `.github/copilot-instructions.md` 的相对位置，或将 `../core/` 路径按实际部署结构调整。

目录结构示例：

```
你的项目/
├── .github/
│   └── copilot-instructions.md   ← 从本目录复制而来
├── core/                          ← 资源层（保留，供指令层引用）
│   ├── scripts/
│   ├── references/
│   └── schema/
├── input/                         ← 可选：放置谱系文件
│   ├── profile.json
│   └── lineage.md
└── output/                        ← 可选：文件输出落盘目录（自动创建）
```

### 方式二：VS Code 设置级指令

若希望指令在所有项目中生效，或不想提交 `.github/copilot-instructions.md` 到仓库，可通过 VS Code 设置配置：

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

> 注：`codeGeneration.instructions` 适合代码生成场景；若仅需对话级行为约束，优先使用方式一的 `.github/copilot-instructions.md`。

## skill.json 用途

`skill.json` 是**团队协作参考文件**，Copilot 运行时本身不解析它（Copilot 仅读取 `.github/copilot-instructions.md`）。其用途为：

- **能力索引**：`description`（≤120 字符）与 `triggers` 数组让团队成员一眼看清"这个 Skill 做什么、何时触发"，便于跨平台对齐。
- **资源定位**：`resources` 字段映射 `scripts` / `references` / `schema` 的相对路径，方便开发者与 IDE 工具快速跳转到共享资源层。
- **版本治理**：`version` 字段支持多平台 Skill 的版本对齐与升级追踪。
- **跨平台等价性校验**：与 `claude-skill/`、`openai-skill/`、`cursor-skill/`、`trae-skill/` 的元数据文件对照，确认能力等价。

## 渐进式披露机制

为控制上下文成本（Token 效率），本 Skill 不在激活时全量注入资源层内容：

- **开场轻量**：Skill 激活时仅注入指令层（`copilot-instructions.md`），描述决策规则与引用路径。
- **按需加载**：仅当模型确认"需要执行计算"（解析谱系、生成提案、校验约束、生成报告）时，才主动读取 `../core/scripts/` 对应脚本与 `../core/references/` 对应数据。
- **引用优先**：约束数值、模板文本、评分权重等死知识一律留在 `../core/references/`，指令层只引用不重复。

## 自愈与兜底机制

指令层与脚本层内置错误处理预案，避免执行出错即中断：

- **API 失败重试**：调用大模型 API 或脚本失败时返回 `status: retry`，延迟 2 秒重试，最多 3 次；耗尽后返回 `status: error`。
- **超时中断**：脚本执行超过 30 秒触发超时，返回 `status: error` + `error_message: "执行超时"`。
- **沙盒执行**：脚本在受限沙盒运行，禁止网络访问与文件系统越权写入，仅允许写入 `output/` 目录（由 `validate_write_path` 强制校验）。
- **标准化 I/O**：所有脚本返回 `{status, data, error_message}` 结构（见 `../core/schema/output_schema.json`），模型依据 `status` 自主决定继续 / 重试 / 报错。

## GitHub Copilot Chat 如何读取指令

- **自动加载**：当工作区存在 `.github/copilot-instructions.md` 时，Copilot Chat 在每次会话启动时自动将其注入为系统级上下文，无需用户手动 `@` 提及。
- **作用范围**：项目级指令仅对当前工作区生效，跟随仓库走，团队成员克隆后即可共享同一套 ThesisArchitect 行为。
- **格式要求**：Copilot 不解析 YAML frontmatter，因此 `copilot-instructions.md` 为纯 Markdown 文本。

## 调用示例

部署完成后，在 Copilot Chat 中直接用自然语言触发：

### 示例 1：纯对话快速发散

```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
```

Copilot 解析对话提取谱系 → 调用 `lineage_parser.parse_lineage` → 调用 `idea_generator.generate_ideas`（strategy=all）→ 自评分过滤 → 在 Chat 中直接输出 3 个结构化提案。

### 示例 2：读取工作区文件 + 直出开题报告

```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```

Copilot 读取工作区文件解析谱系 → 生成提案并选最优 → 调用 `constraint_checker.check_and_repair` 校验修复 → 调用 `report_generator.generate_report` 填充 `report_template.md` → 在 Chat 中直出完整 Markdown 开题报告。

### 示例 3：混合输入 + 文件落盘

```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
```

Copilot 读取工作区文件底座 + 追加 RAG 跨域指令（strategy=cross_domain）→ 生成提案 → 沙盒校验后写入 `output/draft_YYYYMMDD_HHMMSS.md`，并回复路径摘要。

## 与其他平台版本的等价性

本目录产物与 `claude-skill/`、`openai-skill/`、`cursor-skill/`、`trae-skill/` 中的 Skill 在能力层面完全等价，差异仅在于：

- **格式包装**：纯 Markdown 无 frontmatter（Copilot 不解析 frontmatter），元数据独立为 `skill.json`。
- **触发语法**：依赖 Copilot Chat 的自然语言识别与 `@` 文件提及机制。
- **I/O 通道**：以 Copilot 工作区文件作为谱系输入源，以 Chat 作为默认输出通道。
- **资源引用**：通过相对路径 `../core/` 引用共享资源层，与其他平台共用同一套脚本与参考数据。
