# Tasks

- [x] Task 1: 初始化 Git 仓库与基础配置
  - [x] SubTask 1.1: 在项目根目录执行 `git init`
  - [x] SubTask 1.2: 创建 `.gitignore`，排除 `/output/`、`/input/`、`__pycache__/`、`.DS_Store`、`*.pyc`
  - [x] SubTask 1.3: 执行首次 `git add` 与 `git commit`，提交既有设计文档与 spec 文件

- [x] Task 2: 产出 Claude Skill（`claude-skill/`）
  - [x] SubTask 2.1: 创建 `claude-skill/` 独立目录
  - [x] SubTask 2.2: 编写 `claude-skill/SKILL.md`，含 YAML frontmatter（`name: thesis-architect`、`description` ≤200 字符且说明"做什么+何时触发"）
  - [x] SubTask 2.3: 正文承载 I/O 多态路由、谱系解析器、四维创意引擎（含自评分）、硬约束校验与自动修复器、开题报告直出模板、Prompt 约束模板
  - [x] SubTask 2.4: 补充 `claude-skill/README.md` 说明部署路径（置于运行时 `/skills/` 目录）

- [x] Task 3: 产出 OpenAI Skill（`openai-skill/`）
  - [x] SubTask 3.1: 创建 `openai-skill/` 独立目录
  - [x] SubTask 3.2: 编写 `openai-skill/gpt-instructions.md`（纯 Markdown 指令，无 YAML frontmatter），承载与 Claude 等价的能力
  - [x] SubTask 3.3: 编写 `openai-skill/config.json`，含 `name`、`description`、`capabilities`、`suggested_starters` 字段
  - [x] SubTask 3.4: 补充 `openai-skill/README.md` 说明如何导入 Custom GPT（粘贴 Instructions、配置 Actions）

- [x] Task 4: 产出 Cursor Rules（`cursor-skill/`）
  - [x] SubTask 4.1: 创建 `cursor-skill/` 独立目录
  - [x] SubTask 4.2: 编写 `cursor-skill/thesis-architect.mdc`，含 Cursor 规则 frontmatter（`description`、`globs`、`alwaysApply`）与正文指令
  - [x] SubTask 4.3: 补充 `cursor-skill/README.md` 说明部署至 `.cursor/rules/`

- [x] Task 5: 产出 Trae Skill（`trae-skill/`）
  - [x] SubTask 5.1: 创建 `trae-skill/` 独立目录
  - [x] SubTask 5.2: 编写 `trae-skill/SKILL.md`，遵循 Trae Skill 规范（frontmatter `name`+`description`，正文为详细指令）
  - [x] SubTask 5.3: 补充 `trae-skill/README.md` 说明部署至 `.trae/skills/thesis-architect/`

- [x] Task 6: 产出 GitHub Copilot Instructions（`copilot-skill/`）
  - [x] SubTask 6.1: 创建 `copilot-skill/` 独立目录
  - [x] SubTask 6.2: 编写 `copilot-skill/copilot-instructions.md`（纯 Markdown 指令，适配 Copilot Chat 上下文）
  - [x] SubTask 6.3: 补充 `copilot-skill/README.md` 说明部署至 `.github/`

- [x] Task 7: 生成项目架构 `README.md`
  - [x] SubTask 7.1: 按 `架构readmeV3.0` 模板编写根目录 `README.md`
  - [x] SubTask 7.2: 覆盖项目概述、文件结构与职责、技术栈、核心机制与架构设计、Skill 接口/调用清单、配置与环境变量、部署与运行、扩展性设计
  - [x] SubTask 7.3: 文件结构树需反映 `claude-skill/`、`openai-skill/`、`cursor-skill/`、`trae-skill/`、`copilot-skill/` 五个独立目录

- [x] Task 8: 提交 Git 并验证
  - [x] SubTask 8.1: `git add` 全部新增产物
  - [x] SubTask 8.2: 执行 `git commit`，提交信息描述多平台 Skill 产出
  - [x] SubTask 8.3: 验证各 Skill 文件格式合规（frontmatter、目录结构、内容等价性）

# Task Dependencies
- Task 2、3、4、5、6 相互独立，可并行执行
- Task 7 依赖 Task 2-6 完成（需在文件结构树中体现各目录）
- Task 8 依赖 Task 1-7 全部完成
- Task 1 为前置依赖，须最先完成
