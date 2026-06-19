#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开题报告直出器（Report Generator）
读取 core/references/report_template.md 获取模板，填充五大模块，生成开题报告 Markdown。
五大模块：选题依据与研究意义、国内外研究现状、研究内容与关键问题、研究方案与可行性分析、进度安排。
"""

import os
import re
import json
import time
import threading
from functools import wraps


# ========== 路径常量（使用相对路径定位 references/） ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(SCRIPT_DIR, "..", "references")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "..", "output")


# ========== 超时装饰器（≤30秒，使用 threading 实现，兼容 Windows） ==========
def timeout(seconds=30):
    """超时装饰器：超过指定秒数返回标准化错误输出"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result_container = [None]
            exception_container = [None]

            def target():
                try:
                    result_container[0] = func(*args, **kwargs)
                except Exception as e:
                    exception_container[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)

            if thread.is_alive():
                return {
                    "status": "error",
                    "data": None,
                    "error_message": f"执行超时（超过 {seconds} 秒）"
                }
            if exception_container[0] is not None:
                return {
                    "status": "error",
                    "data": None,
                    "error_message": f"执行异常：{str(exception_container[0])}"
                }
            return result_container[0]

        return wrapper
    return decorator


# ========== 沙盒路径校验（仅允许写入 output/ 目录） ==========
def validate_write_path(path):
    """沙盒限制：校验写入路径是否在 output/ 目录内"""
    output_abs = os.path.abspath(OUTPUT_DIR)
    target_abs = os.path.abspath(path)
    if not target_abs.startswith(output_abs + os.sep) and target_abs != output_abs:
        raise PermissionError(
            f"沙盒限制：仅允许写入 output/ 目录，禁止写入 {path}"
        )
    return target_abs


