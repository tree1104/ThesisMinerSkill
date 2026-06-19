# Tasks

- [x] Task 1: 资源层新增 3 个参考数据文件
  - [x] SubTask 1.1: 创建 `core/references/search_strategies.json`（检索式模板、默认时间窗灵感2年/查重5年、可调节步长）
  - [x] SubTask 1.2: 创建 `core/references/forbidden_ai_phrases.json`（200+ AI 化术语及学术中性映射表）
  - [x] SubTask 1.3: 创建 `core/references/output_granularity.yaml`（精简/标准/详实三级颗粒度定义：Markdown 深度、列表层级、字数阈值）

- [x] Task 2: 资源层新增 2 个脚本
  - [x] SubTask 2.1: 创建 `core/scripts/style_normalizer.py`（remove_ai_traces：词频替换、依存句法重构、主动被动态互换，含 try/except + 超时 + 沙盒）
  - [x] SubTask 2.2: 创建 `core/scripts/deep_helper.py`（literature_deep_reader / experiment_designer / thesis_defense_simulator，含 try/except + 超时 + 沙盒）

- [x] Task 3: 资源层修改 3 个现有脚本
  - [x] SubTask 3.1: 修改 `core/scripts/idea_generator.py`（generate_ideas 增加 search_feeds 参数，注入联网热点作为种子语料）
  - [x] SubTask 3.2: 修改 `core/scripts/constraint_checker.py`（新增 check_novelty 方法，输出联网查重重合度与风险评级）
  - [x] SubTask 3.3: 修改 `core/scripts/report_generator.py`（generate_report 增加 granularity 与 style_neutral 参数，动态渲染不同深度模板）

- [x] Task 4: 资源层修改 1 个参考数据 + 2 个 Schema
  - [x] SubTask 4.1: 修改 `core/references/prompt_templates.json`（开题模板替换为"批判性矩阵"引导词）
  - [x] SubTask 4.2: 修改 `core/schema/input_schema.json`（新增 output_granularity、inspiration_time_window、novelty_time_window）
  - [x] SubTask 4.3: 修改 `core/schema/output_schema.json`（新增 novelty_risk、novelty_report、high_plagiarism_risk_sections、next_actions）

- [x] Task 5: 升级 5 个平台 Skill 指令层与元数据
  - [x] SubTask 5.1: 升级 `claude-skill/`（SKILL.md version→4.0 + description 更新；INSTRUCTION.md 重写为五阶段闭环流 + Rule 7-10）
  - [x] SubTask 5.2: 升级 `openai-skill/`（skill.json version→4.0；gpt-instructions.md 重写为五阶段闭环流 + Rule 7-10）
  - [x] SubTask 5.3: 升级 `cursor-skill/`（.mdc frontmatter version→4.0；正文重写为五阶段闭环流 + Rule 7-10）
  - [x] SubTask 5.4: 升级 `trae-skill/`（SKILL.md version→4.0；INSTRUCTION.md 重写为五阶段闭环流 + Rule 7-10）
  - [x] SubTask 5.5: 升级 `copilot-skill/`（skill.json version→4.0；copilot-instructions.md 重写为五阶段闭环流 + Rule 7-10）

- [x] Task 6: 自测扩充与适配
  - [x] SubTask 6.1: 新增 `tests/test_style_normalizer.py`（测试 remove_ai_traces：禁用词替换、语态转换）
  - [x] SubTask 6.2: 新增 `tests/test_deep_helper.py`（测试三件套：文献精读/实验预研/答辩模拟）
  - [x] SubTask 6.3: 新增 `tests/test_search_strategies.py`（测试检索式生成与时间窗口）
  - [x] SubTask 6.4: 适配 `tests/test_idea_generator.py`（新增 search_feeds 参数测试）
  - [x] SubTask 6.5: 适配 `tests/test_constraint_checker.py`（新增 check_novelty 测试）
  - [x] SubTask 6.6: 适配 `tests/test_report_generator.py`（新增 granularity 与 style_neutral 测试）
  - [x] SubTask 6.7: 适配 `tests/test_schema.py`（验证 V4.0 新增字段）
  - [x] SubTask 6.8: 运行全部测试，确认通过（63 passed）

- [x] Task 7: 文档升级与 Problem.md
  - [x] SubTask 7.1: 升级根目录 `README.md` 到 V4.0（五阶段闭环流、新增资源、新规则、新 Schema 字段）
  - [x] SubTask 7.2: 创建 `Problem.md` 记录升级中遇到的问题与解决思路
  - [x] SubTask 7.3: 修改 `scripts/build-trae-zip.py`（输出文件名改为 thesis-architect-v4.0.zip）

- [x] Task 8: Git 提交与验证
  - [x] SubTask 8.1: `git add` 全部新增与修改产物
  - [x] SubTask 8.2: `git commit` 提交信息描述 V4.0 升级
  - [x] SubTask 8.3: 验证五阶段闭环流、4 条新规则、I/O Schema V4.0、自测全部通过

# Task Dependencies
- Task 1、2 为资源层基础，须最先完成
- Task 3、4 依赖 Task 1（脚本读取新参考数据）
- Task 5 依赖 Task 1-4（指令层引用资源层）
- Task 6 依赖 Task 1-4（测试新脚本与新 Schema）
- Task 7 依赖 Task 1-6（文档反映全部变更）
- Task 8 依赖 Task 1-7 全部完成
- Task 5 的 5 个平台子任务相互独立，可并行
