# ThesisArchitect 指令层（INSTRUCTION）

本文件定义 ThesisArchitect Skill 的工作流决策规则、I/O 接口规范、自愈兜底逻辑与 Prompt 约束。所有死知识（约束规则、评分权重、模板）与可执行逻辑均下沉至资源层 `../core/`，按需加载，不在 Skill 激活时全量注入上下文。

## §1 工作流决策规则

当运行时调用 `thesis-architect` 技能时，按以下无状态 6 步流程执行。每一步均引用资源层脚本，禁止凭空生成结构化数据。

### 步骤 1：I/O 意图识别
解析用户指令，确定输入源与输出目标：
- **输入路由**（按优先级）：文件输入（`@input/` 或检测 `/input/profile.json`、`/input/lineage.md`）→ 对话输入 → 混合输入（文件底座 + 对话追加指令）。
- **输出路由**：用户指令含「保存/生成文件/输出到本地」→ 文件输出（写入 `/output/`）；否则默认对话输出（Markdown 打印）。

### 步骤 2：上下文加载与谱系解析
调用 `../core/scripts/lineage_parser.py` 的 `parse_lineage(text)` 函数，将非结构化谱系文本解析为结构化 `LineageGraph`：
- 实体抽取：导师项目（name、objective）、同门论文（title、method、limitation）。
- 边缘探测：标记「未来工作/受限于算力/数据未展开」等高价值切入点。
- 返回标准化输出（见 §2），`data` 含 `advisor_projects`、`peer_papers`、`edge_opportunities` 三数组。

### 步骤 3：四维创意发散
调用 `../core/scripts/idea_generator.py` 的 `generate_ideas(lineage_graph, strategy, degree)` 函数，按策略生成候选：
- 四策略：`advisor_extension`（导师项目延伸）、`peer_inheritance`（同门成果继承）、`cross_domain`（跨域联想）、`contradiction_driven`（矛盾驱动）。`strategy="all"` 时四策略并行。
- 自评分：可行性(40%) + 创新度(30%) + 谱系贴合度(30%)，权重读取自 `../core/references/scoring_weights.json`，过滤低于阈值（默认 6 分）的候选。
- 返回 Top 3-5 个方向，按分数降序排列。

### 步骤 4：结构化精炼
针对每个候选，调用大模型填充 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline` 字段。Prompt 约束见 §5。

### 步骤 5：硬约束拦截与自动修复
调用 `../core/scripts/constraint_checker.py` 的 `check_and_repair(proposal)` 函数，对每个提案执行：
- **标题格式**：≤20 字、禁主动动词开头、禁「基于X的Y研究」模式；超长截取核心名词短语，动词前置自动转名词性短语。
- **学术日历**：硕士 ≤12 月、博士 ≤24 月；超期注入「分阶段并行执行」降级策略。
- **文献基线**：硕士 ≥30 篇、博士 ≥50 篇；不足时注入基线要求提示。
- **逻辑自洽**：研究内容与意义重合度 >70% 标记 `WARNING`。
- 约束规则读取自 `../core/references/constraints.json`，返回 `repaired_proposal`、`repairs`、`warnings`。

### 步骤 6：多态输出
- **对话输出**：将结构化提案与开题草稿渲染为 Markdown 打印至对话框。
- **文件输出**：调用 `../core/scripts/report_generator.py` 的 `generate_report(proposal)` 函数，读取 `../core/references/report_template.md` 模板填充五大模块，写入 `/output/draft_<timestamp>.md`；提案列表写入 `/output/proposals_<timestamp>.json`。回复文件路径摘要。

## §2 I/O 接口规范

本 Skill 采用去上下文化 I/O，输入输出均通过 JSON Schema 标准化，不依赖模型记忆传递数据。

### 输入 Schema
引用 `../core/schema/input_schema.json`，必填字段：
- `degree`（枚举：`master` / `phd`）：学位级别。
- `lineage`（对象）：学术谱系，含 `advisor_projects`、`peer_papers`、`edge_opportunities`。
- 可选：`strategy`（枚举：四策略 + `all`，默认 `all`）、`count`（1-10，默认 3）、`output_format`（`dialogue` / `file`，默认 `dialogue`）。

### 输出 Schema
引用 `../core/schema/output_schema.json`，标准化结构：
- `status`（枚举：`success` / `retry` / `error`）：执行状态。模型据此自主决定继续 / 重试 / 报错。
- `data`（对象）：核心结果，`proposals` 数组含 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline`、`score` 七字段。
- `error_message`（字符串）：`status` 为 `error` 或 `retry` 时必填，描述错误原因。

所有脚本函数均返回此三字段结构，模型按 `status` 决策后续动作。

## §3 自愈与兜底规则

### API 失败重试
当调用大模型 API 失败时，返回 `status: "retry"` 并附带 2 秒延迟重试建议，不直接报错中断。脚本层（如 `idea_generator.py`）内置 `max_retries=3`、`retry_delay=2` 秒的重试装饰器，重试耗尽方返回 `status: "error"`。

### 超时中断
所有脚本主函数均经 `@timeout(30)` 装饰器包装（基于 threading 实现，兼容 Windows）。执行超过 30 秒触发超时中断，返回 `status: "error"` + `error_message: "执行超时（超过 30 秒）"`。

### 沙盒执行
脚本在受限沙盒中运行，禁止网络访问与文件系统越权写入。所有脚本内置 `validate_write_path(path)` 校验函数，仅允许写入 `output/` 目录，越权写入抛出 `PermissionError`。

## §4 渐进式披露

为管控上下文成本，本 Skill 采用渐进式披露策略：

1. **Skill 激活时**：仅加载元数据层 `SKILL.md` 与指令层 `INSTRUCTION.md` 注入上下文。
2. **脚本按需加载**：`../core/scripts/` 下的 4 个 Python 脚本不在开场注入；仅当模型确认「需要执行计算」（如解析谱系、生成提案、校验约束、直出报告）时，主动调用对应脚本函数加载执行。
3. **参考数据按需读取**：`../core/references/` 下的约束规则、评分权重、模板、Prompt 模板由脚本在执行时读取，不进入 Skill 上下文。

此机制确保 Skill 激活时上下文成本最小化，死知识与可执行逻辑延迟到真正需要时才加载。

## §5 Prompt 约束

调用大模型生成提案时，强制注入 `../core/references/prompt_templates.json` 中的约束模板：

- **SYSTEM 约束**：严谨学术导师角色；标题 ≤20 字、无主动动词开头、杜绝「基于X的Y研究」套路；必须基于谱系生成严禁捏造；输出严格符合 JSON Schema。
- **USER 模板**：注入 `{lineage_graph}`、`{strategy}`、`{degree}` 占位符，要求生成含 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline` 六字段的提案。

模型生成后须交由 §1 步骤 5 的 `check_and_repair` 进行硬约束校验与自动修复，确保输出合规。
