# V4.0 全生命周期升级 Spec

## Why
当前 V2.1 架构是"单次开题生成器"：生成开题报告后智能体即静默，未接管后续文献精读与实验设计；信息获取草率（直出论题无时效性佐证）；输出颗粒度单一无法适配不同学科；AI 痕迹过重导致查重率与 AI 检测率双高。V4.0 设计文档已明确将线性六步流重构为"五阶段闭环导航流"，需对整个多平台 SKILL 项目进行完美升级，使所有平台 Skill 与共享资源层同步进化到 V4.0。

## What Changes
- **核心工作流重构**：从 V2.1 线性六步流升级为 V4.0 五阶段闭环导航流（信息确权 → 谱系四维 → 重复度评估 → 多粒度生成+降重 → 深度辅助）。
- **资源层新增 3 个参考数据文件**：
  - `core/references/search_strategies.json`：检索式生成模板、默认时间窗口（灵感 2 年 / 查重 5 年）、可调节步长。
  - `core/references/forbidden_ai_phrases.json`：200+ 高频 AI 化术语及学术中性映射表。
  - `core/references/output_granularity.yaml`：精简/标准/详实三级颗粒度对应的 Markdown 深度、列表层级、字数阈值。
- **资源层新增 2 个脚本**：
  - `core/scripts/style_normalizer.py`：`remove_ai_traces(text)` 词频替换、依存句法重构、主动被动态互换。
  - `core/scripts/deep_helper.py`：`literature_deep_reader()`、`experiment_designer()`、`thesis_defense_simulator()`。
- **资源层修改 3 个脚本**：
  - `idea_generator.py`：`generate_ideas` 增加 `search_feeds` 参数，强制注入联网检索热点作为种子语料。
  - `constraint_checker.py`：新增 `check_novelty()` 方法，输出联网查重重合度与风险评级。
  - `report_generator.py`：`generate_report` 增加 `granularity` 与 `style_neutral` 参数，动态渲染不同深度模板。
- **资源层修改 1 个参考数据**：`prompt_templates.json` 开题模板替换为"批判性矩阵"引导词。
- **I/O Schema 升级**：
  - `input_schema.json` 新增 `output_granularity`、`inspiration_time_window`、`novelty_time_window` 字段。
  - `output_schema.json` 新增 `novelty_risk`、`novelty_report`、`high_plagiarism_risk_sections`、`next_actions` 字段。
- **指令层新增 4 条阻断性规则**（所有平台 INSTRUCTION.md）：
  - Rule 7（信息确权门禁）：四维创意前必须完成联网检索摘要展示并等待用户确认。
  - Rule 8（时间窗口交互）：每次联网检索前展示时间窗口并提供修改入口。
  - Rule 9（降重去 AI 化优先级）：style_normalizer 优先级高于 report_generator 排版。
  - Rule 10（后置交互循环）：报告输出后禁止结束对话，必须渲染深度辅助导航菜单。
- **5 个平台 Skill 全部升级**：Claude / OpenAI / Cursor / Trae / Copilot 的元数据 version 升至 "4.0"，指令层同步五阶段闭环流与 4 条新规则。
- **自测扩充**：新增 `test_style_normalizer.py`、`test_deep_helper.py`、`test_search_strategies.py`；更新现有测试以适配新参数。
- **文档升级**：根目录 `README.md` 升级到 V4.0；新增 `Problem.md` 记录升级中遇到的问题与解决思路。
- **TRAE 打包脚本同步**：`scripts/build-trae-zip.py` 输出文件名改为 `thesis-architect-v4.0.zip`。

## Impact
- Affected specs: skill-arch-refactor（V2.1 三层结构基线，V4.0 在其上增量）
- Affected code:
  - 新增：`core/references/search_strategies.json`、`core/references/forbidden_ai_phrases.json`、`core/references/output_granularity.yaml`
  - 新增：`core/scripts/style_normalizer.py`、`core/scripts/deep_helper.py`
  - 修改：`core/scripts/idea_generator.py`、`core/scripts/constraint_checker.py`、`core/scripts/report_generator.py`
  - 修改：`core/references/prompt_templates.json`
  - 修改：`core/schema/input_schema.json`、`core/schema/output_schema.json`
  - 修改：5 个平台 Skill 的元数据与指令层（claude-skill/、openai-skill/、cursor-skill/、trae-skill/、copilot-skill/）
  - 新增：`tests/test_style_normalizer.py`、`tests/test_deep_helper.py`、`tests/test_search_strategies.py`
  - 修改：`tests/` 下现有 5 个测试文件
  - 修改：`README.md`、`scripts/build-trae-zip.py`
  - 新增：`Problem.md`

## ADDED Requirements

