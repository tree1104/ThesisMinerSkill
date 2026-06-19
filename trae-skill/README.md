# ThesisArchitect — Trae Skill 部署说明

本目录包含 ThesisArchitect（研究生开题智能体技能）的 Trae IDE Skill 产物。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `SKILL.md` | Trae Skill 主体，含 YAML frontmatter（`name`、`description`）与完整能力指令正文 |

## 部署方式

1. 将 `trae-skill/` 目录下的全部内容复制到 Trae IDE 工作区的 Skill 目录：
   ```
   .trae/skills/thesis-architect/
   ```
   即确保最终路径为：
   ```
   <项目根目录>/.trae/skills/thesis-architect/SKILL.md
   ```

2. **自动加载**：Trae IDE 在启动时会扫描 `.trae/skills/` 目录，自动加载其中的 `SKILL.md`，解析 frontmatter 中的 `name` 与 `description` 字段，并将正文指令注入到底层大模型运行时的上下文中。无需手动注册或重启编辑器之外的步骤。

3. **验证加载**：启动 Trae IDE 后，在对话窗口中输入与开题相关的指令（如“帮我生成3个论题”），若技能被正确加载，模型会按 ThesisArchitect 工作流执行谱系解析、四维创意涌现、硬约束修复与开题直出。

## 调用示例

技能由 Trae IDE 根据用户指令语义自动触发，无需显式命令。以下为典型调用场景：

### 场景 1：纯对话输入输出（快速发散）
```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
```
技能动作：解析对话提取谱系 → 执行四维创意 → 对话框直接输出 3 个结构化提案。

### 场景 2：文件输入 + 对话输出（详尽开题）
```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿，直接发给我。
```
技能动作：读取文件解析谱系 → 生成提案并选最优 → 对话框直出完整 Markdown 开题报告。

### 场景 3：混合输入 + 文件输出（沉淀落盘）
```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
```
技能动作：读取文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `/output/proposals_<timestamp>.json`，回复“已保存至该路径”。

## 能力概览

本 Skill 与项目内其他平台产物（Claude Skill、OpenAI Skill、Cursor Rules、GitHub Copilot Instructions）在能力层面等价，完整承载以下五大核心能力：

1. **I/O 多态路由**：文件 / 对话 / 混合输入，文件 / 对话输出
2. **谱系解析器**：实体抽取 + 边缘探测
3. **四维创意引擎**：导师项目延伸、同门成果继承、跨域联想、矛盾驱动 + 自评分过滤
4. **硬约束校验与自动修复器**：标题格式、学术日历、文献基线、逻辑自洽
5. **开题报告直出**：五大模块标准模板

差异仅在于外层格式（YAML frontmatter）与触发语法适配 Trae IDE 的 Skill 发现机制。
