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


def _load_search_strategies():
    """读取 search_strategies.json 获取检索策略配置（V4.0 新增）"""
    strategies_path = os.path.join(REFERENCES_DIR, "search_strategies.json")
    with open(strategies_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ========== 新颖性查重辅助函数（V4.0 新增） ==========

# 高频学术通用词：出现这些词表示研究主题较泛，重合风险高
_GENERIC_ACADEMIC_TERMS = {
    "研究", "分析", "应用", "设计", "方法", "基于", "系统", "模型",
    "算法", "技术", "影响", "关系", "机制", "效果", "评估", "优化",
    "构建", "实现", "探索", "创新", "改进", "对比", "预测", "识别",
    "问题", "策略", "框架", "体系", "路径", "视角", "导向", "驱动"
}

# 标题停用词：提取关键词时需剔除的功能性词汇
_TITLE_STOPWORDS = {
    "的", "与", "和", "及", "或", "在", "中", "上", "下", "以", "为",
    "基于", "面向", "针对", "关于", "通过", "利用", "使用", "采用",
    "一种", "一个", "这个", "该", "其", "之", "等", "类"
}


def _extract_title_keywords(title):
    """从候选标题中提取关键词（去除停用词与通用学术词，保留实质性术语）"""
    if not title:
        return []
    # 按非汉字/非字母数字字符切分，保留长度>=2的片段
    segments = re.split(r'[^\u4e00-\u9fa5a-zA-Z0-9]+', title)
    keywords = []
    for seg in segments:
        seg = seg.strip()
        if len(seg) < 2:
            continue
        if seg in _TITLE_STOPWORDS:
            continue
        keywords.append(seg)
    return keywords


def _generate_novelty_query(keywords, time_window, novelty_config):
    """基于候选标题关键词与时间窗口生成查重检索式"""
    templates = novelty_config.get("query_templates", [])
    # 将关键词列表拼接为检索词组
    keywords_str = " AND ".join(keywords) if keywords else "未指定关键词"
    # 解析时间窗口为年份范围
    import datetime
    current_year = datetime.datetime.now().year
    years_map = {"1y": 1, "2y": 2, "3y": 3, "5y": 5, "10y": 10}
    years_back = years_map.get(time_window, 5)
    start_year = current_year - years_back
    end_year = current_year

    queries = []
    for tpl in templates:
        template_str = tpl.get("template", "")
        query = template_str.replace("{candidate_title_keywords}", keywords_str)
        query = query.replace("{start_year}", str(start_year))
        query = query.replace("{end_year}", str(end_year))
        queries.append({"field": tpl.get("field", ""), "query": query})
    return queries


def _estimate_overlap_ratio(keywords):
    """
    基于标题关键词的通用性估算重合度（无联网检索时的本地启发式估算）。
    通用学术词占比越高、关键词越少，重合度越高。
    """
    if not keywords:
        return 0.5  # 无法提取关键词，默认中等重合
    generic_count = sum(1 for kw in keywords if kw in _GENERIC_ACADEMIC_TERMS)
    # 通用词占比越高，重合度越高
    generic_ratio = generic_count / len(keywords)
    # 基础重合度 0.3 + 通用词占比 * 0.5，范围约 [0.3, 0.8]
    overlap = 0.3 + generic_ratio * 0.5
    # 关键词越少，重合度越高（短标题更泛化）
    if len(keywords) <= 2:
        overlap += 0.1
    return round(min(overlap, 0.95), 2)


def _determine_novelty_risk(overlap_ratio, overlap_threshold):
    """基于重合度与阈值配置确定风险评级（low/medium/high）"""
    low_threshold = overlap_threshold.get("low", 0.2)
    medium_threshold = overlap_threshold.get("medium", 0.5)
    high_threshold = overlap_threshold.get("high", 0.7)
    if overlap_ratio < low_threshold:
        return "low"
    elif overlap_ratio < medium_threshold:
        return "medium"
    else:
        # 达到或超过 medium 阈值即为 high 风险
        return "high"


def _generate_differentiation_gap(keywords, overlap_ratio, risk, high_threshold):
    """生成差异化空档说明"""
    specific_keywords = [kw for kw in keywords if kw not in _GENERIC_ACADEMIC_TERMS]
    specific_str = "、".join(specific_keywords[:3]) if specific_keywords else "核心术语"
    if risk == "low":
        return (
            f"候选论题与近5年已有研究重合度较低（{overlap_ratio:.0%}），差异化空间充足。"
            f"建议聚焦「{specific_str}」方向深化，强化独特学术贡献。"
        )
    elif risk == "medium":
        return (
            f"候选论题与近5年已有研究存在部分重合（{overlap_ratio:.0%}），"
            f"建议在方法层面寻求差异化：引入新变量或迁移至新场景，"
            f"强化「{specific_str}」的创新点以区别于已有工作。"
        )
    else:
        severity = "极高" if overlap_ratio >= high_threshold else "较高"
        return (
            f"候选论题与近5年已有研究重合度{severity}（{overlap_ratio:.0%}），"
            f"需显著调整研究方向。建议：1）引入跨学科视角重构问题框架；"
            f"2）迁移至「{specific_str}」的新应用场景；"
            f"3）更换核心方法路径以建立实质性差异化。"
        )


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


# ========== 新颖性查重主函数（V4.0 新增） ==========

@timeout(30)
def check_novelty(candidate_title: str, time_window: str = "5y") -> dict:
    """
    新颖性查重评估主函数（V4.0 新增）。
    读取 search_strategies.json 的 novelty_check 配置，基于候选标题生成查重检索式，
    估算重合度并输出风险评级与差异化空档说明。

    参数:
        candidate_title: 候选论题标题
        time_window: 查重时间窗口（默认 "5y"，可选 "3y"/"5y"/"10y"）

    返回:
        标准化输出 dict，data 含：
        - overlap_ratio：重合度百分比（0~1 浮点数）
        - novelty_risk：风险评级（low/medium/high）
        - novelty_report：重合度与风险说明
        - differentiation_gap：差异化空档说明
        - search_queries：生成的查重检索式列表
    """
    try:
        if not candidate_title or not isinstance(candidate_title, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "候选标题为空或非字符串"
            }

        # 读取检索策略配置
        strategies = _load_search_strategies()
        novelty_config = strategies.get("novelty_check", {})

        # 校验时间窗口是否在可调节步长范围内
        adjustable_steps = novelty_config.get("adjustable_steps", ["3y", "5y", "10y"])
        if time_window not in adjustable_steps:
            # 不在步长范围内时降级为默认时间窗口
            time_window = novelty_config.get("default_time_window", "5y")

        # 从候选标题提取关键词
        keywords = _extract_title_keywords(candidate_title)

        # 生成查重检索式
        search_queries = _generate_novelty_query(keywords, time_window, novelty_config)

        # 估算重合度（本地启发式估算）
        overlap_ratio = _estimate_overlap_ratio(keywords)

        # 基于阈值确定风险评级
        overlap_threshold = novelty_config.get("overlap_threshold", {"low": 0.2, "medium": 0.5, "high": 0.7})
        novelty_risk = _determine_novelty_risk(overlap_ratio, overlap_threshold)
        high_threshold = overlap_threshold.get("high", 0.7)

        # 生成差异化空档说明
        differentiation_gap = _generate_differentiation_gap(
            keywords, overlap_ratio, novelty_risk, high_threshold
        )

        # 生成新颖性报告
        risk_label_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
        novelty_report = (
            f"候选标题「{candidate_title}」在近{time_window}时间窗口内的查重评估："
            f"重合度约 {overlap_ratio:.0%}，风险评级为{risk_label_map.get(novelty_risk, novelty_risk)}。"
            f"已生成 {len(search_queries)} 组查重检索式，建议联网检索后以实际结果校准重合度。"
        )

        return {
            "status": "success",
            "data": {
                "overlap_ratio": overlap_ratio,
                "novelty_risk": novelty_risk,
                "novelty_report": novelty_report,
                "differentiation_gap": differentiation_gap,
                "search_queries": search_queries
            },
            "error_message": None
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"检索策略配置文件缺失：{str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"检索策略配置文件格式错误：{str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"新颖性查重失败：{str(e)}"
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
    print("===== 硬约束校验测试 =====")
    result = check_and_repair(sample_proposal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # 新颖性查重测试（V4.0 新增）
    print("\n===== 新颖性查重测试（V4.0）=====")
    novelty_result = check_novelty("基于深度学习的医疗问答系统研究", "5y")
    print(json.dumps(novelty_result, ensure_ascii=False, indent=2))
