#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度辅助三件套（deep_helper）自测。
测试文献精读工作簿生成、实验/应用预研映射（理工/数学/社科）、
答辩模拟（逻辑压力测试）三大功能，以及空输入处理。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from deep_helper import literature_deep_reader, experiment_designer, thesis_defense_simulator


# ========== 公共测试数据 ==========

SAMPLE_RESEARCH_STATUS = (
    "近年来，大语言模型在医疗问询领域取得显著进展。"
    "LoRA微调方法降低了训练成本，但存在科室泛化能力不足的问题。"
    "提示工程方法无需训练，但效果受限于提示设计。"
)

SAMPLE_RESEARCH_CONTENT = "本研究设计基于深度学习的医疗问询微调方案，对比基线模型验证效果。"

SAMPLE_KEY_PROBLEMS = (
    "本方法可能显著提升医疗问询精度，"
    "所有测试场景下均表现出明显优势，"
    "众所周知深度学习需要大量数据。"
)


def test_literature_deep_reader():
    """测试文献精读工作簿生成"""
    result = literature_deep_reader(SAMPLE_RESEARCH_STATUS, count=3)
    assert result["status"] == "success"
    workbooks = result["data"]["reading_workbooks"]
    # 应生成 3 篇文献精读框架
    assert len(workbooks) == 3
    for wb in workbooks:
        # 三明治拆解应含 motivation/method/limitation
        assert "sandwich_analysis" in wb
        sandwich = wb["sandwich_analysis"]
        assert "motivation" in sandwich
        assert "method" in sandwich
        assert "limitation" in sandwich
        # GAP 分析
        assert "gap_analysis" in wb
        # 可借鉴图表
        assert "borrowable_charts" in wb
        assert isinstance(wb["borrowable_charts"], list)


def test_experiment_designer_stem():
    """测试理工/计算机类实验预研映射"""
    result = experiment_designer(SAMPLE_RESEARCH_CONTENT, "stem")
    assert result["status"] == "success"
    design_plan = result["data"]["design_plan"]
    # 应含库版本、核心算法伪代码、基线对比计划
    assert "library_versions" in design_plan
    assert isinstance(design_plan["library_versions"], list)
    assert "core_algorithm_pseudocode" in design_plan
    assert "baseline_comparison_plan" in design_plan
    assert isinstance(design_plan["baseline_comparison_plan"], list)


def test_experiment_designer_math():
    """测试数学/理论类证明路径图谱"""
    result = experiment_designer(SAMPLE_RESEARCH_CONTENT, "math")
    assert result["status"] == "success"
    design_plan = result["data"]["design_plan"]
    # 应含前置引理、核心引理构造、数值算例验证
    assert "preliminary_lemmas" in design_plan
    assert isinstance(design_plan["preliminary_lemmas"], list)
    assert "core_lemma_construction" in design_plan
    assert "numerical_verification" in design_plan
    assert isinstance(design_plan["numerical_verification"], list)


def test_experiment_designer_social():
    """测试社科/商科类调研方案设计"""
    result = experiment_designer(SAMPLE_RESEARCH_CONTENT, "social")
    assert result["status"] == "success"
    design_plan = result["data"]["design_plan"]
    # 应含问卷量表映射、抽样策略、数据分析模型
    assert "questionnaire_scale_mapping" in design_plan
    assert isinstance(design_plan["questionnaire_scale_mapping"], list)
    assert "sampling_strategy" in design_plan
    assert "data_analysis_models" in design_plan
    assert isinstance(design_plan["data_analysis_models"], list)


def test_experiment_designer_invalid_discipline():
    """测试未知学科类型返回 status=error"""
    result = experiment_designer(SAMPLE_RESEARCH_CONTENT, "invalid")
    assert result["status"] == "error"
    assert result["data"] is None
    assert result["error_message"] is not None


def test_thesis_defense_simulator():
    """测试答辩模拟（逻辑压力测试）"""
    result = thesis_defense_simulator(SAMPLE_KEY_PROBLEMS, rounds=3)
    assert result["status"] == "success"
    data = result["data"]
    # 应生成 3 轮答辩
    defense_rounds = data["defense_rounds"]
    assert len(defense_rounds) == 3
    for rnd in defense_rounds:
        # 每轮应含 focus 和 questions
        assert "focus" in rnd
        assert "questions" in rnd
        assert isinstance(rnd["questions"], list)
        assert len(rnd["questions"]) > 0
    # weakness_points 应为列表
    assert "weakness_points" in data
    assert isinstance(data["weakness_points"], list)


def test_empty_inputs():
    """测试三个函数分别传空字符串返回 status=error"""
    # 文献精读工作簿
    result1 = literature_deep_reader("", count=3)
    assert result1["status"] == "error"
    assert result1["data"] is None
    assert result1["error_message"] is not None

    # 实验预研映射
    result2 = experiment_designer("", "stem")
    assert result2["status"] == "error"
    assert result2["data"] is None
    assert result2["error_message"] is not None

    # 答辩模拟
    result3 = thesis_defense_simulator("", rounds=3)
    assert result3["status"] == "error"
    assert result3["data"] is None
    assert result3["error_message"] is not None
