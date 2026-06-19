# Skill 架构重构 Spec（三层结构 + I/O 标准化 + 自愈 + Token 效率）

## Why
当前 5 个平台 Skill 均为单文件结构（SKILL.md / gpt-instructions.md / .mdc / copilot-instructions.md），将元数据、指令、约束数据、模板全部塞进一个文件，导致：上下文成本高（开场即注入全部内容）、无法渐进式披露（脚本与参考数据无法按需加载）、I/O 无结构化校验（依赖模型记忆传递数据）、缺乏自愈逻辑（执行出错无标准重试机制）。需按主流最佳实践重构为三层物理结构 + 去上下文化 I/O + 自愈兜底 + Token 效率优化。

## What Changes
- 新增平台无关的共享资源层 `core/`，承载可执行脚本、静态参考数据、I/O Schema，供 5 个平台 Skill 按需引用。
- 将 5 个平台 Skill 从单文件重构为**三层物理结构**：
  - **元数据层**：SKILL.md（Claude/Trae）、skill.json（OpenAI/Copilot）、.mdc frontmatter（Cursor）—— 仅含唯一标识、版本、触发条件，精简描述。
  - **指令层**：INSTRUCTION.md（Claude/Trae）、gpt-instructions.md（OpenAI）、.mdc 正文（Cursor）、copilot-instructions.md（Copilot）—— 定义工作流与决策规则，不含死知识。
  - **资源层**：通过 `core/scripts/`、`core/references/`、`core/schema/` 引用，渐进式披露。
- 新增**去上下文化 I/O 接口**：
  - `core/schema/input_schema.json`：JSON Schema 验证输入（degree、lineage、strategy、count 等必填字段）。
  - `core/schema/output_schema.json`：标准化输出（status: success/retry/error、data、error_message）。
- 新增**自愈与兜底逻辑**：
  - 指令层写死错误处理规则（API 失败→status:retry+延迟2秒重试；超时中断；沙盒执行）。
  - 脚本内置 try/except 与重试装饰器。
- **Token 效率优化**：
  - 元数据 description 精简至 ≤120 字符（原 ≤200）。
  - 脚本与参考数据仅在模型确认"需要执行计算"时按需加载，不在开场注入。
- 新增 `core/scripts/` 下 4 个可执行 Python 脚本：lineage_parser.py、idea_generator.py、constraint_checker.py、report_generator.py。
- 新增 `core/references/` 下 4 个静态数据文件：constraints.json、scoring_weights.json、report_template.md、prompt_templates.json。
- 新增 `tests/` 目录，对脚本与 Schema 进行自测。
- 更新根目录 README.md 反映新结构。

## Impact
- Affected specs: multi-platform-skills（前置，已完成）
- Affected code:
  - 新增 `core/` 目录（scripts/、references/、schema/）
  - 重构 `claude-skill/SKILL.md` → 拆分为 `SKILL.md`（元数据）+ `INSTRUCTION.md`（指令）
  - 重构 `trae-skill/SKILL.md` → 拆分为 `SKILL.md`（元数据）+ `INSTRUCTION.md`（指令）
  - 重构 `openai-skill/` → 新增 `skill.json`（元数据），精简 `gpt-instructions.md`（指令）
  - 重构 `cursor-skill/thesis-architect.mdc` → 精简 frontmatter，正文引用 core/
  - 重构 `copilot-skill/` → 新增 `skill.json`（元数据），精简 `copilot-instructions.md`（指令）
  - 新增 `tests/` 目录
  - 更新 `README.md`

## ADDED Requirements

### Requirement: 三层物理结构
每个平台 Skill SHALL 采用三层物理结构：元数据层、指令层、资源层，职责分明。

#### Scenario: 元数据层精简
- **GIVEN** 任一平台 Skill 的元数据文件
- **THEN** 仅含唯一标识（name）、版本（version）、触发条件（description ≤120 字符），不含工作流细节

#### Scenario: 指令层定义工作流
- **GIVEN** 任一平台 Skill 的指令文件
- **THEN** 定义"遇到A情况怎么做，遇到B情况如何纠错"的决策规则，引用 core/ 资源而非内联死知识

