# Checklist

## 共享资源层 core/
- [ ] `core/scripts/lineage_parser.py` 存在且提供 parse_lineage(text) 函数
- [ ] `core/scripts/idea_generator.py` 存在且提供四维策略生成 + 自评分过滤
- [ ] `core/scripts/constraint_checker.py` 存在且提供硬约束校验 + 自动修复
- [ ] `core/scripts/report_generator.py` 存在且提供开题报告直出
- [ ] 每个脚本含 try/except 错误处理与超时装饰器（≤30秒）
- [ ] `core/references/constraints.json` 存在且为合法 JSON（含标题/日历/文献/逻辑规则）
- [ ] `core/references/scoring_weights.json` 存在且为合法 JSON（可行性40%+创新度30%+谱系贴合度30%，阈值6）
- [ ] `core/references/report_template.md` 存在且含五大模块
- [ ] `core/references/prompt_templates.json` 存在且为合法 JSON（SYSTEM + USER 模板）
- [ ] `core/schema/input_schema.json` 存在且为合法 JSON Schema（含 required: degree, lineage）
- [ ] `core/schema/output_schema.json` 存在且为合法 JSON Schema（含 status/data/error_message）

## 三层结构 — Claude Skill
- [ ] `claude-skill/SKILL.md` 仅含元数据（frontmatter name+version+description≤120字符，正文仅概述与资源指针）
- [ ] `claude-skill/INSTRUCTION.md` 存在，定义工作流决策规则，引用 ../core/
- [ ] `claude-skill/INSTRUCTION.md` 含自愈规则（API失败→retry、超时中断、沙盒执行）
- [ ] `claude-skill/INSTRUCTION.md` 含 I/O 接口说明（引用 core/schema/）
- [ ] `claude-skill/README.md` 说明三层结构与部署方式

## 三层结构 — OpenAI Skill
- [ ] `openai-skill/skill.json` 存在且为合法 JSON（name/version/description≤120字符/triggers）
- [ ] `openai-skill/gpt-instructions.md` 精简为指令层，引用 core/，含自愈规则与 I/O 接口
- [ ] `openai-skill/gpt-instructions.md` 无 YAML frontmatter
- [ ] `openai-skill/README.md` 说明三层结构与导入方式

## 三层结构 — Cursor Rules
- [ ] `cursor-skill/thesis-architect.mdc` frontmatter description≤120字符
- [ ] `.mdc` 正文精简为指令层，引用 core/，含自愈规则与 I/O 接口
- [ ] `cursor-skill/README.md` 说明三层结构与部署方式

## 三层结构 — Trae Skill
- [ ] `trae-skill/SKILL.md` 仅含元数据（frontmatter name+version+description≤120字符，正文仅概述与资源指针）
- [ ] `trae-skill/INSTRUCTION.md` 存在，定义工作流决策规则，引用 ../core/
- [ ] `trae-skill/INSTRUCTION.md` 含自愈规则与 I/O 接口说明
- [ ] `trae-skill/README.md` 说明三层结构与部署方式

## 三层结构 — Copilot Instructions
- [ ] `copilot-skill/skill.json` 存在且为合法 JSON（name/version/description≤120字符/triggers）
- [ ] `copilot-skill/copilot-instructions.md` 精简为指令层，引用 core/，含自愈规则与 I/O 接口
- [ ] `copilot-skill/copilot-instructions.md` 无 YAML frontmatter
- [ ] `copilot-skill/README.md` 说明三层结构与部署方式

## 去上下文化 I/O 接口
- [ ] input_schema.json 定义 required 字段（degree, lineage）
- [ ] input_schema.json 含枚举值（degree: master/phd；strategy: 四策略+all）
- [ ] output_schema.json 含 status（success/retry/error）
- [ ] output_schema.json 含 data（核心结果）与 error_message（错误码）

## 自愈与兜底逻辑
- [ ] 指令层写死错误处理规则（API失败→status:retry+延迟2秒重试）
- [ ] 脚本含超时中断机制（≤30秒）
- [ ] 脚本含沙盒执行限制（仅允许 output/ 目录写入）

## Token 效率
- [ ] 所有平台 Skill 元数据 description ≤120 字符
- [ ] 指令层不在开场注入脚本内容（仅引用路径，按需加载）

## 自测 tests/
- [ ] `tests/test_lineage_parser.py` 存在且测试通过
- [ ] `tests/test_idea_generator.py` 存在且测试通过
- [ ] `tests/test_constraint_checker.py` 存在且测试通过
- [ ] `tests/test_report_generator.py` 存在且测试通过
- [ ] `tests/test_schema.py` 存在且测试通过（Schema 合法性 + 样例校验）

## README 与 Git
- [ ] 根目录 `README.md` 更新，反映 core/ 目录与三层结构
- [ ] 已执行 `git commit`，提交信息描述架构重构
