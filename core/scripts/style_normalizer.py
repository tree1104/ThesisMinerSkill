#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术风格中性化处理器（Style Normalizer）
读取 core/references/forbidden_ai_phrases.json 获取禁用词映射，
执行词频替换、句首禁用词过滤、主动被动态互换，去除 AI 痕迹。
基于规则匹配与正则替换，不依赖外部 NLP 库，纯 Python 实现。
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


# ========== 内置禁用词映射（forbidden_ai_phrases.json 缺失时的降级方案） ==========
# 收录高频 AI 化术语及学术中性映射，确保脚本在配置文件缺失时仍可运行
_DEFAULT_PHRASE_MAP = {
    # 词频替换：AI 化术语 -> 学术中性表达
    "显著提升": "呈现正向关联",
    "显著降低": "呈现负向关联",
    "显著改善": "有所改善",
    "大幅提高": "有所提升",
    "大幅降低": "有所下降",
    "极大地": "在一定程度上",
    "充分证明": "初步表明",
    "充分说明": "初步说明",
    "完全解决": "部分缓解",
    "彻底解决": "有效缓解",
    "深入探讨": "进行分析",
    "全面分析": "进行梳理",
    "系统性研究": "分项研究",
    "创新性地": "尝试性地",
    "高效地": "较为有效地",
    "有效地": "在一定程度上",
    "值得注意的是": "需要指出",
    "值得一提的是": "需要指出",
    # 句首禁用词（值为空字符串表示需移除）
    "首先": "",
    "其次": "",
    "再次": "",
    "最后": "",
    "此外": "",
    "另外": "",
    "综上所述": "由此可见",
    "总而言之": "整体来看",
    "总之": "整体来看",
    # 主动语态 -> 被动/中性表达
    "我们提出": "本研究提出",
    "我们设计": "本研究设计",
    "我们认为": "研究认为",
    "我们发现": "研究表明",
    "我们采用": "本研究采用",
    "我们实现": "本研究实现",
    "我们构建": "本研究构建",
    "本文提出": "本研究提出",
    "本文设计": "本研究设计",
    "本文采用": "本研究采用",
    "本文认为": "研究认为",
    "本文实现": "本研究实现",
    "本文构建": "本研究构建",
}

# 句首禁用词默认列表（用于文件缺失时识别需移除的句首词）
_DEFAULT_SENTENCE_START_FORBIDDEN = [
    "首先", "其次", "再次", "最后", "此外", "另外",
    "综上所述", "总而言之", "总之", "值得一提的是", "值得注意的是"
]

# 主动语态转换默认模式（含"我们"/"本文"的条目）
_DEFAULT_VOICE_PATTERNS = [
    (r"我们提出", "本研究提出"),
    (r"我们设计", "本研究设计"),
    (r"我们认为", "研究认为"),
    (r"我们发现", "研究表明"),
    (r"我们采用", "本研究采用"),
    (r"我们实现", "本研究实现"),
    (r"我们构建", "本研究构建"),
    (r"本文提出", "本研究提出"),
    (r"本文设计", "本研究设计"),
    (r"本文采用", "本研究采用"),
    (r"本文认为", "研究认为"),
    (r"本文实现", "本研究实现"),
    (r"本文构建", "本研究构建"),
]


