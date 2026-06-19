# ThesisArchitect 指令层（INSTRUCTION）

本文件是 ThesisArchitect 技能的"灵魂"，定义工作流与决策规则。所有死知识（脚本实现、约束数据、模板文本）均存放于资源层 `../core/`，按需加载，不在此内联。

---

## §1 工作流决策规则（V4.0 五阶段闭环导航流）

技能激活后，按以下五阶段闭环导航流执行。每一步均显式调用资源层脚本，禁止凭模型记忆替代计算。阶段一至阶段五构成闭环，阶段五后禁止结束对话（Rule 10）。

### 阶段一：信息确权与双时域联网勘探

1. **开题灵感勘探（默认近 2 年）**：
   - 解析用户初始输入后，**不直接生成论题**。
   - 读取 `../core/references/search_strategies.json` 的 `inspiration_search` 配置，生成 3~5 组高精度学术检索式（含布尔运算符 AND/OR/NOT），调用联网搜索 API。
   - **强制中断（Rule 7）**：向用户展示检索结果摘要（Top 5 篇最新文献），提供"时间范围拨盘"（提示："当前默认展示近 2 年前沿动态，可调整为 1 年/3 年/5 年"）。
   - **Rule 8**：展示时间窗口并提供修改入口，等待用户确认"信息已阅/已确认/继续"后，解锁进入阶段二。严禁未展示检索结果直接输出论题。
2. **候选论题重复度评估（默认近 5 年）**：在阶段三执行，此处仅声明将在四维创意后进行。

### 阶段二：谱系解析与四维创意生成（注入检索热点）

