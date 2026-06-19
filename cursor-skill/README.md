# Cursor Rules — ThesisArchitect

研究生开题论题生成规则（ThesisArchitect v2.0）的 Cursor 编辑器适配产物。

## 产物清单

| 文件 | 说明 |
| --- | --- |
| `thesis-architect.mdc` | Cursor 规则文件，含专属 frontmatter 与等价能力正文 |

## 部署方式

1. 在目标项目中创建（或确认已存在）`.cursor/rules/` 目录。
2. 将 `thesis-architect.mdc` 复制到 `.cursor/rules/` 目录下：
   ```
   .cursor/rules/thesis-architect.mdc
   ```
3. 重启 Cursor 或等待其自动加载规则文件。规则加载后会在状态栏 / Rules 面板中可见。

## 触发机制

Cursor 会根据 `.mdc` 文件 frontmatter 中的两个字段自动决定何时应用该规则：

- **`description`**：描述规则用途与触发场景。Cursor 的 AI 助手会基于语义匹配用户当前讨论的话题（论文选题、导师项目、同门论文、开题报告、研究综述等）决定是否激活本规则。
- **`globs`**：文件模式匹配。本规则设为 `**/*.md`，表示当用户在任意 Markdown 文件上下文中工作时可作为候选；但因 `alwaysApply: false`，最终是否触发仍由 description 语义匹配决定。
- **`alwaysApply: false`**：按需触发，不会在每次对话都强制注入，避免污染无关代码任务。

## 能力承载

`thesis-architect.mdc` 正文承载与 Claude Skill 等价的全部能力，仅在外层格式与触发语法上做 Cursor 适配：

- I/O 多态路由（适配 Cursor：可读取工作区文件作为谱系输入，可在对话中输出，也可写入 `output/` 目录）
- 谱系解析器（实体抽取 + 边缘探测）
- 四维创意涌现引擎（导师项目延伸 / 同门成果继承 / 跨域联想 / 矛盾驱动）+ 自评分机制（可行性 40% + 创新度 30% + 谱系贴合度 30%，过滤 < 6 分）
- 硬约束校验与自动修复器（标题 ≤ 20 字、学术日历、文献基线、逻辑自洽）
- 开题报告直出模板（五大模块）
- 执行工作流（无状态六步）

## 调用示例

部署完成后，在 Cursor 对话框中直接用自然语言触发即可：

### 场景 1：纯对话输入输出（快速发散）
```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
```
规则动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

### 场景 2：工作区文件输入 + 对话输出（详尽开题）
```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```
规则动作：读取工作区文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

### 场景 3：混合输入 + 文件输出（沉淀落盘）
```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
```
规则动作：读取工作区文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `output/proposals_<日期>.json` 与 `output/draft_<日期>.md`，回复“已保存至该路径”。

## 验证清单

- [x] `.mdc` 文件含 Cursor 专属 frontmatter（`description`、`globs`、`alwaysApply`）
- [x] 正文承载等价能力（谱系解析 → 四维创意 → 硬约束修复 → 开题直出）
- [x] 部署路径说明为 `.cursor/rules/`
