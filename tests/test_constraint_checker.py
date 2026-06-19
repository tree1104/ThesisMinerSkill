#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬约束校验与修复器（constraint_checker）自测。
测试标题超长截取、动词前置转换、模式检测、学术日历、文献基线与逻辑自洽校验。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from constraint_checker import check_and_repair, check_novelty


def test_title_too_long():
    """测试超长标题自动截取"""
    # 标题超过 20 字（不含"基于"模式、不以动词开头）
    proposal = {
        "title": "医疗大模型在多科室问询场景下的微调方法与应用研究",
        "degree": "master",
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # 修复后标题长度应 <= 20
    assert len(repaired["title"]) <= 20
    # 应有截取修复记录
    repairs = result["data"]["repairs"]
    assert any("超长" in r or "截取" in r for r in repairs)


def test_title_verb_prefix():
    """测试动词前置自动转换（"研究X"→"X的研究"）"""
    proposal = {
        "title": "研究医疗问答系统",
        "degree": "master",
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # "研究医疗问答系统" → "医疗问答系统的研究"
    assert repaired["title"] == "医疗问答系统的研究"
    # 应有动词前置修复记录
    repairs = result["data"]["repairs"]
    assert any("动词前置" in r for r in repairs)


def test_title_pattern():
    """测试"基于X的Y研究"模式检测"""
    proposal = {
        "title": "基于深度学习的医疗问答系统研究",
        "degree": "master",
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # 应重写为"医疗问答系统的深度学习方法"
    assert repaired["title"] == "医疗问答系统的深度学习方法"
    # 应有模式重写修复记录
    repairs = result["data"]["repairs"]
    assert any("基于" in r or "重写" in r for r in repairs)


def test_academic_calendar():
    """测试硕士≤12月、博士≤24月"""
    # 硕士超期测试
    proposal_master = {
        "title": "测试论题",
        "degree": "master",
        "duration_months": 15,
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal_master)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # 硕士上限 12 月
    assert repaired["duration_months"] == 12
    # 应注入分阶段并行执行策略
    assert "分阶段并行执行" in repaired["research_content"]

    # 博士超期测试
    proposal_phd = {
        "title": "测试论题",
        "degree": "phd",
        "duration_months": 30,
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal_phd)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # 博士上限 24 月
    assert repaired["duration_months"] == 24


def test_literature_baseline():
    """测试文献基线注入"""
    # 硕士文献不足 30 篇
    proposal = {
        "title": "测试论题",
        "degree": "master",
        "research_content": "1. 调研；2. 设计；3. 实验。",
        "research_significance": "提升精度。",
        "literature_review_outline": "梳理相关研究，规划文献 15 篇。"
    }
    result = check_and_repair(proposal)
    assert result["status"] == "success"
    repaired = result["data"]["repaired_proposal"]
    # 应注入基线要求提示
    assert "30" in repaired["literature_review_outline"]
    assert "不少于" in repaired["literature_review_outline"]


def test_logical_consistency():
    """测试内容与目标重合度告警"""
    # 研究内容与研究意义高度重合
    same_text = "研究医疗问答系统的微调方法以提升精度"
    proposal = {
        "title": "测试论题",
        "degree": "master",
        "research_content": same_text,
        "research_significance": same_text,
        "literature_review_outline": "梳理相关研究。"
    }
    result = check_and_repair(proposal)
    assert result["status"] == "success"
    warnings = result["data"]["warnings"]
    # 应有重合度告警
    assert any("WARNING" in w or "重合度" in w for w in warnings)


# ========== V4.0 新增：新颖性查重（check_novelty）测试 ==========

def test_check_novelty_default():
    """测试默认时间窗口下的新颖性查重"""
    result = check_novelty("医疗大模型微调研究")
    assert result["status"] == "success"
    data = result["data"]
    # 应含 overlap_ratio（0~1 浮点数）
    assert "overlap_ratio" in data
    assert isinstance(data["overlap_ratio"], (int, float))
    assert 0.0 <= data["overlap_ratio"] <= 1.0
    # 应含 novelty_risk（low/medium/high）
    assert "novelty_risk" in data
    assert data["novelty_risk"] in ["low", "medium", "high"]
    # 应含 novelty_report、differentiation_gap、search_queries
    assert "novelty_report" in data
    assert isinstance(data["novelty_report"], str)
    assert "differentiation_gap" in data
    assert isinstance(data["differentiation_gap"], str)
    assert "search_queries" in data
    assert isinstance(data["search_queries"], list)


def test_check_novelty_custom_window():
    """测试自定义时间窗口 3y"""
    result = check_novelty("医疗大模型微调研究", time_window="3y")
    assert result["status"] == "success"
    data = result["data"]
    assert "overlap_ratio" in data
    assert "novelty_risk" in data
    assert "search_queries" in data
    assert len(data["search_queries"]) > 0


def test_check_novelty_empty_title():
    """测试空标题返回 status=error"""
    result = check_novelty("")
    assert result["status"] == "error"
    assert result["data"] is None
    assert result["error_message"] is not None


def test_check_novelty_risk_enum():
    """验证 novelty_risk 值为 low/medium/high 之一"""
    # 测试多个候选标题，确保风险评级始终在枚举范围内
    titles = [
        "医疗大模型微调研究",
        "基于深度学习的问答系统",
        "知识图谱构建方法探索"
    ]
    for title in titles:
        result = check_novelty(title)
        assert result["status"] == "success"
        assert result["data"]["novelty_risk"] in ["low", "medium", "high"]
