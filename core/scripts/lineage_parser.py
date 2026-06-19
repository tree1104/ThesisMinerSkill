#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
谱系解析器（Lineage Parser）
解析非结构化文本，提取导师项目（名称、核心目标）与同门论文（标题、方法、局限性），
标记"未来工作"或"受限于算力/数据未展开"的边缘探测点。
基于关键词的实体抽取，不依赖外部 NLP 库，纯 Python 正则实现。
"""

import os
import re
import json
import threading
from functools import wraps


# ========== 路径常量（使用相对路径定位 references/ 与 schema/） ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(SCRIPT_DIR, "..", "references")
SCHEMA_DIR = os.path.join(SCRIPT_DIR, "..", "schema")
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
                # 超时：线程仍在运行，返回错误状态
                return {
                    "status": "error",
                    "data": None,
                    "error_message": f"执行超时（超过 {seconds} 秒）"
                }
            if exception_container[0] is not None:
                # 异常：返回错误状态
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


# ========== 关键词定义 ==========
# 导师项目相关关键词
ADVISOR_KEYWORDS = ["导师项目", "导师", "主持", "承担", "负责项目", "在研项目", "国家自然科学基金", "国家重点"]
# 项目目标关键词
OBJECTIVE_KEYWORDS = ["目标", "旨在", "致力于", "解决", "实现", "构建", "研发", "攻关", "探索"]
# 同门论文关键词
PEER_KEYWORDS = ["同门", "师兄", "师姐", "师弟", "师妹", "课题组", "实验室", "已有工作", "前期工作"]
# 论文标题关键词
TITLE_KEYWORDS = ["论文", "题目", "标题", "发表了", "完成了", "撰写"]
# 方法关键词
METHOD_KEYWORDS = ["方法", "采用", "使用", "基于", "利用", "通过", "提出", "应用"]
# 局限性关键词
LIMITATION_KEYWORDS = ["局限", "不足", "缺陷", "问题", "未能", "无法", "欠缺", "瓶颈", "受限于"]
# 边缘机会关键词（未来工作、受限于算力/数据等）
EDGE_KEYWORDS = ["未来工作", "未来研究", "受限于", "算力", "数据不足", "未展开", "有待", "进一步", "后续", "展望", "下一步"]


def _split_sentences(text):
    """将文本切分为句子（按中文标点与换行）"""
    sentences = re.split(r'[。；！？\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def _extract_advisor_projects(sentences):
    """提取导师项目（名称、核心目标）"""
    projects = []
    for sent in sentences:
        # 检测是否包含导师项目关键词
        if not any(kw in sent for kw in ADVISOR_KEYWORDS):
            continue
        name = ""
        objective = ""
        # 尝试从书名号/引号内提取项目名称
        name_match = re.search(r'[《""](.+?)[》""]', sent)
        if name_match:
            name = name_match.group(1)
        else:
            # 提取关键词后的名词短语
            for kw in ADVISOR_KEYWORDS:
                if kw in sent:
                    idx = sent.find(kw) + len(kw)
                    rest = sent[idx:idx + 20].strip("，。、的")
                    if rest:
                        name = rest[:15]
                        break
        # 提取核心目标
        for kw in OBJECTIVE_KEYWORDS:
            if kw in sent:
                idx = sent.find(kw)
                objective = sent[idx:idx + 30].strip("。；")
                break
        if not name:
            name = sent[:15]
        projects.append({
            "name": name,
            "objective": objective or "未明确提取"
        })
    return projects


def _extract_peer_papers(sentences):
    """提取同门论文（标题、方法、局限性）"""
    papers = []
    for sent in sentences:
        # 检测是否包含同门或论文关键词
        if not (any(kw in sent for kw in PEER_KEYWORDS) or any(kw in sent for kw in TITLE_KEYWORDS)):
            continue
        title = ""
        method = ""
        limitation = ""
        # 提取标题（书名号/引号内）
        title_match = re.search(r'[《""](.+?)[》""]', sent)
        if title_match:
            title = title_match.group(1)
        else:
            title = sent[:15]
        # 提取方法
        for kw in METHOD_KEYWORDS:
            if kw in sent:
                idx = sent.find(kw)
                method = sent[idx:idx + 25].strip("。；")
                break
        # 提取局限性
        for kw in LIMITATION_KEYWORDS:
            if kw in sent:
                idx = sent.find(kw)
                limitation = sent[idx:idx + 25].strip("。；")
                break
        papers.append({
            "title": title,
            "method": method or "未明确提取",
            "limitation": limitation or "未明确提取"
        })
    return papers


def _extract_edge_opportunities(sentences):
    """提取边缘探测点（未来工作、受限于算力/数据等高价值切入点）"""
    opportunities = []
    for sent in sentences:
        for kw in EDGE_KEYWORDS:
            if kw in sent:
                opportunities.append({
                    "keyword": kw,
                    "context": sent[:50],
                    "opportunity": f"基于「{kw}」的可延伸研究方向"
                })
                break  # 每个句子只记录一次
    return opportunities


# ========== 主函数 ==========
@timeout(30)
def parse_lineage(text: str) -> dict:
    """
    解析非结构化文本，提取导师项目与同门论文，标记边缘探测点。

    参数:
        text: 非结构化谱系文本

    返回:
        标准化输出 dict，data 为 LineageGraph 结构：
        {"advisor_projects": [...], "peer_papers": [...], "edge_opportunities": [...]}
    """
    try:
        if not text or not isinstance(text, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "输入文本为空或非字符串"
            }

        sentences = _split_sentences(text)
        advisor_projects = _extract_advisor_projects(sentences)
        peer_papers = _extract_peer_papers(sentences)
        edge_opportunities = _extract_edge_opportunities(sentences)

        lineage_graph = {
            "advisor_projects": advisor_projects,
            "peer_papers": peer_papers,
            "edge_opportunities": edge_opportunities
        }

        return {
            "status": "success",
            "data": lineage_graph,
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"谱系解析失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_text = """
    导师主持国家自然科学基金项目《医疗大模型研发》，旨在构建面向医疗领域的专用大语言模型。
    同门师兄的论文《基于微调的问诊系统》采用LoRA方法微调大模型，但受限于算力，仅在单一科室验证。
    师姐的研究使用提示工程方法，存在泛化能力不足的问题。
    未来工作可探索多科室联合训练，目前受限于数据未展开。
    """
    result = parse_lineage(sample_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
