# ThesisArchitect Skill 导入 TRAE IDE 指南

**版本**：v2.1（三层架构版）
**适用平台**：TRAE IDE（Windows / macOS / Linux）

---

## 1. 前置条件

- TRAE IDE 已安装（[下载地址](https://www.trae.com.cn/)）
- 本 Git 项目已克隆到本地

```
git clone <项目地址>
cd ThesisMinerSkill
```

---

## 2. 一键打包（生成 ZIP）

项目根目录已提供自动化打包脚本，运行即可生成 TRAE IDE 可识别的 Skill ZIP 包：

```bash
# 在项目根目录执行
python scripts/build-trae-zip.py
```

执行成功后，会在 `dist/` 目录生成 `thesis-architect-v2.1.zip`。

**脚本做了什么**：
- 读取 `trae-skill/SKILL.md`，将 `../core/` 引用路径自动替换为 `./core/`
- 读取 `trae-skill/INSTRUCTION.md`，同样替换路径
- 将 `core/` 目录（脚本、参考数据、Schema）原样复制到 ZIP 包
- 自动验证 ZIP 包结构完整性

**如果遇到 Python 未安装**：确保 Python 3.8+ 已安装，或者直接下载 `dist/` 目录下已打包好的 ZIP 文件（如存在）。

---

## 3. TRAE IDE 导入步骤

### 方式 A：通过 Skill 管理器导入（推荐）

这是最简便的方式，适合大多数用户。

1. **打开 TRAE IDE**，确保已登录账号

2. **打开 Skill 管理器**
   - 点击左下角用户头像
   - 在弹出的菜单中选择 **「技能」**（Skills）
   
   ![TRAE 用户菜单示意图]（请参考 TRAE IDE 实际界面）

3. **导入 ZIP 包**
   - 在技能管理页面，点击 **「导入技能」** 按钮
   - 文件选择器中找到 `dist/thesis-architect-v2.1.zip`
   - 点击确认

4. **验证导入成功**
   - 技能列表中应出现 **「ThesisArchitect」**
   - 状态显示为已启用
   - 展开可查看其描述和触发条件

5. **开始使用**
   - 在任意对话会话中，直接输入与论文开题相关的问题即可自动触发

### 方式 B：手动放置到 .trae/skills/（备选）

如果方式 A 不可用（如离线环境），可手动部署：

1. **创建目录**
   ```bash
   mkdir -p .trae/skills/thesis-architect/
   ```

2. **解压 ZIP 包**
   ```bash
   # 解压 ZIP 到 .trae/skills/thesis-architect/
   unzip dist/thesis-architect-v2.1.zip -d .trae/skills/thesis-architect/
   ```
   或手动将 ZIP 中的 `SKILL.md`、`INSTRUCTION.md`、`core/` 目录放入 `.trae/skills/thesis-architect/`

3. **重启 TRAE IDE**
   - 完全关闭 TRAE IDE
   - 重新打开
   - TRAE 会在启动时自动扫描 `.trae/skills/` 目录，加载新技能

4. **验证**：检查技能列表中是否出现 ThesisArchitect

---

## 4. 验证导入成功

导入后，在 TRAE 对话中输入以下测试指令：

### 测试 1：纯对话输入输出
```
我是硕士生，导师在做医疗大模型，同门做的是问诊微调。帮我生成3个论题。
```
预期：返回 3 个结构化论题提案（含标题、问题意识、研究意义、差异化、研究内容、文献综述方向）。

### 测试 2：文件输入 + 对话输出
```
读取 @input/profile.json 和 @input/lineage.md，基于这些信息帮我生成开题报告草稿。
```
预期：返回完整的开题报告 Markdown 草稿（五大模块）。

### 测试 3：混合输入 + 文件输出
```
读取 @input/ 里的背景，但我现在想结合最新的 RAG 技术做跨域联想。生成5个提案，保存到本地。
```
预期：提案写入 `/output/` 目录，对话框回复文件路径摘要。

---

## 5. 如何更新 Skill

当 `trae-skill/` 或 `core/` 下的文件内容有修改时，需要重新打包并导入：

```bash
# 1. 重新打包
python scripts/build-trae-zip.py

# 2. 在 TRAE 中重新导入
```
在 TRAE Skill 管理器中：
- 先删除旧版本（点击 ThesisArchitect 技能上的删除按钮）
- 再导入新的 ZIP 包

或者直接点「导入技能」选择新 ZIP，TRAE 通常会自动覆盖旧版本。

---

## 6. 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 导入提示「格式不正确」 | ZIP 包根目录缺少 SKILL.md | 运行 `python scripts/build-trae-zip.py` 重新打包，确保脚本验证通过 |
| 导入后在技能列表找不到 | 导入失败或 ZIP 损坏 | 检查 ZIP 包完整性，尝试方式 B 手动部署 |
| 技能已加载但不响应 | 用户输入未匹配触发条件 | 尝试使用更明确的表述，如"帮我生成论文选题"、"我要开题" |
| 回答质量差 | 谱系信息不完整 | 提供详细的导师项目名称、同门论文标题和方法 |
| 脚本执行报错 | 路径引用不正确 | 验证 ZIP 包内 SKILL.md 使用 `./core/` 而非 `../core/` |
| 文件输出不生效 | 不支持文件写入权限 | 在对话中手动复制结果，或配置 TRAE 的文件写入权限 |

---

## 7. 目录结构说明

导入后，技能在 TRAE 中的工作方式：

```
ZIP 包根目录/
├── SKILL.md              # 元数据层：TRAE 调度系统读取 frontmatter 识别技能
├── INSTRUCTION.md        # 指令层：注入模型运行时的行为规则
└── core/                 # 资源层：按需加载的可执行脚本和参考数据
    ├── scripts/          # 4 个 Python 脚本（lineage_parser/idea_generator/constraint_checker/report_generator）
    ├── references/       # 4 个参考数据文件
    └── schema/           # 2 个 I/O JSON Schema
```

**关键原则**：TRAE 仅在 SKILL.md 和 INSTRUCTION.md 注入上下文，`core/` 内的脚本和数据按需加载，不占用常驻 Token。
