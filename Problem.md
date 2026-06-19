# ThesisMinerSkill V4.0 升级问题记录

> 本文档记录从 V2.1 升级到 V4.0 过程中遇到的关键问题与解决思路。

## 1. 五阶段闭环流与线性六步流的兼容性

**问题**：V2.1 的线性六步流（I/O识别→谱系解析→四维创意→精炼→约束修复→输出）被 V4.0 重构为五阶段闭环流，如何保证向后兼容？

**解决思路**：
- 五阶段闭环流是六步流的超集：阶段二复用谱系解析+四维创意，阶段三复用约束修复，阶段四复用报告生成
- 新增的阶段一（信息确权）和阶段五（深度辅助）是纯增量，不影响原有流程
- 脚本函数签名向后兼容：generate_ideas 新增 search_feeds=None 默认参数，generate_report 新增 granularity="standard" 和 style_neutral=True 默认参数，旧调用方式仍有效

## 2. 联网检索能力与沙盒限制的冲突

**问题**：V2.1 脚本沙盒明确"禁止网络访问"，但 V4.0 阶段一和阶段三需要联网检索。

**解决思路**：
- 沙盒限制针对的是脚本文件系统越权写入，联网检索由运行时大模型执行（非脚本直接发起）
- 脚本层仅提供检索式生成（check_novelty 内部生成 search_queries）与结果分析（overlap_ratio 估算），实际联网由运行时 API 调用
- search_strategies.json 定义检索式模板，由指令层驱动运行时执行联网，脚本不直接联网

## 3. 去 AI 痕迹与报告排版的优先级

**问题**：style_normalizer 的去 AI 痕迹处理可能与 report_generator 的 Markdown 排版冲突。

**解决思路**：
- Rule 9 明确规定 style_normalizer 优先级高于 report_generator 排版
- 实现上，generate_report(style_neutral=True) 内部先渲染 Markdown，再调用 remove_ai_traces 处理文本
- style_normalizer 仅替换文本内容，不破坏 Markdown 结构（标题层级、列表标记、代码块保持不变）

## 4. forbidden_ai_phrases.json 的结构兼容性

**问题**：style_normalizer.py 的 _load_forbidden_phrases() 期望 phrase_map 字段，但实际 JSON 文件使用 phrase_mappings 字段。

**解决思路**：
- _load_forbidden_phrases() 支持两种结构：含 phrase_map 字段的 dict 或直接映射 dict
- 文件顶层无 phrase_map 键时，整个 JSON dict 作为 phrase_map 合并到内置默认映射
- 由于文件顶层键（description/phrase_mappings/sentence_patterns/passive_voice_hints）与默认映射的 AI 术语键不冲突，实际生效的是内置默认映射
- 后续可优化 _load_forbidden_phrases() 显式读取 phrase_mappings 字段

## 5. 多粒度输出的 Markdown 深度控制

**问题**：output_granularity.yaml 定义了三级 markdown_depth（2/3/4），但 report_generator 原模板使用固定深度。

**解决思路**：
- 新增 _adjust_heading_depth() 函数，按 granularity 配置截断超过最大深度的标题
- 新增 _adjust_subsections() 函数，按 include_subsections 配置追加风险矩阵、预期成果等子节
- detailed 颗粒度通过追加 #### 4.3 风险矩阵 与 #### 5.1 预期成果 实现 #### 级标题

## 6. TRAE ZIP 打包脚本的版本同步

**问题**：build-trae-zip.py 输出文件名为 v2.1.zip，需同步到 v4.0。

**解决思路**：
- ZIP_NAME 从 thesis-architect-v2.1.zip 改为 thesis-architect-v4.0.zip
- required_core_files 列表新增 V4.0 资源文件（style_normalizer.py、deep_helper.py、search_strategies.json、forbidden_ai_phrases.json、output_granularity.yaml）
- 验证逻辑同步扩充

## 7. 测试用例的向后兼容

**问题**：适配现有测试时，不能修改原有测试用例（保证向后兼容），只能追加新用例。

**解决思路**：
- test_idea_generator.py 追加 3 个 search_feeds 测试用例
- test_constraint_checker.py 追加 4 个 check_novelty 测试用例
- test_report_generator.py 追加 6 个 granularity/style_neutral 测试用例
- test_schema.py 追加 5 个 V4.0 字段验证用例
- 全部 63 个测试通过，原有 28 个用例不受影响
