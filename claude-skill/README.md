# ThesisArchitect — Claude Skill 部署说明

本目录包含 ThesisArchitect 技能的 Anthropic Claude 原生 Skill 产物（`SKILL.md`），可在 Claude Code 等 Claude 运行时中即插即用。

## 部署方式

1. 将 `claude-skill/` 目录下的全部内容（即 `SKILL.md`）复制到 Claude 运行时的 `/skills/` 目录下。
   - 以 Claude Code 为例：放置于 `~/.claude/skills/thesis-architect/SKILL.md` 或项目级 `.claude/skills/thesis-architect/SKILL.md`。
2. 重启 Claude 运行时，使其在启动时自动加载该 Skill 的 frontmatter（`name` 与 `description`）及正文指令。
3. 加载成功后，当用户请求涉及"生成论文选题 / 开题报告 / 分析导师项目谱系 / 同门论文"等意图时，Claude 将按 `description` 中的触发条件自动激活本技能。

## 调用示例

### 场景 1：纯对话输入 + 对话输出（快速发散）

```
用户：我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
```

SKILL 动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

### 场景 2：文件输入 + 对话输出（详尽开题）

```
用户：读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```

SKILL 动作：读取 `/input/` 文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

### 场景 3：混合输入 + 文件输出（沉淀落盘）

```
用户：读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
```

SKILL 动作：读取文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `/output/proposals_<timestamp>.json` 与 `draft_<timestamp>.md`，回复"已保存至该路径"。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `SKILL.md` | Claude 原生 Skill 定义，含 YAML frontmatter（`name`、`description`）与完整能力正文 |
| `README.md` | 本部署说明文档 |
