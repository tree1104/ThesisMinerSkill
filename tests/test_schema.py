#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I/O Schema 自测。
验证 input_schema.json 与 output_schema.json 为合法 JSON Schema，
检查必填字段、枚举值，并用样例数据验证校验通过。
"""

import sys
import os
import json

# 将 core/schema/ 路径加入以便读取 Schema 文件
SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "schema")

from jsonschema import Draft7Validator


# ========== 加载 Schema ==========

def _load_input_schema():
    """读取 input_schema.json"""
    with open(os.path.join(SCHEMA_DIR, "input_schema.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def _load_output_schema():
    """读取 output_schema.json"""
    with open(os.path.join(SCHEMA_DIR, "output_schema.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def test_input_schema_valid():
    """验证 input_schema.json 为合法 JSON Schema"""
    schema = _load_input_schema()
    # Draft7Validator.check_schema 验证 Schema 本身是否合法
    Draft7Validator.check_schema(schema)


def test_output_schema_valid():
    """验证 output_schema.json 为合法 JSON Schema"""
    schema = _load_output_schema()
    Draft7Validator.check_schema(schema)


def test_input_required_fields():
    """验证 degree 与 lineage 为 required"""
    schema = _load_input_schema()
    assert "required" in schema
    assert "degree" in schema["required"]
    assert "lineage" in schema["required"]


def test_input_enum_values():
    """验证 degree 枚举（master/phd）、strategy 枚举（四策略+all）"""
    schema = _load_input_schema()
    # degree 枚举
    degree_enum = schema["properties"]["degree"]["enum"]
    assert "master" in degree_enum
    assert "phd" in degree_enum
    # strategy 枚举
    strategy_enum = schema["properties"]["strategy"]["enum"]
    assert "advisor_extension" in strategy_enum
    assert "peer_inheritance" in strategy_enum
    assert "cross_domain" in strategy_enum
    assert "contradiction_driven" in strategy_enum
    assert "all" in strategy_enum


def test_output_status_enum():
    """验证 status 枚举（success/retry/error）"""
    schema = _load_output_schema()
    status_enum = schema["properties"]["status"]["enum"]
    assert "success" in status_enum
    assert "retry" in status_enum
    assert "error" in status_enum


def test_sample_input_validation():
    """用样例数据验证 input_schema 校验通过"""
    schema = _load_input_schema()
    sample_input = {
        "degree": "master",
        "lineage": {
            "advisor_projects": [
                {"name": "医疗大模型研发", "objective": "构建专用大语言模型"}
            ],
            "peer_papers": [
                {"title": "微调问诊系统", "method": "LoRA微调", "limitation": "算力受限"}
            ],
            "edge_opportunities": [
                {"keyword": "受限于", "context": "受限于算力", "opportunity": "可延伸方向"}
            ]
        },
        "strategy": "all",
        "count": 3
    }
    # 应校验通过，不抛出异常
    Draft7Validator(schema).validate(sample_input)


def test_sample_output_validation():
    """用样例数据验证 output_schema 校验通过"""
    schema = _load_output_schema()
    sample_output = {
        "status": "success",
        "data": {
            "proposals": [
                {
                    "title": "医疗大模型微调研究",
                    "problem_awareness": "精度不足",
                    "research_significance": "提升精度",
                    "differentiation": "科室微调",
                    "research_content": "1. 调研；2. 实验",
                    "literature_review_outline": "梳理研究",
                    "score": 7.5
                }
            ]
        }
    }
    # 应校验通过，不抛出异常
    Draft7Validator(schema).validate(sample_output)


# ========== V4.0 新增字段验证 ==========

def test_input_new_fields():
    """验证 input_schema 含 V4.0 新增字段"""
    schema = _load_input_schema()
    props = schema["properties"]
    # output_granularity 枚举 concise/standard/detailed
    assert "output_granularity" in props
    granularity_enum = props["output_granularity"]["enum"]
    assert "concise" in granularity_enum
    assert "standard" in granularity_enum
    assert "detailed" in granularity_enum
    # inspiration_time_window 枚举 1y/2y/3y/5y
    assert "inspiration_time_window" in props
    inspiration_enum = props["inspiration_time_window"]["enum"]
    assert "1y" in inspiration_enum
    assert "2y" in inspiration_enum
    assert "3y" in inspiration_enum
    assert "5y" in inspiration_enum
    # novelty_time_window 枚举 3y/5y/10y
    assert "novelty_time_window" in props
    novelty_enum = props["novelty_time_window"]["enum"]
    assert "3y" in novelty_enum
    assert "5y" in novelty_enum
    assert "10y" in novelty_enum


def test_output_novelty_fields():
    """验证 output_schema 的 proposals items 含新颖性字段"""
    schema = _load_output_schema()
    proposal_item_props = schema["properties"]["data"]["properties"]["proposals"]["items"]["properties"]
    # novelty_risk 枚举 low/medium/high
    assert "novelty_risk" in proposal_item_props
    novelty_risk_enum = proposal_item_props["novelty_risk"]["enum"]
    assert "low" in novelty_risk_enum
    assert "medium" in novelty_risk_enum
    assert "high" in novelty_risk_enum
    # novelty_report 字符串类型
    assert "novelty_report" in proposal_item_props
    assert proposal_item_props["novelty_report"]["type"] == "string"


def test_output_high_plagiarism_field():
    """验证 output_schema 的 data 含 high_plagiarism_risk_sections（array）"""
    schema = _load_output_schema()
    data_props = schema["properties"]["data"]["properties"]
    assert "high_plagiarism_risk_sections" in data_props
    assert data_props["high_plagiarism_risk_sections"]["type"] == "array"


def test_output_next_actions_field():
    """验证 output_schema 顶层含 next_actions（array, items enum）"""
    schema = _load_output_schema()
    props = schema["properties"]
    assert "next_actions" in props
    assert props["next_actions"]["type"] == "array"
    # items 应含 enum：literature_deep_reading/experiment_design/defense_simulation
    items_enum = props["next_actions"]["items"]["enum"]
    assert "literature_deep_reading" in items_enum
    assert "experiment_design" in items_enum
    assert "defense_simulation" in items_enum


def test_sample_v4_output_validation():
    """用含 novelty_risk 和 next_actions 的样例数据验证 output_schema 校验通过"""
    schema = _load_output_schema()
    sample_v4_output = {
        "status": "success",
        "data": {
            "proposals": [
                {
                    "title": "医疗大模型微调研究",
                    "problem_awareness": "精度不足",
                    "research_significance": "提升精度",
                    "differentiation": "科室微调",
                    "research_content": "1. 调研；2. 实验",
                    "literature_review_outline": "梳理研究",
                    "score": 7.5,
                    "novelty_risk": "medium",
                    "novelty_report": "候选论题与近5年已有研究存在部分重合，建议在方法层面寻求差异化。"
                }
            ],
            "high_plagiarism_risk_sections": []
        },
        "next_actions": ["literature_deep_reading", "experiment_design", "defense_simulation"]
    }
    # 应校验通过，不抛出异常
    Draft7Validator(schema).validate(sample_v4_output)
