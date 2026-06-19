# Cursor Rules — ThesisArchitect

研究生开题论题生成规则（ThesisArchitect v2.0）的 Cursor 编辑器适配产物，采用三层结构。

## 三层结构

本产物遵循"元数据层 + 指令层 + 资源层"三层物理结构，职责分明：

| 层级 | 载体 | 职责 |
| --- | --- | --- |
| 元数据层 | `thesis-architect.mdc` 的 frontmatter | 仅含 `description`（≤120 字符）、`globs`、`alwaysApply`，供 Cursor 调度系统语义匹配触发 |
| 指令层 | `thesis-architect.mdc` 的正文 | 定义工作流决策规则、I/O 接口规范、自愈兜底、渐进式披露、Prompt 约束，不含死知识 |
| 资源层 | `../core/`（scripts/、references/、schema/） | 平台无关的可执行脚本、静态参考数据、I/O Schema，按需加载 |

指令层不再内联约束数据、评分权重、模板与 Schema，全部下沉至 `../core/` 资源层引用，降低上下文成本。

## 产物清单

| 文件 | 说明 |
| --- | --- |
| `thesis-architect.mdc` | Cursor 规则文件，frontmatter（元数据层）+ 正文（指令层）合一 |
| `../core/` | 共享资源层，承载脚本、参考数据、I/O Schema |

## 部署方式

1. 在目标项目中创建（或确认已存在）`.cursor/rules/` 目录。
2. 将 `thesis-architect.mdc` 复制到 `.cursor/rules/`：
   ```
   .cursor/rules/thesis-architect.mdc
   ```
3. 将 `core/` 目录复制到项目根：
   ```
   <项目根>/core/
   ```
4. 重启 Cursor 或等待其自动加载规则文件，规则加载后会在 Rules 面板中可见。

> **路径提示**：`thesis-architect.mdc` 正文以 `../core/` 引用资源层（对应源仓库中 `cursor-skill/` 与 `core/` 的同级关系）。部署时请确保 `core/` 相对 `.cursor/rules/thesis-architect.mdc` 可达：若将 `core/` 置于项目根，可把正文中的 `../core/` 调整为 `../../core/`；或将 `core/` 放到 `.cursor/core/`，以保持 `../core/` 原样生效。

## 触发机制

Cursor 依据 `.mdc` frontmatter 自动决定何时应用规则：

- **`description`**：精简至 ≤120 字符，描述用途与触发场景。Cursor AI 基于语义匹配用户当前讨论话题（论文选题、导师项目、同门论文、开题报告、研究综述、谱系挖掘等）决定是否激活。
- **`globs: **/*.md`**：当用户在任意 Markdown 文件上下文中工作时作为候选。
- **`alwaysApply: false`**：按需触发，不在每次对话强制注入，避免污染无关代码任务。

## 渐进式披露

为优化 Token 成本，本规则激活时**不在开场注入** `../core/` 下脚本与参考数据全文：

- frontmatter `description` 精简至 ≤120 字符，便于调度系统快速匹配。
- 仅当模型在工作流中确认"需要执行计算 / 需要读取约束 / 需要模板"时，才主动读取对应文件（如执行到谱系解析步才加载 `lineage_parser.py`）。
- 约束数据、评分权重、模板、Schema 均作为外部资源按需加载，而非内联在指令层。

## 自愈与兜底机制

指令层与脚本层内置错误处理预案，模型依据输出 `status` 自主决策：

- **API 失败重试**：调用大模型 API 失败 → 返回 `status: retry` + `error_message`，延迟 2 秒重试；连续失败 3 次升级为 `status: error`。
- **超时中断**：单脚本执行超过 30 秒 → 触发超时中断，返回 `status: error` + `error_message: "执行超时"`。
- **沙盒执行**：脚本在受限沙盒运行，禁止网络访问；文件系统仅允许写入 `output/` 目录。
- **输入校验失败**：输入不符合 `input_schema.json` → 返回 `status: error` + 缺失字段清单，引导补全。

## I/O 接口规范

去上下文化 I/O，统一以 `../core/schema/` 下 JSON Schema 校验，不依赖模型记忆：

- **输入**（`../core/schema/input_schema.json`）：`degree`（master/phd）、`lineage`（导师项目 + 同门论文 + 边缘探测）、`strategy`、`count`、`output_format`。
- **输出**（`../core/schema/output_schema.json`）：`status`（success/retry/error）、`data`（含 `proposals[]`）、`error_message`（error/retry 时必填）。

## 调用示例

部署完成后，在 Cursor 对话框中直接用自然语言触发：

### 场景 1：纯对话输入输出（快速发散）
```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成 3 个论题。
```
规则动作：解析对话提取谱系 → 调用 `lineage_parser.py` + `idea_generator.py` 执行四维创意 → 对话框直接输出 3 个结构化提案（`status: success`）。

### 场景 2：工作区文件输入 + 对话输出（详尽开题）
```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```
规则动作：读取工作区文件解析谱系 → 生成提案并选最优 → 经 `constraint_checker.py` 硬约束修复 → 按 `report_template.md` 对话框直出完整 Markdown 开题报告。

### 场景 3：混合输入 + 文件输出（沉淀落盘）
```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成 5 个提案，保存到本地。
```
规则动作：读取工作区文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `output/proposals_<日期>.json` 与 `output/draft_<日期>.md`，回复"已保存至该路径"。

## 验证清单

- [x] `.mdc` frontmatter 为元数据层（`description` ≤120 字符、`globs`、`alwaysApply: false`）
- [x] `.mdc` 正文为指令层，6 节决策规则引用 `../core/` 资源层，无内联死知识
- [x] 资源层 `../core/` 承载脚本、参考数据、I/O Schema，按需加载
- [x] 自愈兜底（API 重试 / 超时 30 秒 / 沙盒仅写 output/）
- [x] 渐进式披露，不在开场注入资源全文
- [x] 部署路径说明为 `.cursor/rules/` + 项目根 `core/`