def _load_template():
    """读取 report_template.md 获取开题报告模板"""
    template_path = os.path.join(REFERENCES_DIR, "report_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


# ========== 模块内容生成辅助函数 ==========

def _generate_key_questions(proposal):
    """基于 differentiation 提炼 1-2 个核心科学问题"""
    differentiation = proposal.get("differentiation", "")
    if not differentiation:
        return "1. 本研究的核心科学问题待进一步明确。"
    # 从差异化描述中提炼科学问题
    return (
        f"1. 基于差异化定位「{differentiation[:30]}」，如何形式化本研究的核心问题？\n"
        f"2. 所提方法在复杂场景下的有效性与鲁棒性如何保证？"
    )


def _generate_research_method(proposal):
    """基于 research_content 生成具体方法步骤"""
    research_content = proposal.get("research_content", "")
    if not research_content:
        return "（待补充具体研究方法与技术路线）"
    return (
        f"{research_content}\n\n"
        f"技术路线：文献调研 → 问题定义 → 方法设计 → 实验验证 → 结果分析 → 论文撰写。"
    )


def _generate_feasibility_analysis(proposal):
    """生成可行性分析（周期可行性、数据/设备可行性论证）"""
    degree = proposal.get("degree", "master")
    max_months = 12 if degree == "master" else 24
    return (
        f"1. 周期可行性：本研究计划在 {max_months} 个月内完成，"
        f"符合{degree}学制要求，各阶段时间分配合理。\n"
        f"2. 数据可行性：将使用公开数据集或导师课题组既有数据资源，确保数据可得。\n"
        f"3. 设备可行性：依托导师课题组计算资源，必要时采用轻量化方案降低算力需求。\n"
        f"4. 技术可行性：所提方法基于成熟技术栈，具备实现基础。"
    )


def _generate_schedule(proposal):
    """基于 academic_calendar 约束生成甘特图节点列表"""
    degree = proposal.get("degree", "master")
    total_months = 12 if degree == "master" else 24
    # 划分阶段
    phase1 = max(1, total_months // 6)       # 文献调研与开题
    phase2 = max(1, total_months // 3)       # 方法设计与实验
    phase3 = max(1, total_months // 3)       # 结果分析与论文撰写
    phase4 = total_months - phase1 - phase2 - phase3  # 答辩准备

    schedule = (
        f"| 阶段 | 时间（月） | 任务 |\n"
        f"|------|-----------|------|\n"
        f"| 第一阶段 | 第1-{phase1}月 | 文献调研、开题报告撰写 |\n"
        f"| 第二阶段 | 第{phase1 + 1}-{phase1 + phase2}月 | 方法设计、数据准备、初步实验 |\n"
        f"| 第三阶段 | 第{phase1 + phase2 + 1}-{phase1 + phase2 + phase3}月 | 完整实验、结果分析 |\n"
        f"| 第四阶段 | 第{phase1 + phase2 + phase3 + 1}-{total_months}月 | 论文撰写、修改、答辩准备 |"
    )
    return schedule


def _fill_template(template, proposal):
    """填充模板占位符"""
    # 生成衍生字段
    key_questions = _generate_key_questions(proposal)
    research_method = _generate_research_method(proposal)
    feasibility_analysis = _generate_feasibility_analysis(proposal)
    schedule = _generate_schedule(proposal)

    # 占位符替换映射
    replacements = {
        "{{title}}": proposal.get("title", "（未命名论题）"),
        "{{problem_awareness}}": proposal.get("problem_awareness", "（待补充）"),
        "{{research_significance}}": proposal.get("research_significance", "（待补充）"),
        "{{literature_review_outline}}": proposal.get("literature_review_outline", "（待补充）"),
        "{{research_content}}": proposal.get("research_content", "（待补充）"),
        "{{key_questions}}": key_questions,
        "{{research_method}}": research_method,
        "{{feasibility_analysis}}": feasibility_analysis,
        "{{schedule}}": schedule,
    }

    filled = template
    for placeholder, value in replacements.items():
        filled = filled.replace(placeholder, str(value))

    return filled


# ========== 主函数 ==========

@timeout(30)
def generate_report(proposal: dict) -> dict:
    """
    开题报告直出器主函数。

    参数:
        proposal: 论题提案 dict，应含 title、problem_awareness、research_significance、
                  differentiation、research_content、literature_review_outline 等字段
                  可选含 degree（master/phd）

    返回:
        标准化输出 dict，data 含 report_markdown（报告内容）与 report_path（文件路径）
    """
    try:
        if not proposal or not isinstance(proposal, dict):
            return {
                "status": "error",
                "data": None,
                "error_message": "输入提案为空或非字典"
            }

        # 读取模板
        template = _load_template()

        # 填充模板
        report_markdown = _fill_template(template, proposal)

        # 生成文件名（带时间戳）
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"draft_{timestamp}.md"
        report_path = os.path.join(OUTPUT_DIR, filename)

        # 沙盒校验后写入文件
        validated_path = validate_write_path(report_path)

        # 确保 output/ 目录存在
        os.makedirs(os.path.dirname(validated_path), exist_ok=True)

        with open(validated_path, "w", encoding="utf-8") as f:
            f.write(report_markdown)

        return {
            "status": "success",
            "data": {
                "report_markdown": report_markdown,
                "report_path": report_path
            },
            "error_message": None
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"模板文件缺失：{str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"沙盒权限拒绝：{str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"报告生成失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_proposal = {
        "title": "医疗大模型的科室问询微调",
        "degree": "master",
        "problem_awareness": "通用大模型在医疗问询场景精度不足，缺乏科室特异性。",
        "research_significance": "通过科室级微调提升医疗大模型问询精度，兼具理论与实际价值。",
        "differentiation": "聚焦单一科室微调，区别于通用大模型的全场景覆盖。",
        "research_content": "1. 调研医疗大模型现状；2. 设计科室微调方案；3. 实验验证。",
        "literature_review_outline": "梳理医疗大模型与微调技术研究，规划文献不少于30篇。"
    }
    result = generate_report(sample_proposal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
