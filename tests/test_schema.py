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
