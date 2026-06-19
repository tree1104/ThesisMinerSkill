# ThesisArchitect — GitHub Copilot Chat 自定义指令部署说明

本目录提供 ThesisArchitect（研究生开题阶段智能体技能）的 GitHub Copilot Chat 适配版本。能力与 Claude / OpenAI / Cursor / Trae 版本等价，仅在外层格式与触发语法上做 Copilot 适配。

## 产物清单

| 文件 | 说明 |
| --- | --- |
| `copilot-instructions.md` | 纯 Markdown 指令文本，无 YAML frontmatter，承载 ThesisArchitect 全部能力 |

## 部署方式

### 方式一：项目级自定义指令（推荐）

1. 在项目根目录创建 `.github/` 目录（若不存在）。
2. 将 `copilot-instructions.md` 的全部内容复制到 `.github/copilot-instructions.md`。
3. GitHub Copilot Chat 会**自动读取**该文件作为项目级自定义指令，无需任何额外配置。
4. 在 Copilot Chat 中讨论论文选题/开题时，ThesisArchitect 行为自动激活。

目录结构示例：

```
你的项目/
├── .github/
│   └── copilot-instructions.md   ← 从本目录复制而来
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

## GitHub Copilot Chat 如何读取指令

- **自动加载**：当工作区存在 `.github/copilot-instructions.md` 时，Copilot Chat 在每次会话启动时自动将其注入为系统级上下文，无需用户手动 `@` 提及。
- **作用范围**：项目级指令仅对当前工作区生效，跟随仓库走，团队成员克隆后即可共享同一套 ThesisArchitect 行为。
- **格式要求**：Copilot 不解析 YAML frontmatter，因此本指令为纯 Markdown 文本。

## 调用示例

部署完成后，在 Copilot Chat 中直接用自然语言触发：

### 示例 1：纯对话快速发散
```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
```
Copilot 会解析对话提取谱系 → 执行四维创意 → 在 Chat 中直接输出 3 个结构化提案。

### 示例 2：读取工作区文件 + 直出开题报告
```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```
Copilot 会读取工作区文件解析谱系 → 生成提案并选最优 → 在 Chat 中直出完整 Markdown 开题报告。

### 示例 3：混合输入 + 文件落盘
```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
```
Copilot 会读取工作区文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `output/proposals_YYYYMMDD.md`，并回复路径。

## 能力清单

本 Copilot 指令完整承载以下能力（与设计文档 `ThesisMinerSkills设计文档.md` 对齐）：

- **I/O 多态路由**：工作区文件 / 对话 / 混合输入；对话 / 文件输出
- **谱系解析器**：实体抽取 + 边缘探测
- **四维创意引擎**：导师项目延伸、同门成果继承、跨域联想、矛盾驱动 + 自评分过滤（可行性 40% + 创新度 30% + 谱系贴合度 30%，过滤 < 6 分）
- **硬约束校验与自动修复器**：标题 ≤ 20 字、学术日历、文献基线、逻辑自洽
- **开题报告直出模板**：选题依据、国内外研究现状、研究内容与关键问题、研究方案与可行性、进度安排五大模块
- **执行工作流**：I/O 意图识别 → 上下文加载 → 四维创意 → 结构化精炼 → 硬约束修复 → 多态输出

## 与其他平台版本的等价性

本目录产物与 `claude-skill/`、`openai-skill/`、`cursor-skill/`、`trae-skill/` 中的 Skill 在能力层面完全等价，差异仅在于：
- 格式包装：纯 Markdown 无 frontmatter（Copilot 不解析 frontmatter）
- 触发语法：依赖 Copilot Chat 的自然语言识别与 `@` 文件提及机制
- I/O 通道：以 Copilot 工作区文件作为谱系输入源，以 Chat 作为默认输出通道
