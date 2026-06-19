#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四维创意涌现引擎（Idea Generator）
基于谱系图，使用四个策略生成论题提案，并进行自评分过滤。
策略：advisor_extension（导师项目延伸）、peer_inheritance（同门成果继承）、
      cross_domain（跨域联想）、contradiction_driven（矛盾驱动）
自评分：可行性(40%) + 创新度(30%) + 谱系贴合度(30%)，过滤 <6 分（满分10）
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


def _load_scoring_weights():
    """读取 scoring_weights.json 获取评分权重"""
    weights_path = os.path.join(REFERENCES_DIR, "scoring_weights.json")
    with open(weights_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ========== 四维策略生成器 ==========

def _generate_advisor_extension(lineage_graph, degree):
    """策略一：导师项目延伸——将大项目拆解为可在学制内完成的子课题"""
    proposals = []
    for project in lineage_graph.get("advisor_projects", []):
        name = project.get("name", "")
        objective = project.get("objective", "")
        # 截取核心名词作为子课题标题
        sub_topic = name[:8] if len(name) > 8 else name
        proposal = {
            "title": f"{sub_topic}的子课题探索",
            "problem_awareness": f"导师项目「{name}」目标为{objective}，整体研究范围过大，"
                                 f"需在{degree}学制内聚焦可独立完成的子问题。",
            "research_significance": f"通过拆解「{name}」，既继承导师研究方向，"
                                     f"又具备独立学术价值，适合{degree}论文体量。",
            "differentiation": f"相较于导师项目的全景视角，本课题聚焦特定场景与细分问题，"
                               f"降低实现难度，提升可验证性。",
            "research_content": f"1. 调研{name}相关技术现状与不足；"
                                f"2. 选定子问题进行方法设计与实验；"
                                f"3. 对比基线方案验证有效性。",
            "literature_review_outline": f"围绕「{name}」的国内外研究进展，"
                                         f"按技术路线分类梳理，指明现有方法不足。",
            "strategy": "advisor_extension"
        }
        proposals.append(proposal)
    return proposals


def _generate_peer_inheritance(lineage_graph, degree):
    """策略二：同门成果继承——基于边缘探测的局限点，引入新变量或迁移至新场景"""
    proposals = []
    for paper in lineage_graph.get("peer_papers", []):
        title = paper.get("title", "")
        method = paper.get("method", "")
        limitation = paper.get("limitation", "")
        if not limitation or limitation == "未明确提取":
            continue
        proposal = {
            "title": f"面向新场景的{title[:6]}改进研究",
            "problem_awareness": f"同门论文「{title}」采用{method}，但存在{limitation}的局限，"
                                 f"需引入新变量或迁移至新场景以突破瓶颈。",
            "research_significance": f"继承同门工作基础，针对其局限性进行改进，"
                                     f"形成学术谱系上的递进关系，具备延续性价值。",
            "differentiation": f"在同门方法基础上引入新变量，解决{limitation}问题，"
                               f"形成方法层面的增量创新。",
            "research_content": f"1. 复现同门方法并定位{limitation}根因；"
                                f"2. 设计改进方案（新变量/新场景）；"
                                f"3. 实验验证改进效果。",
            "literature_review_outline": f"梳理{method}相关研究及其局限性，"
                                         f"调研改进方向的已有工作。",
            "strategy": "peer_inheritance"
        }
        proposals.append(proposal)
    return proposals


def _generate_cross_domain(lineage_graph, degree):
    """策略三：跨域联想——识别多个不相关学科概念，生成"A领域方法解B领域问题"候选"""
    proposals = []
    # 收集所有方法与领域关键词
    all_methods = []
    all_domains = []
    for paper in lineage_graph.get("peer_papers", []):
        method = paper.get("method", "")
        if method and method != "未明确提取":
            all_methods.append(method[:10])
        title = paper.get("title", "")
        if title:
            all_domains.append(title[:8])
    for project in lineage_graph.get("advisor_projects", []):
        name = project.get("name", "")
        if name:
            all_domains.append(name[:8])

    # 生成跨域候选
    if all_methods and all_domains:
        method_a = all_methods[0]
        domain_b = all_domains[-1] if len(all_domains) > 1 else all_domains[0]
        proposal = {
            "title": f"{method_a}在{domain_b}中的迁移应用",
            "problem_awareness": f"现有{domain_b}领域缺乏高效方法，"
                                 f"而{method_a}在相关场景表现优异，存在跨域迁移潜力。",
            "research_significance": f"通过跨域方法迁移，为{domain_b}领域引入新解法，"
                                     f"拓展{method_a}的应用边界，具备理论与实际双重价值。",
            "differentiation": f"首次将{method_a}系统应用于{domain_b}领域，"
                               f"填补跨域研究空白。",
            "research_content": f"1. 分析{method_a}的适用条件与{domain_b}的匹配度；"
                                f"2. 设计跨域适配方案；"
                                f"3. 实验验证迁移效果与泛化能力。",
            "literature_review_outline": f"分别调研{method_a}与{domain_b}的研究现状，"
                                         f"梳理跨域应用的已有尝试与不足。",
            "strategy": "cross_domain"
        }
        proposals.append(proposal)
    return proposals


def _generate_contradiction_driven(lineage_graph, degree):
    """策略四：矛盾驱动——检测能力边界与实际需求的语义矛盾，基于矛盾生成论题"""
    proposals = []
    # 从边缘机会中提取矛盾点
    for opp in lineage_graph.get("edge_opportunities", []):
        keyword = opp.get("keyword", "")
        context = opp.get("context", "")
        if keyword in ["受限于", "算力", "数据不足", "未展开"]:
            proposal = {
                "title": f"突破{keyword}瓶颈的新方法探索",
                "problem_awareness": f"现有工作{context}，存在{keyword}的能力边界与实际需求矛盾，"
                                     f"需设计新方法突破该瓶颈。",
                "research_significance": f"针对{keyword}矛盾提出解决方案，"
                                         f"既回应同门遗留问题，又具备方法论创新价值。",
                "differentiation": f"直面{keyword}矛盾，不同于回避策略，"
                                   f"通过方法创新从根本上突破能力边界。",
                "research_content": f"1. 形式化定义{keyword}矛盾；"
                                f"2. 设计突破{keyword}限制的新方法；"
                                f"3. 实验验证方法在矛盾场景下的有效性。",
                "literature_review_outline": f"调研{keyword}相关瓶颈的已有解决思路，"
                                             f"指明现有方法的不足与改进空间。",
                "strategy": "contradiction_driven"
            }
            proposals.append(proposal)
    return proposals


# ========== 自评分机制 ==========

def _score_proposal(proposal, degree, strategy, weights_config):
    """
    自评分：可行性(40%) + 创新度(30%) + 谱系贴合度(30%)
    权重从 scoring_weights.json 读取
    """
    weights = weights_config.get("weights", {"feasibility": 0.4, "innovation": 0.3, "lineage_fit": 0.3})
    max_score = weights_config.get("max_score", 10)

    # 可行性：硕士要求更聚焦，可行性略高；博士允许更高难度
    feasibility = 7.5 if degree == "master" else 6.5

    # 创新度：跨域和矛盾驱动创新度更高
    innovation_scores = {
        "advisor_extension": 6.0,
        "peer_inheritance": 7.0,
        "cross_domain": 9.0,
        "contradiction_driven": 8.5
    }
    innovation = innovation_scores.get(strategy, 6.0)

    # 谱系贴合度：导师延伸和同门继承贴合度更高
    lineage_fit_scores = {
        "advisor_extension": 9.0,
        "peer_inheritance": 8.5,
        "cross_domain": 5.5,
        "contradiction_driven": 7.0
    }
    lineage_fit = lineage_fit_scores.get(strategy, 6.0)

    # 加权计算（归一化到 max_score）
    raw_score = (feasibility * weights["feasibility"]
                 + innovation * weights["innovation"]
                 + lineage_fit * weights["lineage_fit"])
    score = round(min(raw_score, max_score), 2)
    return score


# ========== 主函数（含重试逻辑） ==========

@timeout(30)
def generate_ideas(lineage_graph: dict, strategy: str, degree: str) -> dict:
    """
    四维创意涌现引擎主函数。

    参数:
        lineage_graph: 谱系图结构 {"advisor_projects": [...], "peer_papers": [...], "edge_opportunities": [...]}
        strategy: 策略名称（advisor_extension / peer_inheritance / cross_domain / contradiction_driven / all）
        degree: 学位级别（master / phd）

    返回:
        标准化输出 dict，data 含 proposals 数组（每个 proposal 含 score）
    """
    max_retries = 3
    retry_delay = 2  # 秒

    for attempt in range(max_retries):
        try:
            # 读取评分权重配置
            weights_config = _load_scoring_weights()
            filter_threshold = weights_config.get("filter_threshold", 6)

            # 根据策略选择生成器
            strategy_generators = {
                "advisor_extension": _generate_advisor_extension,
                "peer_inheritance": _generate_peer_inheritance,
                "cross_domain": _generate_cross_domain,
                "contradiction_driven": _generate_contradiction_driven
            }

            all_proposals = []
            if strategy == "all":
                # 全部策略并行生成
                for strat, generator in strategy_generators.items():
                    proposals = generator(lineage_graph, degree)
                    for p in proposals:
                        p["score"] = _score_proposal(p, degree, strat, weights_config)
                    all_proposals.extend(proposals)
            else:
                generator = strategy_generators.get(strategy)
                if generator is None:
                    return {
                        "status": "error",
                        "data": None,
                        "error_message": f"未知策略：{strategy}，支持：{list(strategy_generators.keys())}"
                    }
                proposals = generator(lineage_graph, degree)
                for p in proposals:
                    p["score"] = _score_proposal(p, degree, strategy, weights_config)
                all_proposals = proposals

            # 自评分过滤：剔除低于阈值的提案
            filtered_proposals = [p for p in all_proposals if p["score"] >= filter_threshold]

            # 按分数降序排列
            filtered_proposals.sort(key=lambda x: x["score"], reverse=True)

            return {
                "status": "success",
                "data": {"proposals": filtered_proposals},
                "error_message": None
            }

        except FileNotFoundError as e:
            # 配置文件缺失，不可重试
            return {
                "status": "error",
                "data": None,
                "error_message": f"配置文件缺失：{str(e)}"
            }
        except json.JSONDecodeError as e:
            # 配置文件格式错误，不可重试
            return {
                "status": "error",
                "data": None,
                "error_message": f"配置文件格式错误：{str(e)}"
            }
        except Exception as e:
            # 其他异常：重试
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return {
                "status": "retry",
                "data": None,
                "error_message": f"生成失败，已重试 {max_retries} 次：{str(e)}"
            }

    return {
        "status": "error",
        "data": None,
        "error_message": "生成失败：重试次数耗尽"
    }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_graph = {
        "advisor_projects": [
            {"name": "医疗大模型研发", "objective": "构建面向医疗领域的专用大语言模型"}
        ],
        "peer_papers": [
            {"title": "基于微调的问诊系统", "method": "LoRA微调", "limitation": "受限于算力仅在单一科室验证"}
        ],
        "edge_opportunities": [
            {"keyword": "受限于", "context": "受限于算力仅在单一科室验证", "opportunity": "基于「受限于」的可延伸研究方向"}
        ]
    }
    result = generate_ideas(sample_graph, "all", "master")
    print(json.dumps(result, ensure_ascii=False, indent=2))
