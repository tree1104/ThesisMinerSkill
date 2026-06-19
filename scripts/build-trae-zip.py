"""
ThesisArchitect Skill — TRAE IDE ZIP 打包脚本

功能：
1. 读取 trae-skill/SKILL.md 和 trae-skill/INSTRUCTION.md
2. 将 ../core/ 引用路径替换为 ./core/（适配 TRAE ZIP 包根目录结构）
3. 将 core/ 目录原样复制
4. 打包为 thesis-architect-v2.1.zip
5. 验证 ZIP 结构完整性

用法：
    python scripts/build-trae-zip.py

输出：
    dist/thesis-architect-v2.1.zip
"""

import json
import os
import zipfile
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRAE_SKILL_DIR = os.path.join(PROJECT_ROOT, "trae-skill")
CORE_DIR = os.path.join(PROJECT_ROOT, "core")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
ZIP_NAME = "thesis-architect-v2.1.zip"
ZIP_PATH = os.path.join(DIST_DIR, ZIP_NAME)

SKILL_SOURCE = os.path.join(TRAE_SKILL_DIR, "SKILL.md")
INSTRUCTION_SOURCE = os.path.join(TRAE_SKILL_DIR, "INSTRUCTION.md")


def transform_path(content: str) -> str:
    """将 ../core/ 引用路径替换为 ./core/"""
    count = content.count("../core/")
    result = content.replace("../core/", "./core/")
    return result, count


def add_file_to_zip(zf: zipfile.ZipFile, arcname: str, content: str):
    """将文本内容写入 ZIP 包"""
    zf.writestr(arcname, content.encode("utf-8"))


def add_directory_to_zip(zf: zipfile.ZipFile, source_dir: str, arc_prefix: str):
    """递归将目录下所有文件原样加入 ZIP 包（排除 __pycache__ 和 .pyc 文件）"""
    for root, dirs, files in os.walk(source_dir):
        # 排除 __pycache__ 目录
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".pyc"):
                continue
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, source_dir)
            arcname = os.path.join(arc_prefix, rel_path).replace("\\", "/")
            zf.write(file_path, arcname)


def verify_zip(zip_path: str) -> list[str]:
    """验证 ZIP 包结构，返回错误列表"""
    errors = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # 检查根目录文件
        if "SKILL.md" not in names:
            errors.append("ZIP 根目录缺少 SKILL.md")
        if "INSTRUCTION.md" not in names:
            errors.append("ZIP 根目录缺少 INSTRUCTION.md")
        if "core/" not in names and not any(n.startswith("core/") for n in names):
            errors.append("ZIP 缺少 core/ 目录")

        # 检查 core/ 下必备文件
        required_core_files = [
            "core/scripts/lineage_parser.py",
            "core/scripts/idea_generator.py",
            "core/scripts/constraint_checker.py",
            "core/scripts/report_generator.py",
            "core/references/constraints.json",
            "core/references/scoring_weights.json",
            "core/references/report_template.md",
            "core/references/prompt_templates.json",
            "core/schema/input_schema.json",
            "core/schema/output_schema.json",
        ]
        for f in required_core_files:
            if f not in names:
                errors.append(f"ZIP 缺少 {f}")

        # 检查路径是否已变换（ZIP 内的 SKILL.md 不应含 ../core/）
        skill_content = zf.read("SKILL.md").decode("utf-8")
        if "../core/" in skill_content:
            errors.append("SKILL.md 中仍然存在未替换的 ../core/ 引用")

        instr_content = zf.read("INSTRUCTION.md").decode("utf-8")
        if "../core/" in instr_content:
            errors.append("INSTRUCTION.md 中仍然存在未替换的 ../core/ 引用")

    return errors


def main():
    print("=" * 60)
    print("ThesisArchitect — TRAE ZIP 打包脚本")
    print("=" * 60)

    # 检查源文件
    for path, label in [(SKILL_SOURCE, "SKILL.md"), (INSTRUCTION_SOURCE, "INSTRUCTION.md"), (CORE_DIR, "core/")]:
        if not os.path.exists(path):
            print(f"[错误] 未找到 {label}: {path}")
            sys.exit(1)

    # 确保输出目录存在
    os.makedirs(DIST_DIR, exist_ok=True)

    # 创建 ZIP 包
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # 处理 SKILL.md
        with open(SKILL_SOURCE, "r", encoding="utf-8") as f:
            content = f.read()
        transformed, count_skill = transform_path(content)
        add_file_to_zip(zf, "SKILL.md", transformed)
        print(f"[OK] SKILL.md -> ZIP (替换 {count_skill} 处 ../core/ → ./core/)")

        # 处理 INSTRUCTION.md
        with open(INSTRUCTION_SOURCE, "r", encoding="utf-8") as f:
            content = f.read()
        transformed, count_instr = transform_path(content)
        add_file_to_zip(zf, "INSTRUCTION.md", transformed)
        print(f"[OK] INSTRUCTION.md -> ZIP (替换 {count_instr} 处 ../core/ → ./core/)")

        # 复制 core/ 目录
        add_directory_to_zip(zf, CORE_DIR, "core")
        print("[OK] core/ -> ZIP (原样复制)")

    # 验证
    errors = verify_zip(ZIP_PATH)
    if errors:
        print(f"\n[验证失败] 发现 {len(errors)} 个问题:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 输出统计
    file_count = 0
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        file_count = len(zf.namelist())

    size_kb = os.path.getsize(ZIP_PATH) / 1024
    print(f"\n{'=' * 60}")
    print(f"[OK] 打包成功!")
    print(f"  输出路径: {ZIP_PATH}")
    print(f"  ZIP 大小: {size_kb:.1f} KB")
    print(f"  文件总数: {file_count}")
    print(f"  路径变换: SKILL.md {count_skill} 处 + INSTRUCTION.md {count_instr} 处")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
