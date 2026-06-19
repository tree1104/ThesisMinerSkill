# ThesisArchitect — OpenAI Custom GPT Skill

本目录将 `ThesisMinerSkills设计文档.md`（ThesisArchitect v2.0）转译为 OpenAI Custom GPT 可用的指令产物，使同一套开题智能体能力可在 ChatGPT 中即插即用。

## 文件清单

| 文件 | 用途 |
| --- | --- |
| `gpt-instructions.md` | Custom GPT 的 Instructions 字段内容（纯 Markdown 指令，无 YAML frontmatter） |
| `config.json` | GPT 元信息记录（非 OpenAI 官方导入文件，供团队协作参考） |
| `README.md` | 本说明文档 |

## 一、导入 Custom GPT 步骤

1. 登录 ChatGPT，进入 **Explore GPTs** → **+ Create** 进入 GPT Builder。
2. 在 **Configure** 标签页填写：
   - **Name**：`ThesisArchitect`
   - **Description**：`研究生开题智能导师，解析谱系、四维创意、硬约束修复、开题直出`
3. 将 `gpt-instructions.md` 的**全部内容**复制粘贴至 **Instructions** 文本框。
   - 注意：Custom GPT 的 Instructions 字段不解析 YAML frontmatter，本文件已是纯 Markdown 指令，可直接粘贴。
4. **Conversation starters**：可从 `config.json` 的 `suggested_starters` 字段中挑选 3–5 条粘贴进去。
5. 若需要文件读写能力，在 **Actions** 中按下方"可选 Actions 配置"添加（可选）。
6. 点击 **Save** → 选择发布范围（Only me / Anyone with link / Public）。

## 二、config.json 的用途

`config.json` **不是 OpenAI 官方导入文件**，Custom GPT Builder 不提供 JSON 批量导入入口。它的作用是：

- 记录 GPT 的元信息（名称、描述、能力清单、建议开场白），便于团队协作时统一配置。
- 作为版本化产物，纳入 Git 管理，方便追踪能力演进。
- 团队成员可对照该文件手工在 GPT Builder 中填写对应字段，确保多人口径一致。

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | GPT 名称 |
| `description` | string | 简短描述 |
| `capabilities` | string[] | 能力清单（谱系解析、四维创意生成、硬约束校验、开题报告直出） |
| `suggested_starters` | string[] | 3–5 个建议开场白，可粘贴至 Conversation starters |

## 三、可选 Actions 配置

ThesisArchitect 默认以纯对话模式运行，无需 Actions。若需要文件读写或外部检索能力，可按需配置以下 GPT Actions：

### 3.1 文件读写 Action（可选）
若希望 GPT 能直接读写用户云盘或本地服务中的 `input/`、`output/` 目录，可配置一个自定义 Action，指向团队内部的文件服务 OpenAPI：

- **OpenAPI Schema**：定义 `/input/{filename}`（GET 读取谱系文件）与 `/output/{filename}`（POST 写入提案/草稿）两个端点。
- **Authentication**：建议使用 API Key 或 OAuth。
- **Privacy Policy**：填写团队隐私政策 URL。

配置后，GPT 可在用户说"读取 input 里的谱系"时调用 Action 获取文件，在用户说"保存到本地"时调用 Action 写入文件。

### 3.2 文献检索 Action（可选）
若希望文献综述部分能检索真实文献而非仅规划检索方向，可接入学术搜索 API（如 Semantic Scholar、arXiv）作为 Action。注意：接入后仍需遵守指令第八节"不伪造引用"约束，未检索到的文献不得编造。

### 3.3 Code Interpreter / Advanced Data Analysis
若仅需生成可下载的 `proposals_<timestamp>.json` 与 `draft_<timestamp>.md` 文件，无需配置 Action，直接在 GPT Builder 中启用 **Code Interpreter** 即可。GPT 会在用户要求"保存为文件"时生成可下载文件。

## 四、能力等价性

本目录产物与 `claude-skill/`、`cursor-skill/`、`trae-skill/`、`copilot-skill/` 在能力层面等价，均完整承载设计文档五大核心能力：

1. I/O 多态自适应（适配为 GPT 对话/上传文件双通道）
2. 谱系解析器（实体抽取 + 边缘探测）
3. 四维创意引擎（导师项目延伸、同门成果继承、跨域联想、矛盾驱动 + 自评分过滤）
4. 硬约束校验与自动修复器（标题 ≤20 字、学术日历、文献基线、逻辑自洽）
5. 开题报告直出（五大模块模板）

差异仅在于：Prompt 约束以 GPT 行为指令形式内化（不使用 SYSTEM/USER 分离模板），触发语法适配 Custom GPT 对话场景。
