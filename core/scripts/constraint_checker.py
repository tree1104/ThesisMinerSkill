#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬约束校验与自动修复器（Constraint Checker）
读取 core/references/constraints.json 获取规则，对提案进行硬约束校验并提供自动修复能力。
约束项：标题格式、学术日历、文献基线、逻辑自洽。
"""

import os
import re
import json
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


def _load_constraints():
    """读取 constraints.json 获取硬约束规则"""
    constraints_path = os.path.join(REFERENCES_DIR, "constraints.json")
    with open(constraints_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ========== 标题校验与自动修复 ==========

def _repair_title(title, constraints):
    """
    标题校验与自动修复：
    - 超长标题截取核心名词短语
    - 动词前置转为名词性短语
    - 匹配"基于X的Y研究"模式时重写
    """
    title_config = constraints.get("title", {})
    max_length = title_config.get("max_length", 20)
    forbidden_verbs = title_config.get("forbidden_verbs", [])
    forbidden_pattern = title_config.get("forbidden_pattern", "")
    repairs = []

    repaired = title

    # 1. 检测并修复"基于X的Y研究"模式
    if forbidden_pattern:
        pattern = re.compile(forbidden_pattern)
        if pattern.search(repaired):
            # 提取核心内容，去除"基于...的...研究"套路
            match = re.search(r'基于(.+?)的(.+?)(?:研究|分析|探讨)', repaired)
            if match:
                core_a = match.group(1)
                core_b = match.group(2)
                repaired = f"{core_b}的{core_a}方法"
                repairs.append(f"重写「基于X的Y研究」模式为「{repaired}」")
            else:
                # 无法提取，直接截断
                repaired = re.sub(r'基于.*?的', '', repaired)
                repairs.append("去除「基于X的」前缀")

    # 2. 检测并修复动词前置（"研究X" → "X的研究"）
    for verb in forbidden_verbs:
        if repaired.startswith(verb):
            rest = repaired[len(verb):].strip("的")
            repaired = f"{rest}的{verb}"
            repairs.append(f"动词前置修复：「{title}」→「{repaired}」")
            break

    # 3. 检测并修复超长标题（截取核心名词短语）
    if len(repaired) > max_length:
        # 尝试提取名词短语：去除修饰词，保留核心
        # 简化策略：按"的"切分，取核心部分
        parts = repaired.split("的")
        if len(parts) > 1:
            # 取最后两个部分作为核心
            repaired = "的".join(parts[-2:])[:max_length]
        else:
            repaired = repaired[:max_length]
        repairs.append(f"超长标题截取至 {max_length} 字以内：「{repaired}」")

    return repaired, repairs


# ========== 学术日历校验 ==========

def _check_academic_calendar(proposal, constraints, degree):
    """学术日历校验：硕士≤12月，博士≤24月；超期注入降级策略"""
    calendar_config = constraints.get("academic_calendar", {})
    max_months = calendar_config.get("master_months", 12) if degree == "master" else calendar_config.get("phd_months", 24)

    repairs = []
    warnings = []

    # 检查提案中是否声明了研究周期
    duration = proposal.get("duration_months")
    research_content = proposal.get("research_content", "")

    if duration and duration > max_months:
        # 超期：注入"分阶段并行执行"降级策略
        if "分阶段并行执行" not in research_content:
            proposal["research_content"] = (
                research_content + "\n注：因研究周期较长，建议分阶段并行执行以控制进度。"
            )
            repairs.append(f"研究周期 {duration} 月超过 {degree} 上限 {max_months} 月，已注入「分阶段并行执行」降级策略")
        proposal["duration_months"] = max_months

    return proposal, repairs, warnings


# ========== 文献基线校验 ==========

def _check_literature_baseline(proposal, constraints, degree):
    """文献基线校验：硕士30篇，博士50篇"""
    lit_config = constraints.get("literature_baseline", {})
    required_papers = lit_config.get("master_papers", 30) if degree == "master" else lit_config.get("phd_papers", 50)

    repairs = []
    warnings = []

    outline = proposal.get("literature_review_outline", "")
    # 尝试从大纲中提取规划的文献数量
    count_match = re.search(r'(\d+)\s*篇', outline)
    planned_count = int(count_match.group(1)) if count_match else 0

    if planned_count < required_papers:
        # 文献不足：注入基线要求提示
        baseline_note = f"（规划文献不少于 {required_papers} 篇，覆盖国内外研究）"
        if baseline_note not in outline:
            proposal["literature_review_outline"] = outline + baseline_note
            repairs.append(f"文献规划不足 {required_papers} 篇基线，已注入基线要求提示")

    return proposal, repairs, warnings


# ========== 逻辑自洽校验 ==========

def _compute_overlap_ratio(text1, text2):
    """计算两段文本的重合度（基于字符二元组 Jaccard 相似度）"""
    if not text1 or not text2:
        return 0.0
    # 生成字符二元组
    bigrams1 = set(text1[i:i + 2] for i in range(len(text1) - 1))
    bigrams2 = set(text2[i:i + 2] for i in range(len(text2) - 1))
    if not bigrams1 or not bigrams2:
        return 0.0
    intersection = bigrams1 & bigrams2
    union = bigrams1 | bigrams2
    return len(intersection) / len(union)


def _check_logical_consistency(proposal, constraints):
    """逻辑自洽校验：研究内容与目标重合度 >70% 时标记 WARNING"""
    consistency_config = constraints.get("logical_consistency", {})
    max_overlap = consistency_config.get("max_overlap_ratio", 0.7)

    repairs = []
    warnings = []

    research_content = proposal.get("research_content", "")
    research_significance = proposal.get("research_significance", "")
    overlap = _compute_overlap_ratio(research_content, research_significance)

    if overlap > max_overlap:
        warnings.append(
            f"WARNING: 研究内容与研究意义重合度过高（{overlap:.1%} > {max_overlap:.0%}），"
            f"建议区分「做什么」与「为什么做」"
        )

    return repairs, warnings


# ========== 主函数 ==========

@timeout(30)
def check_and_repair(proposal: dict) -> dict:
    """
    硬约束校验与自动修复主函数。

    参数:
        proposal: 论题提案 dict，应含 title、research_content、literature_review_outline 等字段
                  可选含 degree（master/phd）、duration_months

    返回:
        标准化输出 dict，data 含 repaired_proposal（修复后提案）、repairs（修复记录）、warnings（警告）
    """
    try:
        if not proposal or not isinstance(proposal, dict):
            return {
                "status": "error",
                "data": None,
                "error_message": "输入提案为空或非字典"
            }

        # 读取约束规则
        constraints = _load_constraints()
        degree = proposal.get("degree", "master")

        # 复制提案以避免修改原始数据
        repaired_proposal = dict(proposal)
        all_repairs = []
        all_warnings = []

        # 1. 标题校验与自动修复
        original_title = repaired_proposal.get("title", "")
        if original_title:
            repaired_title, title_repairs = _repair_title(original_title, constraints)
            repaired_proposal["title"] = repaired_title
            all_repairs.extend(title_repairs)

        # 2. 学术日历校验
        repaired_proposal, calendar_repairs, calendar_warnings = _check_academic_calendar(
            repaired_proposal, constraints, degree
        )
        all_repairs.extend(calendar_repairs)
        all_warnings.extend(calendar_warnings)

        # 3. 文献基线校验
        repaired_proposal, lit_repairs, lit_warnings = _check_literature_baseline(
            repaired_proposal, constraints, degree
        )
        all_repairs.extend(lit_repairs)
        all_warnings.extend(lit_warnings)

        # 4. 逻辑自洽校验
        consistency_repairs, consistency_warnings = _check_logical_consistency(
            repaired_proposal, constraints
        )
        all_repairs.extend(consistency_repairs)
        all_warnings.extend(consistency_warnings)

        return {
            "status": "success",
            "data": {
                "repaired_proposal": repaired_proposal,
                "repairs": all_repairs,
                "warnings": all_warnings
            },
            "error_message": None
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"约束配置文件缺失：{str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"约束配置文件格式错误：{str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"约束校验失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_proposal = {
        "title": "基于深度学习的医疗问答系统研究",
        "degree": "master",
        "duration_months": 15,
        "problem_awareness": "医疗问答系统精度不足",
        "research_significance": "医疗问答系统精度不足，需要研究医疗问答系统",
        "research_content": "1. 调研医疗问答系统；2. 设计深度学习模型；3. 实验验证。",
        "literature_review_outline": "梳理医疗问答系统相关研究，规划文献 15 篇。"
    }
    result = check_and_repair(sample_proposal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
