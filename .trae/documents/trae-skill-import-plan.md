# ThesisArchitect Skill 导入 TRAE IDE 计划

## 一、目标

为 ThesisArchitect v2.1 的 TRAE Skill 提供**以 ZIP 包形式导入 TRAE IDE** 的完整方案，包括：
1. 自动化打包脚本 `scripts/build-trae-zip.py`（处理 SKILL.md/INSTRUCTION.md 路径变换 + 打包）
2. 导入指南文档 `TRAE_IMPORT_GUIDE.md`
3. 生成的 ZIP 包 `dist/thesis-architect-v2.1.zip`

## 二、现状分析

当前 TRAE Skill 的源文件分布在：

| 路径 | 用途 | 引用路径 |
|------|------|----------|
| `trae-skill/SKILL.md` | 元数据层（frontmatter） | `../core/scripts/`、`../core/references/`、`../core/schema/` |
| `trae-skill/INSTRUCTION.md` | 指令层（工作流决策规则） | `../core/scripts/`、`../core/references/`、`../core/schema/` |
| `trae-skill/README.md` | 部署说明 | 无外部引用 |
| `core/scripts/` | 4 个 Python 脚本 | 引用同级 `../references/`、`../schema/` |
| `core/references/` | 4 个静态参考数据 | 无 |
| `core/schema/` | 2 个 JSON Schema | 无 |

**关键约束**：
- TRAE IDE 只接受 ZIP 包导入
- ZIP 包根目录必须包含 `SKILL.md`
- `trae-skill/SKILL.md` 使用 `../core/` 引用路径（开发时与 core/ 同层级），但 TRAE ZIP 包中 SKILL.md 和 core/ 都在 ZIP 根目录，需要改为 `./core/`

## 三、ZIP 包结构设计

打包脚本将源文件变换后生成以下结构：

```
thesis-architect-v2.1.zip
├── SKILL.md                    # ← 源 trae-skill/SKILL.md，替换 ../core/ → ./core/
├── INSTRUCTION.md              # ← 源 trae-skill/INSTRUCTION.md，替换 ../core/ → ./core/
├── core/                       # ← 源 core/，原样复制
│   ├── scripts/
│   │   ├── lineage_parser.py
│   │   ├── idea_generator.py
│   │   ├── constraint_checker.py
│   │   └── report_generator.py
│   ├── references/
│   │   ├── constraints.json
│   │   ├── scoring_weights.json
│   │   ├── report_template.md
│   │   └── prompt_templates.json
│   └── schema/
│       ├── input_schema.json
│       └── output_schema.json
```

**SKILL.md 路径变换示例**：

| 源文件（trae-skill/SKILL.md） | ZIP 包内（SKILL.md） |
|---|---|
| `../core/scripts/lineage_parser.py` | `./core/scripts/lineage_parser.py` |
| `../core/references/constraints.json` | `./core/references/constraints.json` |
| `../core/schema/input_schema.json` | `./core/schema/input_schema.json` |

`core/` 目录内部文件（scripts/references/schema）不做任何修改，保持原样。

## 四、计划步骤

### 步骤 1：创建打包脚本 `scripts/build-trae-zip.py`

**为什么用构建脚本，而非直接创建 TRAE 专用文件版本**：
- `trae-skill/SKILL.md` 作为唯一信源（single source of truth），修改时只需改一个文件
- 路径替换是纯文本变换（`../core/` → `./core/`），逻辑简单可靠
- 避免两套文件不同步的问题

**脚本功能**：
1. 读取 `trae-skill/SKILL.md` → 全局替换 `../core/` 为 `./core/` → 存入 ZIP 的 `SKILL.md`
2. 读取 `trae-skill/INSTRUCTION.md` → 全局替换 `../core/` 为 `./core/` → 存入 ZIP 的 `INSTRUCTION.md`
3. 递归复制 `core/` 整个目录到 ZIP 的 `core/`（文件内容不做任何修改）
4. 输出 ZIP 到 `dist/thesis-architect-v2.1.zip`
5. 验证检查：ZIP 根目录有 `SKILL.md`、`INSTRUCTION.md`、`core/` 目录