def _load_forbidden_phrases():
    """
    读取 forbidden_ai_phrases.json 获取禁用词映射。
    文件缺失或格式错误时，降级使用内置默认映射，确保脚本可用性。
    """
    phrases_path = os.path.join(REFERENCES_DIR, "forbidden_ai_phrases.json")
    try:
        with open(phrases_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 支持两种结构：直接映射 dict 或含 phrase_map 字段的 dict
        if isinstance(config, dict) and "phrase_map" in config:
            phrase_map = config["phrase_map"]
        elif isinstance(config, dict):
            phrase_map = config
        else:
            phrase_map = {}
        # 合并内置映射（文件配置优先，覆盖默认值）
        merged = dict(_DEFAULT_PHRASE_MAP)
        merged.update(phrase_map)
        return merged
    except (FileNotFoundError, json.JSONDecodeError):
        # 文件缺失或格式错误，降级使用内置映射
        return dict(_DEFAULT_PHRASE_MAP)


# ========== 文本处理辅助函数 ==========

def _split_paragraphs(text):
    """按空行切分段落"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def _split_sentences(text):
    """将文本切分为句子（按中文标点与换行，保留标点用于重建）"""
    # 使用正则找出所有句子（含结尾标点）
    sentences = re.findall(r'[^。；！？\n]*[。；！？\n]?', text)
    return [s for s in sentences if s.strip()]


def _replace_phrases(text, phrase_map):
    """
    词频替换：将 AI 化术语替换为学术中性表达。
    跳过值为空字符串的条目（句首禁用词由专门函数处理）。
    """
    replacements_count = 0
    normalized = text
    for ai_phrase, neutral_phrase in phrase_map.items():
        # 跳过句首禁用词（值为空字符串），交由 _filter_sentence_start 处理
        if neutral_phrase == "":
            continue
        if ai_phrase in normalized:
            count = normalized.count(ai_phrase)
            normalized = normalized.replace(ai_phrase, neutral_phrase)
            replacements_count += count
    return normalized, replacements_count


def _filter_sentence_start(text, forbidden_starts):
    """
    句首禁用词过滤：移除"首先/其次/综上所述"等句首词。
    匹配位于文本起始或句号/分号/感叹号/问号/换行之后的禁用词。
    """
    removed_count = 0
    normalized = text
    for start_word in forbidden_starts:
        # 构造正则：句首位置（^ 或标点之后）+ 禁用词 + 可选的逗号/顿号
        pattern = r'(^|[。；！？\n])\s*' + re.escape(start_word) + r'[，、,]?\s*'
        matches = re.findall(pattern, normalized)
        removed_count += len(matches)
        # 保留前置标点，移除禁用词及其后的逗号
        normalized = re.sub(pattern, r'\1', normalized)
    return normalized, removed_count


def _swap_voice(text, voice_patterns):
    """
    主动被动态互换：将"我们提出/本文设计"等主动语态转为被动或中性表达。
    使用正则替换，统计替换次数。
    """
    swap_count = 0
    normalized = text
    for pattern, replacement in voice_patterns:
        new_text, n = re.subn(pattern, replacement, normalized)
        if n > 0:
            normalized = new_text
            swap_count += n
    return normalized, swap_count


def _detect_high_risk_sections(text, phrase_map):
    """
    检测仍存在高重复风险的段落。
    基于段落长度、"的"字密度、列举式标记、句子平均长度等信号综合判断。
    """
    high_risk = []
    paragraphs = _split_paragraphs(text)
    for idx, para in enumerate(paragraphs):
        risk_signals = 0
        risk_reasons = []
        # 信号1：段落过短（<50字），疑似模板化填充
        if len(para) < 50:
            risk_signals += 1
            risk_reasons.append("段落过短")
        # 信号2："的"字结构密度过高（>5%），疑似定语堆砌
        if len(para) > 0 and para.count("的") / len(para) > 0.05:
            risk_signals += 1
            risk_reasons.append("\"的\"字密度过高")
        # 信号3：含列举式标记（1. 2. 3. 或 ① ② ③），疑似流水账
        if re.search(r'[1-9][\.、]\s*\S|①②③④⑤', para):
            risk_signals += 1
            risk_reasons.append("列举式标记密集")
        # 信号4：句子平均长度过短（<15字），疑似碎片化
        sentences = _split_sentences(para)
        if sentences and sum(len(s) for s in sentences) / len(sentences) < 15:
            risk_signals += 1
            risk_reasons.append("句子碎片化")
        # 信号5：仍残留禁用词（替换未覆盖的变体）
        for ai_phrase in phrase_map.keys():
            if ai_phrase in para:
                risk_signals += 1
                risk_reasons.append(f"残留AI痕迹词「{ai_phrase}」")
                break
        # 风险信号 >= 2 时标记为高重复风险段落
        if risk_signals >= 2:
            preview = para[:30].replace("\n", " ") + "..."
            high_risk.append({
                "section_index": idx + 1,
                "preview": preview,
                "risk_reasons": risk_reasons
            })
    return high_risk


# ========== 主函数 ==========
@timeout(30)
def remove_ai_traces(text: str) -> dict:
    """
    学术风格中性化处理主函数。
    执行词频替换、句首禁用词过滤、主动被动态互换，去除 AI 痕迹。

    参数:
        text: 待处理的文本

    返回:
        标准化输出 dict，data 含：
        - normalized_text：处理后的文本
        - replacements_count：总替换次数
        - high_risk_sections：仍存在高重复风险的段落列表
    """
    try:
        if not text or not isinstance(text, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "输入文本为空或非字符串"
            }

        # 读取禁用词映射（文件缺失时降级使用内置映射）
        phrase_map = _load_forbidden_phrases()

        # 提取句首禁用词（值为空字符串的条目，或使用默认列表）
        sentence_start_forbidden = [k for k, v in phrase_map.items() if v == ""]
        if not sentence_start_forbidden:
            sentence_start_forbidden = list(_DEFAULT_SENTENCE_START_FORBIDDEN)

        # 提取主动语态转换模式（含"我们"/"本文"的条目）
        voice_patterns = [(k, v) for k, v in phrase_map.items()
                          if k.startswith("我们") or k.startswith("本文")]
        if not voice_patterns:
            voice_patterns = list(_DEFAULT_VOICE_PATTERNS)

        # 1. 词频替换：AI 化术语 -> 学术中性表达
        normalized, replace_count = _replace_phrases(text, phrase_map)

        # 2. 句首禁用词过滤：移除"首先/其次/综上所述"等开头
        normalized, start_removed = _filter_sentence_start(normalized, sentence_start_forbidden)

        # 3. 主动被动态互换：将"我们提出/本文设计"转为被动或中性表达
        normalized, voice_swapped = _swap_voice(normalized, voice_patterns)

        # 4. 检测高重复风险段落
        high_risk_sections = _detect_high_risk_sections(normalized, phrase_map)

        total_replacements = replace_count + start_removed + voice_swapped

        return {
            "status": "success",
            "data": {
                "normalized_text": normalized,
                "replacements_count": total_replacements,
                "high_risk_sections": high_risk_sections
            },
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"风格中性化处理失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_text = (
        "首先，我们提出了一种基于深度学习的方法。"
        "其次，本文设计了一个高效的模型架构，显著提升了系统性能。"
        "最后，我们发现该方法在多个数据集上大幅提高了准确率。"
        "综上所述，我们充分证明了该方法的有效性。"
    )
    result = remove_ai_traces(sample_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
