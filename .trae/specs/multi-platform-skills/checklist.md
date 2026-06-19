# Checklist

## Git 仓库
- [x] 项目根目录存在 `.git` 目录（`git init` 已执行）
- [x] 根目录存在 `.gitignore`，且包含 `/output/`、`/input/`、`__pycache__/`、`.DS_Store`、`*.pyc`
- [x] 已执行至少一次 `git commit`，提交信息符合规范

## Claude Skill（`claude-skill/`）
- [x] `claude-skill/SKILL.md` 存在
- [x] 顶部为 YAML frontmatter，含 `name` 与 `description` 字段
- [x] `description` 不超过 200 字符，且同时说明"做什么"与"何时触发"
- [x] 正文包含 I/O 多态路由（文件/对话/混合输入，文件/对话输出）
- [x] 正文包含谱系解析器（实体抽取 + 边缘探测）
- [x] 正文包含四维创意引擎（导师项目延伸、同门成果继承、跨域联想、矛盾驱动）及自评分机制（可行性40%+创新度30%+谱系贴合度30%，过滤<6分）
- [x] 正文包含硬约束校验与自动修复器（标题≤20字、学术日历、文献基线、逻辑自洽）
- [x] 正文包含开题报告直出模板（五大模块）
- [x] 正文包含 Prompt 约束模板（SYSTEM + USER）
- [x] `claude-skill/README.md` 说明部署路径

## OpenAI Skill（`openai-skill/`）
- [x] `openai-skill/gpt-instructions.md` 存在
- [x] 为纯 Markdown 指令文本，无 YAML frontmatter
- [x] 承载与 Claude 等价的能力（谱系解析、四维创意、硬约束修复、开题直出）
- [x] `openai-skill/config.json` 存在且为合法 JSON
- [x] `config.json` 含 `name`、`description`、`capabilities`、`suggested_starters` 字段
- [x] `openai-skill/README.md` 说明导入 Custom GPT 步骤

## Cursor Rules（`cursor-skill/`）
- [x] `cursor-skill/thesis-architect.mdc` 存在
- [x] 含 Cursor 规则 frontmatter（`description`、`globs`、`alwaysApply`）
- [x] 正文承载等价能力
- [x] `cursor-skill/README.md` 说明部署至 `.cursor/rules/`

## Trae Skill（`trae-skill/`）
- [x] `trae-skill/SKILL.md` 存在
- [x] frontmatter 含 `name` 与 `description`（≤200 字符，说明"做什么+何时触发"）
- [x] 正文承载等价能力
- [x] `trae-skill/README.md` 说明部署至 `.trae/skills/thesis-architect/`

## GitHub Copilot（`copilot-skill/`）
- [x] `copilot-skill/copilot-instructions.md` 存在
- [x] 为纯 Markdown 指令，适配 Copilot Chat 上下文
- [x] 承载等价能力
- [x] `copilot-skill/README.md` 说明部署至 `.github/`

## 内容等价性
- [x] 五个平台 Skill 产物均能完成"谱系解析 → 四维创意 → 硬约束修复 → 开题报告直出"完整链路
- [x] 各产物差异仅限于格式包装与触发语法，核心能力一致

## 项目架构 README
- [x] 根目录 `README.md` 存在
- [x] 包含项目概述（定位、核心功能、技术底座）
- [x] 包含文件结构与职责（目录树含五个独立 Skill 目录）
- [x] 包含技术栈详情
- [x] 包含核心机制与架构设计（系统分层、业务流程、I/O 多态）
- [x] 包含 Skill 接口/调用清单（各平台部署与调用方式）
- [x] 包含配置与环境变量
- [x] 包含部署与运行
- [x] 包含扩展性设计

## 格式合规
- [x] Claude `SKILL.md` 与 Trae `SKILL.md` 使用 YAML frontmatter
- [x] OpenAI `gpt-instructions.md` 与 Copilot `copilot-instructions.md` 为纯 Markdown 无 frontmatter
- [x] Cursor `.mdc` 使用 Cursor 专属 frontmatter
- [x] 各 Skill 位于独立目录，未混用格式
