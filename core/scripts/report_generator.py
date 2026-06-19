#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开题报告直出器（Report Generator）
读取 core/references/report_template.md 获取模板，填充五大模块，生成开题报告 Markdown。
五大模块：选题依据与研究意义、国内外研究现状、研究内容与关键问题、研究方案与可行性分析、进度安排。
"""

import os
import re
import sys
import json
import time
import threading
from functools import wraps


# ========== 路径常量（使用相对路径定位 references/） ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(SCRIPT_DIR, "..", "references")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "..", "output")

# 导入 style_normalizer（同目录模块，用于去 AI 痕迹处理）
sys.path.insert(0, SCRIPT_DIR)
try:
    import style_normalizer
except ImportError:
    style_normalizer = None


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


def _load_template():
    """读取 report_template.md 获取开题报告模板"""
    template_path = os.path.join(REFERENCES_DIR, "report_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


# ========== 颗粒度配置加载（V4.0 新增） ==========

def _parse_yaml_value(value):
    """解析 YAML 标量值（布尔/整数/字符串）"""
    value = value.strip()
    if value in ('true', 'True'):
        return True
    if value in ('false', 'False'):
        return False
    try:
        return int(value)
    except ValueError:
        # 去除引号
        return value.strip('"\'')


def _parse_granularity_yaml(text):
    """简易 YAML 解析器（针对 output_granularity.yaml 的固定缩进结构）"""
    config = {}
    current_section = None
    current_subsection = None
    for line in text.splitlines():
        # 去除行内注释
        line = line.split('#')[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            # 顶级键（concise/standard/detailed）
            current_section = stripped.rstrip(':')
            config[current_section] = {}
            current_subsection = None
        elif indent == 2:
            # 二级键
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value == '':
                    # 嵌套字典
                    current_subsection = key
                    config[current_section][current_subsection] = {}
                else:
                    current_subsection = None
                    config[current_section][key] = _parse_yaml_value(value)
        elif indent == 4:
            # 三级键
            if ':' in stripped and current_subsection:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                config[current_section][current_subsection][key] = _parse_yaml_value(value)
    return config


def _load_granularity_config(granularity):
    """
    读取 output_granularity.yaml 获取指定颗粒度的配置（V4.0 新增）。
    优先尝试 import yaml，不可用时降级使用内置简易解析器。
    """
    granularity_path = os.path.join(REFERENCES_DIR, "output_granularity.yaml")
    with open(granularity_path, "r", encoding="utf-8") as f:
        yaml_text = f.read()

    # 优先使用 PyYAML（若可用），否则降级为内置解析器
    try:
        import yaml
        all_configs = yaml.safe_load(yaml_text)
    except ImportError:
        all_configs = _parse_granularity_yaml(yaml_text)

    # 返回指定颗粒度的配置，缺失时降级为 standard
    config = all_configs.get(granularity, all_configs.get("standard", {}))
    return config


# ========== 颗粒度渲染辅助函数（V4.0 新增） ==========

# 五大模块标题到 word_thresholds 键的映射
_SECTION_THRESHOLD_MAP = {
    "一、选题依据与研究意义": "selection_basis",
    "二、国内外研究现状": "research_status",
    "三、研究内容与关键问题": "research_content",
    "四、研究方案与可行性分析": "research_scheme",
    "五、进度安排": "schedule",
}


def _count_words(text):
    """统计文本字数（中文字符各计 1，英文单词各计 1，排除 Markdown 语法符号）"""
    # 去除 Markdown 标题标记与表格分隔符
    cleaned = re.sub(r'#{1,6}\s*', '', text)
    cleaned = re.sub(r'\|', ' ', cleaned)
    cleaned = re.sub(r'[-*]\s*', '', cleaned)
    # 统计中文字符数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', cleaned))
    # 统计英文单词数
    english_words = len(re.findall(r'[a-zA-Z]+', cleaned))
    return chinese_chars + english_words


def _adjust_heading_depth(markdown, max_depth):
    """按最大标题层级裁剪：移除深度超过 max_depth 的标题行（保留其下内容）"""
    lines = markdown.split('\n')
    adjusted_lines = []
    for line in lines:
        heading_match = re.match(r'^(#{1,6})\s', line)
        if heading_match:
            depth = len(heading_match.group(1))
            if depth > max_depth:
                # 超过最大层级的标题行移除，内容保留
                continue
        adjusted_lines.append(line)
    return '\n'.join(adjusted_lines)


def _truncate_sections(markdown, word_thresholds):
    """按各模块字数阈值截断内容（仅截断正文，保留标题）"""
    if not word_thresholds:
        return markdown
    lines = markdown.split('\n')
    result_lines = []
    current_section_key = None
    section_content_buffer = []
    section_threshold = None

    def flush_section():
        """将缓冲的章节内容按阈值截断后写入结果"""
        nonlocal section_content_buffer
        if section_content_buffer:
            content = '\n'.join(section_content_buffer)
            if section_threshold and _count_words(content) > section_threshold:
                # 按字符截断至阈值（中文 1 字符 ≈ 1 字）
                truncated = content[:section_threshold]
                result_lines.append(truncated)
            else:
                result_lines.append(content)
            section_content_buffer = []

    for line in lines:
        heading_match = re.match(r'^##\s+(.+)$', line)
        if heading_match:
            # 遇到新的二级标题，刷新上一节缓冲
            flush_section()
            result_lines.append(line)
            section_title = heading_match.group(1).strip()
            # 匹配模块阈值键
            current_section_key = None
            for title_fragment, threshold_key in _SECTION_THRESHOLD_MAP.items():
                if title_fragment in section_title:
                    current_section_key = threshold_key
                    break
            section_threshold = word_thresholds.get(current_section_key) if current_section_key else None
        else:
            section_content_buffer.append(line)
    # 刷新最后一节
    flush_section()
    return '\n'.join(result_lines)


def _adjust_subsections(markdown, include_subsections, proposal):
    """按配置添加或移除可选子章节（技术路线子图/风险矩阵/预期成果）"""
    # 1. 技术路线子图：concise 模式移除技术路线描述
    if not include_subsections.get("technical_route_diagram", True):
        markdown = re.sub(r'\n技术路线：[^\n]*', '', markdown)

    # 2. 风险矩阵：detailed 模式在可行性分析后追加
    if include_subsections.get("risk_matrix", False):
        risk_matrix = (
            "\n\n#### 4.3 风险矩阵\n"
            "| 风险类型 | 风险描述 | 应对策略 |\n"
            "|---------|---------|---------|\n"
            "| 技术风险 | 方法实现难度超出预期 | 预备降级方案，采用成熟技术兜底 |\n"
            "| 数据风险 | 数据获取受限或质量不足 | 多源数据交叉验证，必要时合成补充 |\n"
            "| 进度风险 | 实验周期延误 | 分阶段并行执行，设置里程碑检查点 |\n"
        )
        # 在"## 五、进度安排"之前插入风险矩阵
        markdown = markdown.replace("## 五、进度安排", risk_matrix + "\n## 五、进度安排")

    # 3. 预期成果：detailed 模式在进度安排后追加
    if include_subsections.get("expected_outcome", False):
        degree = proposal.get("degree", "master")
        degree_label = "硕士" if degree == "master" else "博士"
        expected_outcome = (
            "\n\n#### 5.1 预期成果与价值阐述\n"
            f"1. 学术成果：预期形成{degree_label}学位论文 1 篇，"
            f"围绕「{proposal.get('title', '本课题')}」产出 1-2 篇学术论文。\n"
            "2. 方法贡献：所提方法在目标场景下预期较基线方案有所提升，"
            "形成可复用的技术方案或开源工具。\n"
            "3. 应用价值：研究成果具备向实际场景转化的潜力，"
            "可为相关领域的工程实践提供参考。"
        )
        markdown = markdown.rstrip() + expected_outcome + "\n"

    return markdown


def _apply_granularity(markdown, granularity_config, proposal):
    """按颗粒度配置动态渲染报告（V4.0 新增）"""
    # 1. 调整标题深度
    max_depth = granularity_config.get("markdown_depth", 3)
    markdown = _adjust_heading_depth(markdown, max_depth)

    # 2. 按字数阈值截断各模块
    word_thresholds = granularity_config.get("word_thresholds", {})
    markdown = _truncate_sections(markdown, word_thresholds)

    # 3. 按配置添加/移除可选子章节
    include_subsections = granularity_config.get("include_subsections", {})
    markdown = _adjust_subsections(markdown, include_subsections, proposal)

    return markdown


# ========== 模块内容生成辅助函数 ==========

def _generate_key_questions(proposal):
    """基于 differentiation 提炼 1-2 个核心科学问题"""
    differentiation = proposal.get("differentiation", "")
    if not differentiation:
        return "1. 本研究的核心科学问题待进一步明确。"
    # 从差异化描述中提炼科学问题
    return (
        f"1. 基于差异化定位「{differentiation[:30]}」，如何形式化本研究的核心问题？\n"
        f"2. 所提方法在复杂场景下的有效性与鲁棒性如何保证？"
    )


def _generate_research_method(proposal):
    """基于 research_content 生成具体方法步骤"""
    research_content = proposal.get("research_content", "")
    if not research_content:
        return "（待补充具体研究方法与技术路线）"
    return (
        f"{research_content}\n\n"
        f"技术路线：文献调研 → 问题定义 → 方法设计 → 实验验证 → 结果分析 → 论文撰写。"
    )


def _generate_feasibility_analysis(proposal):
    """生成可行性分析（周期可行性、数据/设备可行性论证）"""
    degree = proposal.get("degree", "master")
    max_months = 12 if degree == "master" else 24
    return (
        f"1. 周期可行性：本研究计划在 {max_months} 个月内完成，"
        f"符合{degree}学制要求，各阶段时间分配合理。\n"
        f"2. 数据可行性：将使用公开数据集或导师课题组既有数据资源，确保数据可得。\n"
        f"3. 设备可行性：依托导师课题组计算资源，必要时采用轻量化方案降低算力需求。\n"
        f"4. 技术可行性：所提方法基于成熟技术栈，具备实现基础。"
    )


def _generate_schedule(proposal):
    """基于 academic_calendar 约束生成甘特图节点列表"""
    degree = proposal.get("degree", "master")
    total_months = 12 if degree == "master" else 24
    # 划分阶段
    phase1 = max(1, total_months // 6)       # 文献调研与开题
    phase2 = max(1, total_months // 3)       # 方法设计与实验
    phase3 = max(1, total_months // 3)       # 结果分析与论文撰写
    phase4 = total_months - phase1 - phase2 - phase3  # 答辩准备

    schedule = (
        f"| 阶段 | 时间（月） | 任务 |\n"
        f"|------|-----------|------|\n"
        f"| 第一阶段 | 第1-{phase1}月 | 文献调研、开题报告撰写 |\n"
        f"| 第二阶段 | 第{phase1 + 1}-{phase1 + phase2}月 | 方法设计、数据准备、初步实验 |\n"
        f"| 第三阶段 | 第{phase1 + phase2 + 1}-{phase1 + phase2 + phase3}月 | 完整实验、结果分析 |\n"
        f"| 第四阶段 | 第{phase1 + phase2 + phase3 + 1}-{total_months}月 | 论文撰写、修改、答辩准备 |"
    )
    return schedule


def _fill_template(template, proposal):
    """填充模板占位符"""
    # 生成衍生字段
    key_questions = _generate_key_questions(proposal)
    research_method = _generate_research_method(proposal)
    feasibility_analysis = _generate_feasibility_analysis(proposal)
    schedule = _generate_schedule(proposal)

    # 占位符替换映射
    replacements = {
        "{{title}}": proposal.get("title", "（未命名论题）"),
        "{{problem_awareness}}": proposal.get("problem_awareness", "（待补充）"),
        "{{research_significance}}": proposal.get("research_significance", "（待补充）"),
        "{{literature_review_outline}}": proposal.get("literature_review_outline", "（待补充）"),
        "{{research_content}}": proposal.get("research_content", "（待补充）"),
        "{{key_questions}}": key_questions,
        "{{research_method}}": research_method,
        "{{feasibility_analysis}}": feasibility_analysis,
        "{{schedule}}": schedule,
    }

    filled = template
    for placeholder, value in replacements.items():
        filled = filled.replace(placeholder, str(value))

    return filled


# ========== 主函数 ==========

@timeout(30)
def generate_report(proposal: dict, granularity: str = "standard", style_neutral: bool = True) -> dict:
    """
    开题报告直出器主函数。

    参数:
        proposal: 论题提案 dict，应含 title、problem_awareness、research_significance、
                  differentiation、research_content、literature_review_outline 等字段
                  可选含 degree（master/phd）
        granularity: 输出颗粒度（concise/standard/detailed，默认 standard）。
                     读取 output_granularity.yaml 按配置动态渲染模板深度（V4.0 新增）。
        style_neutral: 是否执行学术风格中性化去 AI 痕迹处理（默认 True，V4.0 新增）。
                       为 True 时调用 style_normalizer.remove_ai_traces() 处理输出。

    返回:
        标准化输出 dict，data 含：
        - report_markdown：报告内容
        - report_path：文件路径
        - high_plagiarism_risk_sections：局部高重复风险段落列表（style_neutral=True 时返回）
    """
    try:
        if not proposal or not isinstance(proposal, dict):
            return {
                "status": "error",
                "data": None,
                "error_message": "输入提案为空或非字典"
            }

        # 读取模板
        template = _load_template()

        # 填充模板
        report_markdown = _fill_template(template, proposal)

        # 按颗粒度配置动态渲染（V4.0 新增）
        granularity_config = _load_granularity_config(granularity)
        report_markdown = _apply_granularity(report_markdown, granularity_config, proposal)

        # 学术风格中性化处理：去 AI 痕迹（V4.0 新增）
        high_plagiarism_risk_sections = []
        if style_neutral:
            if style_normalizer is not None:
                normalize_result = style_normalizer.remove_ai_traces(report_markdown)
                if normalize_result.get("status") == "success":
                    report_markdown = normalize_result["data"]["normalized_text"]
                    high_plagiarism_risk_sections = normalize_result["data"].get("high_risk_sections", [])
            # style_normalizer 不可用时跳过去 AI 处理，保持原始输出

        # 生成文件名（带时间戳）
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"draft_{timestamp}.md"
        report_path = os.path.join(OUTPUT_DIR, filename)

        # 沙盒校验后写入文件
        validated_path = validate_write_path(report_path)

        # 确保 output/ 目录存在
        os.makedirs(os.path.dirname(validated_path), exist_ok=True)

        with open(validated_path, "w", encoding="utf-8") as f:
            f.write(report_markdown)

        return {
            "status": "success",
            "data": {
                "report_markdown": report_markdown,
                "report_path": report_path,
                "high_plagiarism_risk_sections": high_plagiarism_risk_sections
            },
            "error_message": None
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"模板文件缺失：{str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"沙盒权限拒绝：{str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"报告生成失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    sample_proposal = {
        "title": "医疗大模型的科室问询微调",
        "degree": "master",
        "problem_awareness": "通用大模型在医疗问询场景精度不足，缺乏科室特异性。",
        "research_significance": "通过科室级微调提升医疗大模型问询精度，兼具理论与实际价值。",
        "differentiation": "聚焦单一科室微调，区别于通用大模型的全场景覆盖。",
        "research_content": "1. 调研医疗大模型现状；2. 设计科室微调方案；3. 实验验证。",
        "literature_review_outline": "梳理医疗大模型与微调技术研究，规划文献不少于30篇。"
    }
    # 测试向后兼容（默认 standard + style_neutral=True）
    print("===== 标准版测试（默认参数，向后兼容）=====")
    result = generate_report(sample_proposal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # 测试精简版
    print("\n===== 精简版测试（granularity=concise）=====")
    result_concise = generate_report(sample_proposal, granularity="concise")
    print(json.dumps(result_concise, ensure_ascii=False, indent=2))
    # 测试详实版
    print("\n===== 详实版测试（granularity=detailed）=====")
    result_detailed = generate_report(sample_proposal, granularity="detailed")
    print(json.dumps(result_detailed, ensure_ascii=False, indent=2))