### Requirement: 五阶段闭环导航流
系统 SHALL 将核心工作流从 V2.1 线性六步流升级为 V4.0 五阶段闭环导航流，强制引入中断点与确权门禁。

#### Scenario: 阶段一信息确权
- **WHEN** 用户输入初始信息后
- **THEN** 系统不直接生成论题，而是生成 3~5 组检索式联网搜索近 2 年文献，展示 Top 5 摘要并提供时间范围拨盘，等待用户确认"已阅"后解锁四维创意

#### Scenario: 阶段三多粒度生成
- **WHEN** 进入开题报告生成阶段
- **THEN** 系统强制询问用户选择【精简】/【标准】/【详实】版，按选择渲染对应深度模板

#### Scenario: 阶段五后置交互循环
- **WHEN** 开题报告输出完成
- **THEN** 系统禁止结束对话，必须渲染"深度辅助导航菜单"（文献精读/实验预研/答辩模拟），等待用户选择

### Requirement: 联网检索与新颖性评估
系统 SHALL 在阶段一与阶段三分别执行联网检索，并在阶段三输出新颖性风险评估。

#### Scenario: 灵感勘探检索
- **GIVEN** 阶段一执行
- **THEN** 读取 `core/references/search_strategies.json` 生成检索式，默认近 2 年，可交互调节

#### Scenario: 重复度评估
- **GIVEN** 阶段三执行
- **THEN** `constraint_checker.check_novelty()` 基于候选标题生成查重检索式，联网检索近 5 年，输出重合度百分比与差异化空档

### Requirement: 学术风格中性化
系统 SHALL 在报告生成后强制执行去 AI 痕迹处理。

#### Scenario: 禁用词过滤
- **GIVEN** `core/references/forbidden_ai_phrases.json`
- **THEN** `style_normalizer.remove_ai_traces(text)` 替换 200+ 高频 AI 化术语为学术中性表达（如"显著提升"→"呈现正向关联"）

#### Scenario: 优先级
- **WHEN** report_generator 输出后
- **THEN** style_normalizer 必须执行，检测到禁用词必须替换后方可输出

### Requirement: 深度辅助三件套
系统 SHALL 在阶段五提供文献精读、实验预研、答辩模拟三种可执行工单。

#### Scenario: 文献精读工作簿
- **WHEN** 用户选择"文献精读"
- **THEN** `deep_helper.literature_deep_reader()` 针对研究现状生成 3 篇标志性文献精读框架（三明治拆解 + GAP 分析 + 可借鉴图表）

#### Scenario: 实验预研映射
- **WHEN** 用户选择"实验预研"
- **THEN** `deep_helper.experiment_designer()` 按学科类型输出 MVE 清单（理工）/ 证明路径图谱（数学）/ 调研方案（社科）

#### Scenario: 答辩模拟
- **WHEN** 用户选择"答辩模拟"
- **THEN** `deep_helper.thesis_defense_simulator()` 扮演严苛盲审专家发起 3 轮苏格拉底式诘问

### Requirement: I/O Schema V4.0 升级
系统 SHALL 升级 input_schema 与 output_schema 以支持多粒度与全流程引导。

#### Scenario: 输入新增字段
- **GIVEN** input_schema.json
- **THEN** 新增 `output_granularity`（concise/standard/detailed）、`inspiration_time_window`（1y/2y/3y/5y）、`novelty_time_window`（3y/5y/10y）

#### Scenario: 输出新增字段
- **GIVEN** output_schema.json
- **THEN** proposals 新增 `novelty_risk`（low/medium/high）与 `novelty_report`；data 新增 `high_plagiarism_risk_sections`；顶层新增 `next_actions` 数组

### Requirement: 指令层四条阻断性规则
所有平台 Skill 的指令层 SHALL 强制插入 Rule 7-10 阻断性逻辑。

#### Scenario: Rule 7 信息确权门禁
- **WHEN** 执行四维创意发散前
- **THEN** 必须先完成联网检索摘要展示并等待用户明确回复"已确认/继续"，严禁未展示直接输出论题

#### Scenario: Rule 10 后置交互循环
- **WHEN** 报告输出后
- **THEN** 禁止结束对话，必须渲染深度辅助导航菜单并等待用户选择

## MODIFIED Requirements

### Requirement: 三层物理结构（V4.0 增量）
V2.1 三层物理结构保留，资源层扩充 3 个参考数据 + 2 个脚本，指令层新增 4 条规则。

### Requirement: 多平台 Skill 升级到 V4.0
5 个平台 Skill 元数据 version 升至 "4.0"，description 同步更新，指令层承载五阶段闭环流与 4 条新规则。

### Requirement: 自测覆盖 V4.0 新增能力
tests/ 新增 3 个测试文件，现有 5 个测试文件适配新参数（search_feeds、granularity、style_neutral、check_novelty）。
