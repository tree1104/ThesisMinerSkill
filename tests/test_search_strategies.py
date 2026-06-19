#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索策略配置（search_strategies.json）自测。
验证灵感勘探与查重评估两阶段检索配置的结构与内容，
包括时间窗口、可调节步长、布尔运算符、查重阈值与检索模板。
"""

import sys
import os
import json

# 定位 core/references/ 目录
REFERENCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "references")
STRATEGIES_PATH = os.path.join(REFERENCES_DIR, "search_strategies.json")


def _load_strategies():
    """读取 search_strategies.json"""
    with open(STRATEGIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_file_valid_json():
    """验证文件为合法 JSON"""
    config = _load_strategies()
    assert isinstance(config, dict)
    # 应含两个配置块
    assert "inspiration_search" in config
    assert "novelty_check" in config


def test_inspiration_search_config():
    """验证灵感勘探检索配置"""
    config = _load_strategies()
    inspiration = config["inspiration_search"]
    # 默认时间窗口为 2y
    assert inspiration["default_time_window"] == "2y"
    # 可调节步长应含 1y/2y/3y/5y
    steps = inspiration["adjustable_steps"]
    assert "1y" in steps
    assert "2y" in steps
    assert "3y" in steps
    assert "5y" in steps
    # 布尔运算符应含 AND/OR/NOT
    operators = inspiration["boolean_operators"]
    assert "AND" in operators
    assert "OR" in operators
    assert "NOT" in operators


def test_novelty_check_config():
    """验证查重评估检索配置"""
    config = _load_strategies()
    novelty = config["novelty_check"]
    # 默认时间窗口为 5y
    assert novelty["default_time_window"] == "5y"
    # 可调节步长应含 3y/5y/10y
    steps = novelty["adjustable_steps"]
    assert "3y" in steps
    assert "5y" in steps
    assert "10y" in steps
    # 重合度阈值应含 low/medium/high 三个阈值
    threshold = novelty["overlap_threshold"]
    assert "low" in threshold
    assert "medium" in threshold
    assert "high" in threshold


def test_query_templates_exist():
    """验证两个配置块都有 query_templates 数组且非空"""
    config = _load_strategies()
    inspiration = config["inspiration_search"]
    novelty = config["novelty_check"]
    # 灵感勘探应有非空 query_templates
    assert "query_templates" in inspiration
    assert isinstance(inspiration["query_templates"], list)
    assert len(inspiration["query_templates"]) > 0
    # 查重评估应有非空 query_templates
    assert "query_templates" in novelty
    assert isinstance(novelty["query_templates"], list)
    assert len(novelty["query_templates"]) > 0
