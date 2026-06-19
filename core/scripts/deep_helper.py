#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度辅助三件套（Deep Helper）
提供文献精读工作簿生成、实验/应用预研映射、答辩模拟（逻辑压力测试）三大功能。
基于规则模板与文本分析生成结构化工单，不依赖外部 NLP 库，纯 Python 实现。
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


# ========== 文本处理辅助函数 ==========

def _split_sentences(text):
    """将文本切分为句子（按中文标点与换行）"""
    sentences = re.split(r'[。；！？\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def _extract_key_phrases(text, max_count=5):
    """
    从文本中提取关键名词短语（简化实现：取2-8字的中文词组）。
    用于为生成的工单提供主题锚点。
    """
    # 提取2-8字的连续中文词组
    phrases = re.findall(r'[\u4e00-\u9fa5]{2,8}', text)
    # 去重并保留顺序
    seen = set()
    unique = []
    for p in phrases:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique[:max_count]


# ========== 文献精读工作簿生成 ==========

def _generate_reading_workbook(research_status, index):
    """
    生成单篇文献精读框架。
    包含三明治拆解（动机-方法-局限）、GAP 分析、可借鉴图表。
    """
    # 从研究现状中提取关键短语作为文献主题锚点
    key_phrases = _extract_key_phrases(research_status, max_count=10)
    if key_phrases:
        topic = key_phrases[index % len(key_phrases)]
    else:
        topic = f"研究方向{index + 1}"

    return {
        "literature_index": index + 1,
        "suggested_topic": topic,
        "sandwich_analysis": {
            # 三明治拆解：动机-方法-局限
            "motivation": (
                f"围绕「{topic}」，该文献拟解决的核心问题是"
                f"现有方法在特定场景下的性能瓶颈或理论空白。"
            ),
            "method": (
                f"采用与「{topic}」相关的技术路线，"
                f"提出改进方案以提升效果或填补空白。"
            ),
            "limitation": (
                f"该方法在「{topic}」的泛化性、计算效率或数据依赖方面"
                f"可能存在不足，构成可延伸的研究空间。"
            )
        },
        "gap_analysis": {
            # GAP 分析：与自身课题关键问题的映射
            "self_key_problem": f"本课题关键问题与「{topic}」的关联点",
            "mapping": (
                f"该文献的方法可为本课题的「{topic}」部分提供借鉴，"
                f"但其局限性正是本课题的切入点。"
            ),
            "differentiation": (
                f"本课题在「{topic}」上拟通过引入新变量或迁移至新场景，"
                f"突破该文献的局限。"
            )
        },
        "borrowable_charts": [
            # 可借鉴图表
            f"「{topic}」技术路线对比图（可借鉴框架，替换为本课题数据）",
            f"「{topic}」实验结果表格（可借鉴评价指标设计）"
        ]
    }


@timeout(30)
def literature_deep_reader(research_status: str, count: int = 3) -> dict:
    """
    文献精读工作簿生成主函数。
    针对研究现状文本，生成 count 篇标志性文献的精读框架。

    参数:
        research_status: 研究现状文本
        count: 生成精读框架的文献数量，默认3

    返回:
        标准化输出 dict，data 含 reading_workbooks 数组
    """
    try:
        if not research_status or not isinstance(research_status, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "研究现状文本为空或非字符串"
            }

        if not isinstance(count, int) or count <= 0:
            return {
                "status": "error",
                "data": None,
                "error_message": "count 必须为正整数"
            }

        # 限制最大数量避免过度生成
        count = min(count, 10)

        workbooks = []
        for i in range(count):
            workbook = _generate_reading_workbook(research_status, i)
            workbooks.append(workbook)

        return {
            "status": "success",
            "data": {"reading_workbooks": workbooks},
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"文献精读工作簿生成失败：{str(e)}"
        }


# ========== 实验/应用预研映射 ==========

def _design_stem_plan(research_content):
    """
    理工/计算机类：输出 MVE 清单（最小可行性实验）。
    含库版本、核心算法伪代码、基线对比计划。
    """
    key_phrases = _extract_key_phrases(research_content, max_count=5)
    core_topic = key_phrases[0] if key_phrases else "核心算法"
    # 生成函数名（去除空格，非中文部分保留）
    func_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_]', '_', core_topic)[:20]

    return {
        "plan_type": "MVE清单（最小可行性实验）",
        "library_versions": [
            "Python 3.10+",
            "PyTorch 2.1+ / TensorFlow 2.15+",
            "NumPy 1.24+ / Pandas 2.0+",
            "Scikit-learn 1.3+（基线方法）",
            f"领域专用库：根据「{core_topic}」需求选型"
        ],
        "core_algorithm_pseudocode": (
            f"# 「{core_topic}」核心算法伪代码\n"
            f"function {func_name}_main(data, config):\n"
            f"    # 1. 数据预处理\n"
            f"    processed = preprocess(data)\n"
            f"    # 2. 模型构建\n"
            f"    model = build_model(config)\n"
            f"    # 3. 训练与优化\n"
            f"    model.train(processed)\n"
            f"    # 4. 评估\n"
            f"    metrics = evaluate(model, test_set)\n"
            f"    return metrics"
        ),
        "baseline_comparison_plan": [
            f"基线1：传统方法（与「{core_topic}」相关的经典算法）",
            f"基线2：现有SOTA方法（近2年顶会/顶刊代表方案）",
            f"基线3：消融实验（去除本方法关键组件以验证贡献）",
            "评价指标：准确率/精确率/召回率/F1/运行效率（按领域选取）"
        ]
    }


