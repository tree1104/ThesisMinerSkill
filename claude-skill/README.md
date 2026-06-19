# ThesisArchitect — Claude Skill 部署说明

本目录包含 ThesisArchitect 技能的 Anthropic Claude 原生 Skill 产物，采用三层物理结构设计，可在 Claude Code 等 Claude 运行时中即插即用。

## 三层结构

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| 元数据层 | `SKILL.md` | 仅含唯一标识（`name`）、版本（`version`）与触发条件（`description` ≤120 字符），供调度系统快速匹配 |
| 指令层 | `INSTRUCTION.md` | 定义工作流决策规则、I/O 接口规范、自愈兜底与渐进式披露原则，是技能的"灵魂" |
| 资源层 | `../core/` | 承载可执行脚本（`scripts/`）、静态参考数据（`references/`）与 I/O Schema（`schema/`），按需加载 |

资源层目录结构：
- `../core/scripts/`：`lineage_parser.py`、`idea_generator.py`、`constraint_checker.py`、`report_generator.py`
- `../core/references/`：`constraints.json`、`scoring_weights.json`、`report_template.md`、`prompt_templates.json`
- `../core/schema/`：`input_schema.json`、`output_schema.json`

## 部署方式

1. 将 `claude-skill/` 与 `core/` 两个目录一同置于 Claude 运行时的 `/skills/` 目录下，保持两者同级（`core/` 为 `claude-skill/` 的同级目录，确保 `../core/` 相对路径有效）。
   - 以 Claude Code 为例：`claude-skill/` 置于 `~/.claude/skills/thesis-architect/`，`core/` 置于同级 `~/.claude/skills/core/`。
2. 重启 Claude 运行时，使其在启动时自动加载 `SKILL.md` 的 frontmatter（`name`、`version`、`description`）。
3. 加载成功后，当用户请求涉及"生成论文选题 / 开题报告 / 分析导师项目谱系 / 同门论文"等意图时，Claude 将按 `description` 中的触发条件自动激活本技能。

## 渐进式披露机制

为管控上下文成本，本技能采用渐进式披露：
- **激活时**：仅加载 `SKILL.md`（元数据）与 `INSTRUCTION.md`（指令），不预加载脚本与参考数据。
- **执行时**：脚本与参考数据仅在执行到对应工作流步骤时，通过 `read_script` 工具按需加载。
- **效果**：避免开场注入全部资源内容，降低 Token 消耗。

## 调用示例

### 场景 1：纯对话输入 + 对话输出（快速发散）

```
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
```

SKILL 动作：解析对话提取谱系 → 调用 `lineage_parser.py` 解析 → 调用 `idea_generator.py` 四维创意 → 调用 `constraint_checker.py` 校验修复 → 对话框直接输出 3 个结构化提案。

### 场景 2：文件输入 + 对话输出（详尽开题）

```
用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```

SKILL 动作：读取 `/input/` 文件 → 调用 `lineage_parser.py` 解析谱系 → 生成提案并选最优 → 调用 `report_generator.py` 渲染 → 对话框直出完整 Markdown 开题报告。

### 场景 3：混合输入 + 文件输出（沉淀落盘）

```
用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
```

SKILL 动作：读取文件底座 + 追加 RAG 跨域指令 → 调用 `idea_generator.py`（`strategy: cross_domain`）生成 5 个提案 → 调用 `constraint_checker.py` 校验 → 写入 `/output/proposals_<timestamp>.json` 与 `draft_<timestamp>.md`，回复"已保存至该路径"。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `SKILL.md` | 元数据层，含 YAML frontmatter（`name`、`version`、`description`）与三层结构说明 |
| `INSTRUCTION.md` | 指令层，定义工作流决策规则、I/O 接口规范、自愈兜底与渐进式披露原则 |
| `README.md` | 本部署说明文档 |
