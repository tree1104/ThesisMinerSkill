#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
谱系解析器（lineage_parser）自测。
测试 parse_lineage 接口的导师项目提取、同门论文提取、边缘探测、空输入处理与标准化输出。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from lineage_parser import parse_lineage


def test_parse_advisor_project():
    """测试从文本中提取导师项目（名称、目标）"""
    text = (
        "导师主持国家自然科学基金项目《医疗大模型研发》，"
        "旨在构建面向医疗领域的专用大语言模型。"
    )
    result = parse_lineage(text)
    assert result["status"] == "success"
    projects = result["data"]["advisor_projects"]
    assert len(projects) >= 1
    project = projects[0]
    # 应包含名称与目标字段
    assert "name" in project
    assert "objective" in project
    # 名称应包含核心项目名
    assert "医疗大模型" in project["name"]
    # 目标应成功提取（非默认占位）
    assert project["objective"] != "未明确提取"


def test_parse_peer_papers():
    """测试提取同门论文（标题、方法、局限性）"""
    text = (
        "同门师兄的论文《基于微调的问诊系统》采用LoRA方法微调大模型，"
        "但受限于算力，仅在单一科室验证。"
    )
    result = parse_lineage(text)
    assert result["status"] == "success"
    papers = result["data"]["peer_papers"]
    assert len(papers) >= 1
    paper = papers[0]
    # 应包含标题、方法、局限性字段
    assert "title" in paper
    assert "method" in paper
    assert "limitation" in paper
    # 标题应包含核心论文标题
    assert "微调" in paper["title"] or "问诊" in paper["title"]
    # 方法应成功提取（非默认占位），且包含方法相关关键词
    assert paper["method"] != "未明确提取"
    assert "微调" in paper["method"] or "方法" in paper["method"]


def test_edge_detection():
    """测试边缘探测（未来工作、算力/数据限制）"""
    text = (
        "未来工作可探索多科室联合训练。"
        "目前受限于数据未展开。"
    )
    result = parse_lineage(text)
    assert result["status"] == "success"
    opportunities = result["data"]["edge_opportunities"]
    assert len(opportunities) >= 1
    # 至少检测到一个边缘探测点
    keywords = [opp["keyword"] for opp in opportunities]
    # 应包含"未来工作"或"受限于"等关键词
    assert any(kw in keywords for kw in ["未来工作", "受限于", "算力", "数据不足", "未展开"])


def test_empty_input():
    """测试空输入返回 status:error"""
    result = parse_lineage("")
    assert result["status"] == "error"
    assert result["data"] is None
    assert result["error_message"] is not None


def test_standard_output():
    """测试返回 dict 含 status/data/error_message"""
    text = "导师主持项目《测试项目》，旨在验证接口。"
    result = parse_lineage(text)
    assert isinstance(result, dict)
    assert "status" in result
    assert "data" in result
    assert "error_message" in result