**脚本位置**：`scripts/build-trae-zip.py`

### 步骤 2：创建导入指南文档

在项目根目录创建 `TRAE_IMPORT_GUIDE.md`，文档结构如下：

```
# ThesisArchitect Skill 导入 TRAE IDE 指南

## 1. 前置条件
- TRAE IDE 已安装
- 本 Git 项目已克隆到本地

## 2. 一键打包（生成 ZIP）
> cd 项目根目录
> python scripts/build-trae-zip.py
执行后会在 dist/ 目录生成 thesis-architect-v2.1.zip

## 3. TRAE IDE 导入步骤
### 方式 A：通过 Skill 管理器导入（推荐）
1. 打开 TRAE IDE
2. 点击左下角用户头像 → "技能"（Skills）
3. 点击"导入技能"（Import Skill）
4. 选择生成的 thesis-architect-v2.1.zip
5. 导入成功后，在技能列表中能看到 "ThesisArchitect"
6. 在对话中即可使用

### 方式 B：手动放置到 .trae/skills/（备选）
1. 在项目根创建 .trae/skills/thesis-architect/ 目录
2. 解压 ZIP，将 SKILL.md、INSTRUCTION.md、core/ 放入该目录
3. 重启 TRAE IDE，自动加载

## 4. 验证导入成功
在 TRAE 对话中测试：
> "我是硕士生，导师在做医疗大模型，帮我生成3个论题"

## 5. 如何更新 Skill
修改 trae-skill/ 或 core/ 下的源文件后，重新运行打包脚本并重新导入即可。

## 6. 常见问题
- ZIP 格式不正确 → 运行脚本后检查输出
- 技能不响应 → 检查对话是否包含触发关键词
- 脚本报错 → 检查引用路径是否为 ./core/
```

### 步骤 3：更新 .gitignore

添加 `dist/` 目录，避免构建产物被提交到 Git。

### 步骤 4：执行并验证

1. 创建 `scripts/build-trae-zip.py`
2. 运行脚本，生成 `dist/thesis-architect-v2.1.zip`
3. 验证 ZIP 结构（SKILL.md 在根目录、路径已变换、core/ 完整）
4. 创建 `TRAE_IMPORT_GUIDE.md`
5. 在 TRAE IDE 中实际导入测试
6. 提交 Git

## 五、文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `scripts/build-trae-zip.py` | ZIP 打包自动化脚本（核心） |
| 新增 | `TRAE_IMPORT_GUIDE.md` | 导入步骤指南文档（详尽步骤） |
| 新增 | `dist/thesis-architect-v2.1.zip` | 打包产物（构建生成） |
| 修改 | `.gitignore` | 添加 `dist/` 目录 |
| 不修改 | `trae-skill/SKILL.md` | 源文件保持不变，由构建脚本变换后放入 ZIP |
| 不修改 | `trae-skill/INSTRUCTION.md` | 同上 |
| 不修改 | `core/` 下所有文件 | 原样复制到 ZIP |

## 六、验证标准

- [ ] `scripts/build-trae-zip.py` 可运行，退出码 0
- [ ] 生成的 ZIP 包根目录包含 `SKILL.md`
- [ ] ZIP 包内 `SKILL.md` 引用路径为 `./core/` 而非 `../core/`
- [ ] ZIP 包内 `INSTRUCTION.md` 引用路径为 `./core/` 而非 `../core/`
- [ ] ZIP 包内 `core/` 目录结构完整（4 scripts + 4 references + 2 schema）
- [ ] ZIP 包内 `core/` 文件不做路径变换
- [ ] ZIP 包可以在 TRAE IDE 中成功导入
- [ ] `TRAE_IMPORT_GUIDE.md` 步骤清晰，用户可独立完成