def _design_math_plan(research_content):
    """
    数学/理论类：输出证明路径图谱。
    含前置引理梳理、核心引理构造思路、数值算例验证方案。
    """
    key_phrases = _extract_key_phrases(research_content, max_count=5)
    core_topic = key_phrases[0] if key_phrases else "核心定理"

    return {
        "plan_type": "证明路径图谱",
        "preliminary_lemmas": [
            f"引理1：与「{core_topic}」相关的基础性质（需引用经典文献）",
            f"引理2：构建「{core_topic}」所需的中间结论",
            f"引理3：连接引理1与核心定理的桥梁性命题"
        ],
        "core_lemma_construction": (
            f"针对「{core_topic}」，核心引理构造思路如下：\n"
            f"1. 从定义出发，明确「{core_topic}」的形式化表述；\n"
            f"2. 识别关键不等式或恒等式，建立上下界估计；\n"
            f"3. 通过归纳法或反证法完成核心引理证明；\n"
            f"4. 将核心引理推广至主定理。"
        ),
        "numerical_verification": [
            f"算例1：构造「{core_topic}」的简化情形，验证理论结论",
            f"算例2：选取标准测试集，对比理论与数值结果",
            "算例3：边界情形检验（极端参数下的稳定性）",
            "工具建议：Mathematica / MATLAB / Python(SymPy+NumPy)"
        ]
    }


def _design_social_plan(research_content):
    """
    社科/商科类：输出调研方案设计。
    含问卷量表映射、抽样策略、数据分析模型预设。
    """
    key_phrases = _extract_key_phrases(research_content, max_count=5)
    core_topic = key_phrases[0] if key_phrases else "核心构念"

    return {
        "plan_type": "调研方案设计",
        "questionnaire_scale_mapping": [
            f"量表1：「{core_topic}」测量量表（建议参考成熟量表改编，Likert 5/7点）",
            f"量表2：自变量测量（与「{core_topic}」相关的前因变量）",
            f"量表3：因变量测量（与「{core_topic}」相关的结果变量）",
            "量表4：控制变量（人口统计学特征等）",
            "信效度检验：Cronbach's α ≥ 0.7，KMO ≥ 0.6"
        ],
        "sampling_strategy": (
            f"针对「{core_topic}」研究问题，建议抽样策略：\n"
            f"1. 目标总体定义：明确研究对象的边界；\n"
            f"2. 样本量估算：依据效应量、显著性水平、统计功效计算（G*Power）；\n"
            f"3. 抽样方法：分层随机抽样 / 方便抽样（视研究条件）；\n"
            f"4. 样本代表性：控制关键人口学变量的分布。"
        ),
        "data_analysis_models": [
            f"描述性统计：「{core_topic}」相关变量的分布与相关性",
            "信效度分析：Cronbach's α、验证性因子分析（CFA）",
            "假设检验：结构方程模型（SEM）/ 回归分析 / 方差分析",
            "稳健性检验：替换变量、子样本检验、内生性处理"
        ]
    }


@timeout(30)
def experiment_designer(research_content: str, discipline: str) -> dict:
    """
    实验/应用预研映射主函数。
    根据学科类型输出对应的预研方案。

    参数:
        research_content: 研究内容文本
        discipline: 学科类型（stem/math/social）
            - stem：理工/计算机，输出 MVE 清单
            - math：数学/理论，输出证明路径图谱
            - social：社科/商科，输出调研方案设计

    返回:
        标准化输出 dict，data 含 discipline 与 design_plan
    """
    try:
        if not research_content or not isinstance(research_content, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "研究内容文本为空或非字符串"
            }

        discipline = discipline.lower().strip()
        valid_disciplines = {"stem", "math", "social"}
        if discipline not in valid_disciplines:
            return {
                "status": "error",
                "data": None,
                "error_message": f"未知学科类型：{discipline}，支持：{sorted(valid_disciplines)}"
            }

        # 根据学科类型选择设计方案
        if discipline == "stem":
            design_plan = _design_stem_plan(research_content)
        elif discipline == "math":
            design_plan = _design_math_plan(research_content)
        else:  # social
            design_plan = _design_social_plan(research_content)

        return {
            "status": "success",
            "data": {
                "discipline": discipline,
                "design_plan": design_plan
            },
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"实验预研映射失败：{str(e)}"
        }


# ========== 答辩模拟（逻辑压力测试） ==========

