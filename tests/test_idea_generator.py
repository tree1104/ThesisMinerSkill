#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四维创意引擎（idea_generator）自测。
测试导师项目延伸、同门成果继承、跨域联想、矛盾驱动四种策略，
以及自评分过滤与 all 策略多提案生成。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from idea_generator import generate_ideas
import idea_generator


# ========== 公共测试数据 ==========

SAMPLE_LINEAGE = {
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


def test_advisor_extension():
    """测试导师项目延伸策略"""
    result = generate_ideas(SAMPLE_LINEAGE, "advisor_extension", "master")
    assert result["status"] == "success"
    proposals = result["data"]["proposals"]
    assert len(proposals) >= 1
    for p in proposals:
        assert p["strategy"] == "advisor_extension"
        assert "title" in p
        assert "score" in p


def test_peer_inheritance():
    """测试同门成果继承策略"""
    result = generate_ideas(SAMPLE_LINEAGE, "peer_inheritance", "master")
    assert result["status"] == "success"
    proposals = result["data"]["proposals"]
    assert len(proposals) >= 1
    for p in proposals:
        assert p["strategy"] == "peer_inheritance"


def test_cross_domain():
    """测试跨域联想策略"""
    result = generate_ideas(SAMPLE_LINEAGE, "cross_domain", "master")
    assert result["status"] == "success"
    proposals = result["data"]["proposals"]
    assert len(proposals) >= 1
    for p in proposals:
        assert p["strategy"] == "cross_domain"


def test_contradiction_driven():
    """测试矛盾驱动策略"""
    result = generate_ideas(SAMPLE_LINEAGE, "contradiction_driven", "master")
    assert result["status"] == "success"
    proposals = result["data"]["proposals"]
    assert len(proposals) >= 1
    for p in proposals:
        assert p["strategy"] == "contradiction_driven"


def test_scoring_filter(monkeypatch):
    """测试自评分过滤（<6分被过滤）"""
    # 1. 正常评分下，所有提案分数应 >= 6（不被过滤）
    result = generate_ideas(SAMPLE_LINEAGE, "advisor_extension", "master")
    assert result["status"] == "success"
    for p in result["data"]["proposals"]:
        assert p["score"] >= 6

    # 2. 模拟低分（<6），验证被过滤
    monkeypatch.setattr(idea_generator, "_score_proposal", lambda p, d, s, w: 5.0)
    result = generate_ideas(SAMPLE_LINEAGE, "advisor_extension", "master")
    assert result["status"] == "success"
    # 全部提案评分为 5.0 < 6，应被过滤
    assert len(result["data"]["proposals"]) == 0


def test_all_strategy():
    """测试 all 策略生成多提案"""
    result = generate_ideas(SAMPLE_LINEAGE, "all", "master")
    assert result["status"] == "success"
    proposals = result["data"]["proposals"]
    # all 策略应生成多个提案
    assert len(proposals) >= 2
    # 应包含多种策略
    strategies = {p["strategy"] for p in proposals}
    assert len(strategies) >= 2