#### Scenario: 资源层渐进式披露
- **GIVEN** core/scripts/ 与 core/references/
- **THEN** 仅在模型确认"需要执行计算"时按需加载，不在 Skill 激活时全量注入上下文

### Requirement: 共享资源层 core/
系统 SHALL 提供平台无关的 `core/` 目录，承载可执行脚本、静态参考数据、I/O Schema，供 5 个平台 Skill 引用。

#### Scenario: 脚本可执行
- **GIVEN** core/scripts/lineage_parser.py
- **THEN** 可独立运行，提供 parse_lineage(text) 函数，返回结构化 LineageGraph

#### Scenario: 参考数据结构化
- **GIVEN** core/references/constraints.json
- **THEN** 以 JSON 格式定义硬约束规则（标题长度、学术日历、文献基线），可被脚本与指令层引用

### Requirement: 去上下文化 I/O 接口
系统 SHALL 通过 JSON Schema 标准化输入输出，不依赖模型记忆传递数据。

#### Scenario: 输入 Schema 验证
- **GIVEN** core/schema/input_schema.json
- **THEN** 定义 required 字段（degree、lineage），明确枚举值（degree: master/phd；strategy: 四策略+all）

#### Scenario: 输出结构化
- **GIVEN** core/schema/output_schema.json
- **THEN** 输出包含 status（success/retry/error）、data（核心结果）、error_message（错误码），让模型能自主决定继续/重试/报错

### Requirement: 自愈与兜底逻辑
系统 SHALL 在指令层与脚本层内置错误处理预案。

#### Scenario: API 失败重试
- **WHEN** 调用大模型 API 失败
- **THEN** 返回 status: retry，附带延迟 2 秒重试建议，不直接报错中断

#### Scenario: 超时中断
- **WHEN** 脚本执行超过 30 秒
- **THEN** 触发超时中断，返回 status: error + error_message: "执行超时"

#### Scenario: 沙盒执行
- **GIVEN** 脚本执行环境
- **THEN** 在受限沙盒中运行，禁止网络访问与文件系统越权写入（仅允许 output/ 目录）

### Requirement: Token 效率优化
系统 SHALL 严格管控上下文成本。

#### Scenario: 精简描述
- **GIVEN** 任一平台 Skill 元数据的 description
- **THEN** ≤120 字符（从原 200 收紧），短小精悍便于调度系统快速匹配

#### Scenario: 动态加载脚本
- **WHEN** Skill 激活
- **THEN** 不在开场注入脚本内容；仅当模型确认"需要执行计算"时主动调用 read_script 加载

### Requirement: 自测覆盖
系统 SHALL 提供自测脚本，覆盖核心脚本与 Schema 验证。

#### Scenario: 脚本自测
- **GIVEN** tests/ 目录
- **THEN** 对 lineage_parser、idea_generator、constraint_checker、report_generator 各提供测试用例

#### Scenario: Schema 自测
- **GIVEN** tests/ 目录
- **THEN** 验证 input_schema.json 与 output_schema.json 为合法 JSON Schema，且能校验样例数据

## MODIFIED Requirements

### Requirement: Claude Skill 三层结构
Claude Skill 从单文件 SKILL.md 重构为 SKILL.md（元数据）+ INSTRUCTION.md（指令），引用 core/ 资源层。

### Requirement: OpenAI Skill 三层结构
OpenAI Skill 新增 skill.json（元数据），gpt-instructions.md 精简为指令层，引用 core/ 资源层。

### Requirement: Cursor Rules 三层结构
Cursor .mdc 精简 frontmatter，正文引用 core/ 资源层。

### Requirement: Trae Skill 三层结构
Trae Skill 从单文件 SKILL.md 重构为 SKILL.md（元数据）+ INSTRUCTION.md（指令），引用 core/ 资源层。

### Requirement: Copilot Instructions 三层结构
Copilot 新增 skill.json（元数据），copilot-instructions.md 精简为指令层，引用 core/ 资源层。