# 苏格拉底式诘问模板（按轮次递进，聚焦点逐步深入）
_DEFENSE_QUESTION_TEMPLATES = [
    {
        "round": 1,
        "focus": "问题定义与动机审查",
        "questions": [
            "您所定义的核心问题是否真正构成'问题'？请用一句话说清'如果不解决会怎样'。",
            "该问题的研究价值是理论贡献还是应用价值？如果是理论贡献，与现有理论的边界在哪？",
            "您提到的研究现状中，是否已有工作部分解决了该问题？您与他们的本质差异是什么？"
        ]
    },
    {
        "round": 2,
        "focus": "方法严谨性与可行性审查",
        "questions": [
            "您所提方法的核心假设是什么？这些假设在实际场景中是否成立？",
            "方法的创新点是否可证伪？即如果实验失败，能否明确归因？",
            "实验设计中，如何排除混淆变量？对照组设置是否充分？",
            "样本量/数据规模是否足以支撑结论的统计显著性？"
        ]
    },
    {
        "round": 3,
        "focus": "结论泛化与贡献边界审查",
        "questions": [
            "您的结论能否推广至其他场景？泛化的边界条件是什么？",
            "如果审稿人要求增加一组对比实验，您会如何应对？",
            "本研究最大的局限是什么？如果重做，您会如何改进？",
            "该研究对学科发展的长期价值是什么？5年后是否仍有意义？"
        ]
    }
]

# 弱点检测模式（正则 + 描述）
_WEAKNESS_PATTERNS = [
    (r'可能|或许|大概|似乎', "表述模糊：使用了不确定词汇，缺乏量化支撑"),
    (r'所有|全部|完全|彻底', "过度泛化：使用了绝对化表述，缺乏边界限定"),
    (r'明显|显著|极大|大幅', "夸大效果：未提供统计检验即下强度判断"),
    (r'等等|诸如此类|以及其他', "列举不充分：使用省略词替代完整论证"),
    (r'众所周知|不言而喻', "论证跳跃：以常识替代严谨推导"),
]


def _extract_weakness_points(key_problems):
    """
    从关键问题文本中检测潜在弱点。
    基于模糊词、绝对化表述、夸大效果等模式匹配。
    """
    weaknesses = []
    for pattern, description in _WEAKNESS_PATTERNS:
        matches = re.findall(pattern, key_problems)
        if matches:
            weaknesses.append({
                "type": description,
                "evidence": matches[:3],  # 最多展示3个证据
                "suggestion": "建议在答辩前补充量化数据或限定表述边界"
            })
    return weaknesses


def _simulate_defense_round(round_config, key_problems):
    """模拟单轮答辩，生成诘问清单"""
    return {
        "round": round_config["round"],
        "focus": round_config["focus"],
        "questions": round_config["questions"],
        "tip": "请逐条准备口头回答，每题回答不超过2分钟，避免使用模糊词汇。"
    }


@timeout(30)
def thesis_defense_simulator(key_problems: str, rounds: int = 3) -> dict:
    """
    答辩模拟（逻辑压力测试）主函数。
    AI 扮演严苛盲审专家，针对关键问题发起苏格拉底式诘问。

    参数:
        key_problems: 关键问题文本
        rounds: 模拟轮数，默认3

    返回:
        标准化输出 dict，data 含 defense_rounds 与 weakness_points
    """
    try:
        if not key_problems or not isinstance(key_problems, str):
            return {
                "status": "error",
                "data": None,
                "error_message": "关键问题文本为空或非字符串"
            }

        if not isinstance(rounds, int) or rounds <= 0:
            return {
                "status": "error",
                "data": None,
                "error_message": "rounds 必须为正整数"
            }

        # 限制最大轮数（不超过预设模板数量）
        rounds = min(rounds, len(_DEFENSE_QUESTION_TEMPLATES))

        # 模拟答辩轮次
        defense_rounds = []
        for i in range(rounds):
            round_config = _DEFENSE_QUESTION_TEMPLATES[i]
            defense_rounds.append(_simulate_defense_round(round_config, key_problems))

        # 检测关键问题文本中的弱点
        weakness_points = _extract_weakness_points(key_problems)

        return {
            "status": "success",
            "data": {
                "defense_rounds": defense_rounds,
                "weakness_points": weakness_points
            },
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error_message": f"答辩模拟失败：{str(e)}"
        }


# ========== 命令行入口（自测） ==========
if __name__ == "__main__":
    print("===== 文献精读工作簿生成 =====")
    sample_status = (
        "近年来，大语言模型在医疗问询领域取得显著进展。"
        "LoRA微调方法降低了训练成本，但存在科室泛化能力不足的问题。"
        "提示工程方法无需训练，但效果受限于提示设计。"
    )
    result1 = literature_deep_reader(sample_status, count=3)
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    print("\n===== 实验预研映射（stem） =====")
    sample_content = "本研究设计基于深度学习的医疗问询微调方案，对比基线模型验证效果。"
    result2 = experiment_designer(sample_content, "stem")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

    print("\n===== 答辩模拟 =====")
    sample_problems = (
        "本方法可能显著提升医疗问询精度，"
        "所有测试场景下均表现出明显优势，"
        "众所周知深度学习需要大量数据。"
    )
    result3 = thesis_defense_simulator(sample_problems, rounds=3)
    print(json.dumps(result3, ensure_ascii=False, indent=2))
