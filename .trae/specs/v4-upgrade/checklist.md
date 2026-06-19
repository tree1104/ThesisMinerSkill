# Checklist

## 资源层新增参考数据
- [x] `core/references/search_strategies.json` 存在且为合法 JSON（含检索式模板、灵感2年/查重5年默认窗、可调节步长）
- [x] `core/references/forbidden_ai_phrases.json` 存在且为合法 JSON（含 200+ AI 化术语及中性映射）
- [x] `core/references/output_granularity.yaml` 存在且为合法 YAML（含精简/标准/详实三级定义）

## 资源层新增脚本
- [x] `core/scripts/style_normalizer.py` 存在且提供 remove_ai_traces(text) 函数
- [x] `core/scripts/deep_helper.py` 存在且提供 literature_deep_reader / experiment_designer / thesis_defense_simulator 三函数
- [x] 两个新脚本含 try/except、超时装饰器（≤30秒）、沙盒限制（仅写 output/）
- [x] 两个新脚本返回标准化输出 dict（status/data/error_message）

## 资源层修改脚本
- [x] `idea_generator.py` 的 generate_ideas 增加 search_feeds 参数
- [x] `constraint_checker.py` 新增 check_novelty() 方法
- [x] `report_generator.py` 的 generate_report 增加 granularity 与 style_neutral 参数

## 资源层修改参考数据与 Schema
- [x] `prompt_templates.json` 开题模板替换为"批判性矩阵"引导词
- [x] `input_schema.json` 新增 output_granularity（concise/standard/detailed）
- [x] `input_schema.json` 新增 inspiration_time_window（1y/2y/3y/5y）
- [x] `input_schema.json` 新增 novelty_time_window（3y/5y/10y）
- [x] `output_schema.json` proposals 新增 novelty_risk（low/medium/high）
- [x] `output_schema.json` proposals 新增 novelty_report
- [x] `output_schema.json` data 新增 high_plagiarism_risk_sections
- [x] `output_schema.json` 顶层新增 next_actions 数组

## 五阶段闭环导航流
- [x] 阶段一：信息确权门禁（联网检索 + 摘要展示 + 等待用户确认）
- [x] 阶段二：谱系解析 + 四维创意（注入检索热点作为种子）
- [x] 阶段三：重复度评估 + 硬约束修复（check_novelty + 自动修复）
- [x] 阶段四：多粒度生成 + 降重脱敏（granularity + style_normalizer）
- [x] 阶段五：深度辅助导航菜单（文献精读/实验预研/答辩模拟）

## 指令层四条阻断性规则
- [x] Rule 7（信息确权门禁）：四维创意前必须完成联网检索摘要展示并等待用户确认
- [x] Rule 8（时间窗口交互）：每次联网检索前展示时间窗口并提供修改入口
- [x] Rule 9（降重去 AI 化优先级）：style_normalizer 优先级高于 report_generator 排版
- [x] Rule 10（后置交互循环）：报告输出后禁止结束对话，必须渲染深度辅助导航菜单

## 5 个平台 Skill 升级
- [x] `claude-skill/SKILL.md` version=4.0，description 更新
- [x] `claude-skill/INSTRUCTION.md` 重写为五阶段闭环流 + Rule 7-10
- [x] `openai-skill/skill.json` version=4.0
- [x] `openai-skill/gpt-instructions.md` 重写为五阶段闭环流 + Rule 7-10
- [x] `cursor-skill/thesis-architect.mdc` frontmatter description 更新为 V4.0
- [x] `.mdc` 正文重写为五阶段闭环流 + Rule 7-10
- [x] `trae-skill/SKILL.md` version=4.0
- [x] `trae-skill/INSTRUCTION.md` 重写为五阶段闭环流 + Rule 7-10
- [x] `copilot-skill/skill.json` version=4.0
- [x] `copilot-skill/copilot-instructions.md` 重写为五阶段闭环流 + Rule 7-10

## 自测
- [x] `tests/test_style_normalizer.py` 存在且测试通过
- [x] `tests/test_deep_helper.py` 存在且测试通过
- [x] `tests/test_search_strategies.py` 存在且测试通过
- [x] `tests/test_idea_generator.py` 适配 search_feeds 参数且通过
- [x] `tests/test_constraint_checker.py` 适配 check_novelty 且通过
- [x] `tests/test_report_generator.py` 适配 granularity 与 style_neutral 且通过
- [x] `tests/test_schema.py` 验证 V4.0 新增字段且通过
- [x] 全部测试运行通过（`python -m pytest tests/ -v` → 63 passed）

## 文档与打包
- [x] 根目录 `README.md` 升级到 V4.0（五阶段闭环流、新增资源、新规则、新 Schema）
- [x] `Problem.md` 存在，记录升级中遇到的问题与解决思路
- [x] `scripts/build-trae-zip.py` 输出文件名改为 thesis-architect-v4.0.zip
- [x] 已执行 `git commit`，提交信息描述 V4.0 升级（commit 503bdf4，35 files changed）
