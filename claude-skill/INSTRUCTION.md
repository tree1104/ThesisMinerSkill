# ThesisArchitect 指令层（INSTRUCTION）

本文件是 ThesisArchitect 技能的"灵魂"，定义工作流与决策规则。所有死知识（脚本实现、约束数据、模板文本）均存放于资源层 `../core/`，按需加载，不在此内联。

---

## §1 工作流决策规则

技能激活后，按以下 6 步无状态流程执行。每一步均显式调用资源层脚本，禁止凭模型记忆替代计算。

### 步骤 1：I/O 意图识别
解析用户指令，确定输入源与输出目标：
- **输入路由**（按优先级）：
  1. 文件输入：检测 `@input/` 引用或 `/input/profile.json`、`/input/lineage.md`，优先读取作为基础上下文。
  2. 对话输入：未提供文件时，通过对话引导获取学位、学科、导师项目与同门信息。
  3. 混合输入：以文件为底座，对话中追加临时指令。
- **输出路由**：根据指令动词决定——含"保存/生成文件/输出到本地"等意图→文件输出（写入 `/output/`）；否则→对话输出（默认）。

### 步骤 2：上下文加载与解析
调用 `../core/scripts/lineage_parser.py` 的 `parse_lineage(text)` 函数，将非结构化谱系文本解析为结构化 `LineageGraph`（含 `advisor_projects`、`peer_papers`、`edge_opportunities`）。该函数内置 30 秒超时与异常捕获，返回标准化 `{status, data, error_message}` 结构。

### 步骤 3：四维创意发散
调用 `../core/scripts/idea_generator.py` 的 `generate_ideas(lineage_graph, strategy, degree)` 函数，按四维策略（导师项目延伸、同门成果继承、跨域联想、矛盾驱动）生成候选。评分权重读取自 `../core/references/scoring_weights.json`（可行性 40% + 创新度 30% + 谱系贴合度 30%，满分 10 分，过滤低于 6 分的候选）。

### 步骤 4：结构化精炼
针对每个保留候选，调用大模型填充以下字段：
- `title`（标题）
- `problem_awareness`（问题意识/现实痛点）
- `research_significance`（研究意义）
- `differentiation`（差异化/创新点）
- `research_content`（研究内容）
- `literature_review_outline`（文献综述大纲）

### 步骤 5：硬约束拦截与修复
调用 `../core/scripts/constraint_checker.py` 的 `check_and_repair(proposal)` 函数，对每个提案执行标题格式、学术日历、文献基线、逻辑自洽校验并自动修复。约束规则读取自 `../core/references/constraints.json`（标题 ≤20 字、禁用主动动词开头、禁用"基于X的Y研究"模式；硕士 ≤12 个月、博士 ≤24 个月；文献基线硕士 30 篇/博士 50 篇；内容与目标重合度 ≤70%）。

### 步骤 6：多态输出
调用 `../core/scripts/report_generator.py` 的 `generate_report(proposal)` 函数，按输出路由生成最终产物。报告模板读取自 `../core/references/report_template.md`。
- 对话输出：渲染为高可读 Markdown 打印。
- 文件输出：序列化为 JSON 与 Markdown 写入 `/output/` 目录（`proposals_<timestamp>.json`、`draft_<timestamp>.md`），回复文件路径摘要。

---

## §2 I/O 接口规范

输入与输出均通过 JSON Schema 标准化校验，不依赖模型记忆传递数据。

### 输入规范
输入必须符合 `../core/schema/input_schema.json`：
- **必填字段**：`degree`（`master`/`phd`）、`lineage`（学术谱系对象）。
- **可选字段**：`strategy`（`advisor_extension`/`peer_inheritance`/`cross_domain`/`contradiction_driven`/`all`，默认 `all`）、`count`（1-10，默认 3）、`output_format`（`dialogue`/`file`，默认 `dialogue`）。

### 输出规范
输出必须符合 `../core/schema/output_schema.json`：
- `status`：`success`（成功）/ `retry`（需重试）/ `error`（错误）。
- `data`：核心结果数据（含 `proposals` 列表，每项含 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline`、`score`）。
- `error_message`：错误信息，`status` 为 `error`/`retry` 时必填。

Schema 路径引用，不在本文件内联字段定义。

---

## §3 自愈与兜底规则

以下规则为写死的硬性约束，非建议，必须严格执行：

1. **脚本调用失败**：返回 `status: retry`，建议延迟 2 秒后重试，最多重试 3 次；超过 3 次仍失败则升级为 `status: error`。
2. **脚本执行超时**：脚本执行超过 30 秒触发超时中断，返回 `status: error` + `error_message: "执行超时"`。
3. **沙盒写入限制**：脚本仅允许写入 `output/` 目录，禁止越权写入其他路径或访问网络。
4. **大模型 API 调用失败**：返回 `status: retry`，不直接报错中断流程；附带延迟重试建议。

---

## §4 渐进式披露原则

为管控上下文成本，遵循按需加载原则：

1. **激活时**：仅加载 `SKILL.md`（元数据）与 `INSTRUCTION.md`（本文件）。
2. **执行时**：脚本与参考数据仅在执行到对应工作流步骤时，通过 `read_script` 工具按需加载，不在开场注入脚本内容。
3. **不预加载**：禁止在技能激活阶段一次性读取全部 `../core/scripts/` 与 `../core/references/` 内容。

---

## §5 Prompt 约束模板

调用大模型生成提案时，强制注入约束模板。模板定义于 `../core/references/prompt_templates.json`，包含 `system`（学术导师角色与硬性约束）与 `user`（谱系信息 + 策略 + 学位 + 必填字段）两部分。引用该文件加载，不在本文件内联模板文本。