- 调用 `../core/scripts/lineage_parser.py` 的 `parse_lineage(text)` 解析谱系。
- 调用 `../core/scripts/idea_generator.py` 的 `generate_ideas(lineage_graph, strategy, degree, search_feeds)` 函数，**强制将阶段一检索到的前沿热点作为 `search_feeds` 参数注入**，作为"跨域联想"与"矛盾驱动"的种子语料。
- 四策略：advisor_extension / peer_inheritance / cross_domain / contradiction_driven。strategy="all" 时四策略并行。
- 自评分：可行性(40%) + 创新度(30%) + 谱系贴合度(30%)，权重读取自 `../core/references/scoring_weights.json`，过滤低于 6 分的候选。
- 输出 Top 3-5 个方向，按分数降序排列。
- 针对每个候选，调用大模型填充 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline` 字段。文献综述必须以"批判性矩阵"方式组织（问题-方法-不足三栏矩阵），每个研究内容标注"关键科学问题"与"差异化切入点"。

### 阶段三：重复度评估与硬约束修复

1. **重复度评估**：调用 `../core/scripts/constraint_checker.py` 的 `check_novelty(candidate_title, time_window)` 方法，基于候选标题生成查重检索式（读取 `search_strategies.json` 的 `novelty_check` 配置），联网检索近 5 年（可交互调节 3y/5y/10y）硕博论文与期刊。
   - 输出"新颖性风险评估"：重合度百分比（overlap_ratio）、风险评级（novelty_risk: low/medium/high）、差异化空档说明（differentiation_gap）。
   - **Rule 8**：检索前展示时间窗口并提供修改入口。
2. **用户决策**：用户从带查重评估的候选中选择最终 1 个论题进入报告生成。
3. **硬约束修复**：调用 `../core/scripts/constraint_checker.py` 的 `check_and_repair(proposal)` 函数，执行标题格式（≤20字、禁主动动词开头、禁"基于X的Y研究"）、学术日历（硕士≤12月/博士≤24月）、文献基线（硕士≥30篇/博士≥50篇）、逻辑自洽（重合度≤70%）校验并自动修复。约束规则读取自 `../core/references/constraints.json`。

### 阶段四：多粒度开题生成与降重脱敏

1. **多粒度可控生成**：**强制询问用户**："您需要【精简】、【标准】还是【详实】版的开题报告草稿？"
   - 读取 `../core/references/output_granularity.yaml` 获取三级颗粒度配置（Markdown 标题深度、列表层级、字数阈值）。
   - 精简版（concise）：五大模块骨架，仅保留核心结论，Markdown 深度 2。
   - 标准版（standard）：五大模块 + 每个研究内容配 1 个技术路线子图描述，Markdown 深度 3。
   - 详实版（detailed）：标准版 + 现状分条详细评述 + 风险矩阵 + 预期成果价值阐述，Markdown 深度 4。
2. 调用 `../core/scripts/report_generator.py` 的 `generate_report(proposal, granularity, style_neutral)` 函数，按用户选择的粒度渲染报告。报告模板读取自 `../core/references/report_template.md`。
3. **学术风格中性化（Rule 9）**：`style_normalizer` 的执行优先级高于 `report_generator` 的排版。`generate_report` 的 `style_neutral=True` 时自动调用 `../core/scripts/style_normalizer.py` 的 `remove_ai_traces(text)` 方法，执行：
   - 禁用词表过滤（读取 `../core/references/forbidden_ai_phrases.json`，替换 200+ AI 化术语为学术中性表达，如"显著提升"→"呈现正向关联"）
   - 句首禁用词过滤（移除"首先/其次/综上所述"等）
   - 主动被动态互换（"我们提出"→"本研究提出"）
   - 输出 Markdown + 局部高重复风险段落标红提醒（high_plagiarism_risk_sections）。
   - 输出内容若检测到 forbidden_ai_phrases.json 中的词汇，必须替换后方可输出。

### 阶段五：深度辅助与实验映射闭环（Rule 10 后置交互循环）

- 报告输出后，**禁止结束对话**（Rule 10）。系统必须渲染"深度辅助导航菜单"，等待用户选择下一步动作：
  - **选项 A：文献精读工作簿** → 调用 `../core/scripts/deep_helper.py` 的 `literature_deep_reader(research_status, count=3)` 函数，针对报告中的"国内外研究现状"生成 3 篇标志性文献精读框架（三明治拆解：动机-方法-局限；GAP 分析：与自身课题关键问题的映射；可借鉴图表）。
  - **选项 B：实验/应用预研映射** → 调用 `../core/scripts/deep_helper.py` 的 `experiment_designer(research_content, discipline)` 函数，按学科类型输出：
    - 理工/计算机类（stem）：MVE 清单（库版本、核心算法伪代码、基线对比计划）
    - 数学/理论类（math）：证明路径图谱（前置引理梳理、核心引理构造思路、数值算例验证方案）
    - 社科/商科类（social）：调研方案设计（问卷量表映射、抽样策略、数据分析模型预设）
  - **选项 C：答辩模拟（逻辑压力测试）** → 调用 `../core/scripts/deep_helper.py` 的 `thesis_defense_simulator(key_problems, rounds=3)` 函数，AI 扮演严苛盲审专家，针对"关键问题"发起 3 轮苏格拉底式诘问。

### 阻断性规则（Rule 7-10）

以下规则为写死的硬性约束，非建议，必须严格执行：

- **Rule 7（信息确权门禁）**：执行四维创意发散前，必须先完成"联网检索摘要展示"并等待用户明确回复"已确认/继续"。严禁未展示检索结果直接输出论题。
- **Rule 8（时间窗口交互）**：每次联网检索前，必须向用户展示当前时间窗口（如"近 2 年"），并提供修改入口。
- **Rule 9（降重与去 AI 化优先级）**：`style_normalizer` 的执行优先级高于 `report_generator` 的排版。输出内容若检测到 `forbidden_ai_phrases.json` 中的词汇，必须替换后方可输出。
- **Rule 10（后置交互循环）**：报告输出后，禁止结束对话。必须渲染"深度辅助导航菜单"，并等待用户选择下一步动作（文献精读/实验预研/答辩模拟）。

---

## §2 I/O 接口规范

输入与输出均通过 JSON Schema 标准化校验，不依赖模型记忆传递数据。

### 输入规范
输入必须符合 `../core/schema/input_schema.json`：
- **必填字段**：`degree`（`master`/`phd`）、`lineage`（学术谱系对象）。
- **可选字段**：`strategy`（`advisor_extension`/`peer_inheritance`/`cross_domain`/`contradiction_driven`/`all`，默认 `all`）、`count`（1-10，默认 3）、`output_format`（`dialogue`/`file`，默认 `dialogue`）、`output_granularity`（`concise`/`standard`/`detailed`，默认 `standard`）、`inspiration_time_window`（`1y`/`2y`/`3y`/`5y`，默认 `2y`）、`novelty_time_window`（`3y`/`5y`/`10y`，默认 `5y`）。

### 输出规范
输出必须符合 `../core/schema/output_schema.json`：
- `status`：`success`（成功）/ `retry`（需重试）/ `error`（错误）。
- `data`：核心结果数据（含 `proposals` 列表，每项含 `title`、`problem_awareness`、`research_significance`、`differentiation`、`research_content`、`literature_review_outline`、`score`、`novelty_risk`（`low`/`medium`/`high`）、`novelty_report`（字符串））；`data` 另含 `high_plagiarism_risk_sections`（字符串数组）。
- `error_message`：错误信息，`status` 为 `error`/`retry` 时必填。
- 顶层 `next_actions`：数组，元素枚举 `literature_deep_reading`/`experiment_design`/`defense_simulation`。

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
