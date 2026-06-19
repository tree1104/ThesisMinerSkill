# ThesisArchitect — Trae Skill 部署说明

本目录包含 ThesisArchitect（研究生开题智能体技能）的 Trae IDE Skill 产物，采用三层物理结构。

## 三层结构

| 层级 | 文件 | 职责 |
| --- | --- | --- |
| 元数据层 | `SKILL.md` | YAML frontmatter（`name`、`version`、`description`），供 Trae IDE 调度系统快速匹配与加载 |
| 指令层 | `INSTRUCTION.md` | 工作流决策规则、I/O 接口规范、自愈兜底逻辑、Prompt 约束 |
| 资源层 | `../core/` | 可执行脚本、静态参考数据、I/O Schema，平台无关、按需加载 |

元数据层 description 精简至 ≤120 字符，仅含唯一标识与触发条件；工作流细节、能力描述全部下沉至指令层；死知识（约束规则、评分权重、模板）与可执行逻辑下沉至资源层。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `SKILL.md` | 元数据层，含 YAML frontmatter 与三层结构说明 |
| `INSTRUCTION.md` | 指令层，含 §1-§5 五大决策规则 |

## 部署方式

1. **复制 Skill 文件**：将 `trae-skill/` 目录下的全部内容复制到 Trae IDE 工作区的 Skill 目录：
   ```
   .trae/skills/thesis-architect/
   ```
   确保最终路径为：
   ```
   <项目根目录>/.trae/skills/thesis-architect/SKILL.md
   <项目根目录>/.trae/skills/thesis-architect/INSTRUCTION.md
   ```

2. **复制资源层**：将 `core/` 目录复制到项目根目录，供 Skill 指令层引用：
   ```
   <项目根目录>/core/
   ├── scripts/       # 4 个可执行 Python 脚本
   ├── references/    # 4 个静态参考数据
   └── schema/        # 2 个 I/O Schema
   ```

3. **自动加载**：Trae IDE 启动时扫描 `.trae/skills/` 目录，自动加载 `SKILL.md`，解析 frontmatter 中的 `name` 与 `description` 字段，并将 `INSTRUCTION.md` 注入到底层大模型运行时上下文。资源层脚本与参考数据不在开场注入，按需加载。

4. **验证加载**：启动 Trae IDE 后，在对话窗口输入与开题相关的指令（如「帮我生成3个论题」），若技能被正确加载，模型会按 `INSTRUCTION.md` 的 6 步工作流执行谱系解析、四维创意涌现、硬约束修复与开题直出。

## 渐进式披露机制

为管控上下文成本，本 Skill 采用渐进式披露：

- **Skill 激活时**：仅加载 `SKILL.md`（元数据）与 `INSTRUCTION.md`（指令）注入上下文。
- **脚本按需加载**：`core/scripts/` 下的 4 个 Python 脚本不在开场注入；仅当模型确认「需要执行计算」时主动调用对应函数加载执行。
- **参考数据按需读取**：`core/references/` 下的约束规则、评分权重、模板由脚本在执行时读取，不进入 Skill 上下文。

## 自愈与兜底机制

- **API 失败重试**：调用大模型 API 失败时返回 `status: "retry"`，附带 2 秒延迟重试建议；脚本内置 `max_retries=3`、`retry_delay=2` 秒重试装饰器。
- **超时中断**：所有脚本主函数经 `@timeout(30)` 装饰器包装，超过 30 秒触发超时中断，返回 `status: "error"`。
- **沙盒执行**：脚本仅允许写入 `output/` 目录，越权写入抛出 `PermissionError`。

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
技能动作：读取文件底座 + 追加 RAG 跨域指令 → 生成提案 → 写入 `/output/proposals_<timestamp>.json`，回复「已保存至该路径」。
