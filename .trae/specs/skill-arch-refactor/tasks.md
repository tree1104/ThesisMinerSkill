# Tasks

- [x] Task 1: 创建共享资源层 core/（脚本 + 参考数据 + Schema）
  - [x] SubTask 1.1: 创建 `core/scripts/lineage_parser.py`（谱系解析：parse_lineage(text) -> LineageGraph，含 try/except 与超时装饰器）
  - [x] SubTask 1.2: 创建 `core/scripts/idea_generator.py`（四维创意生成 + 自评分过滤，含重试逻辑）
  - [x] SubTask 1.3: 创建 `core/scripts/constraint_checker.py`（硬约束校验 + 自动修复，含沙盒限制）
  - [x] SubTask 1.4: 创建 `core/scripts/report_generator.py`（开题报告直出，引用 report_template.md）
  - [x] SubTask 1.5: 创建 `core/references/constraints.json`（标题≤20字、学术日历、文献基线、逻辑自洽规则）
  - [x] SubTask 1.6: 创建 `core/references/scoring_weights.json`（可行性40%+创新度30%+谱系贴合度30%，过滤阈值6）
  - [x] SubTask 1.7: 创建 `core/references/report_template.md`（五大模块开题报告模板）
  - [x] SubTask 1.8: 创建 `core/references/prompt_templates.json`（SYSTEM + USER Prompt 模板）
  - [x] SubTask 1.9: 创建 `core/schema/input_schema.json`（输入 JSON Schema：degree/lineage/strategy/count/output_format）
  - [x] SubTask 1.10: 创建 `core/schema/output_schema.json`（输出 JSON Schema：status/data/error_message）

- [x] Task 2: 重构 Claude Skill 为三层结构
  - [x] SubTask 2.1: 精简 `claude-skill/SKILL.md` 为元数据层（frontmatter name+version+description≤120字符，正文仅概述与资源指针）
  - [x] SubTask 2.2: 新增 `claude-skill/INSTRUCTION.md` 指令层（工作流决策规则、引用 ../core/、自愈规则、I/O 接口说明）
  - [x] SubTask 2.3: 更新 `claude-skill/README.md` 说明三层结构与部署方式

- [x] Task 3: 重构 OpenAI Skill 为三层结构
  - [x] SubTask 3.1: 新增 `openai-skill/skill.json` 元数据层（name/version/description≤120字符/triggers）
  - [x] SubTask 3.2: 精简 `openai-skill/gpt-instructions.md` 为指令层（工作流、引用 core/、自愈规则、I/O 接口）
  - [x] SubTask 3.3: 更新 `openai-skill/config.json`（保留，作为 GPT Builder 配置参考）
  - [x] SubTask 3.4: 更新 `openai-skill/README.md` 说明三层结构与导入方式

- [x] Task 4: 重构 Cursor Rules 为三层结构
  - [x] SubTask 4.1: 精简 `cursor-skill/thesis-architect.mdc` frontmatter（description≤120字符）与正文（指令层，引用 core/）
  - [x] SubTask 4.2: 更新 `cursor-skill/README.md` 说明三层结构与部署方式

- [x] Task 5: 重构 Trae Skill 为三层结构
  - [x] SubTask 5.1: 精简 `trae-skill/SKILL.md` 为元数据层（frontmatter name+version+description≤120字符，正文仅概述与资源指针）
  - [x] SubTask 5.2: 新增 `trae-skill/INSTRUCTION.md` 指令层（工作流决策规则、引用 ../core/、自愈规则、I/O 接口说明）
  - [x] SubTask 5.3: 更新 `trae-skill/README.md` 说明三层结构与部署方式

- [x] Task 6: 重构 Copilot Instructions 为三层结构
  - [x] SubTask 6.1: 新增 `copilot-skill/skill.json` 元数据层（name/version/description≤120字符/triggers）
  - [x] SubTask 6.2: 精简 `copilot-skill/copilot-instructions.md` 为指令层（工作流、引用 core/、自愈规则、I/O 接口）
  - [x] SubTask 6.3: 更新 `copilot-skill/README.md` 说明三层结构与部署方式

- [x] Task 7: 创建自测 tests/
  - [x] SubTask 7.1: 创建 `tests/test_lineage_parser.py`（测试实体抽取与边缘探测）
  - [x] SubTask 7.2: 创建 `tests/test_idea_generator.py`（测试四维策略与自评分过滤）
  - [x] SubTask 7.3: 创建 `tests/test_constraint_checker.py`（测试标题修复、日历校验、文献基线）
  - [x] SubTask 7.4: 创建 `tests/test_report_generator.py`（测试五大模块生成）
  - [x] SubTask 7.5: 创建 `tests/test_schema.py`（测试 input/output Schema 合法性与样例校验）
  - [x] SubTask 7.6: 运行全部测试，确认通过（28 passed）

- [ ] Task 8: 更新 README.md 与 Git 提交
  - [ ] SubTask 8.1: 更新根目录 `README.md` 反映三层结构（core/ 目录树、各 Skill 三层拆分）
  - [ ] SubTask 8.2: `git add` 全部新增与修改产物
  - [ ] SubTask 8.3: `git commit` 提交信息描述架构重构
  - [ ] SubTask 8.4: 验证各 Skill 三层结构合规、I/O Schema 合法、自测通过

# Task Dependencies
- Task 1 为核心前置依赖，须最先完成（其他 Task 引用 core/）
- Task 2、3、4、5、6 相互独立，可并行执行（均依赖 Task 1）
- Task 7 依赖 Task 1（测试 core/ 脚本与 Schema）
- Task 8 依赖 Task 1-7 全部完成
