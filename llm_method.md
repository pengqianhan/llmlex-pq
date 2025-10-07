# 基于 Vision LLM 的混合自动机识别方法（LLM 方法）

## 目标与总体思路
- 目标：绕过传统 trace segmentation/cluster/guard/reset 的全链条，用视觉-语言模型（VLM）先产出混合自动机的结构骨架（模式、方程形式、转移、重置），再用数值拟合确定参数，形成“结构由 LLM，参数由拟合”的闭环。
- 流程：图像与上下文 → VLM 产 JSON → 参数提取与拟合 → Dainarx 仿真对比 → 图像与指标回馈给 VLM → 岛屿模型进化搜索。

## 数据与可视化
- 输入数据：时间序列 `x(t)`，维度建议 ≤3–4，采样间隔 `dt`。
- 可视化要素：
  - 时间域曲线（各状态叠加）与相图（如 `x`–`x'`）。
  - 关键点标注（极值、零交点、疑似切换点）。
  - 上下文文字：变量名、采样率、量纲、是否有外部输入等。
- 本仓库工具：`llmlex/images.py` 生成 base64 图像，便于送入 VLM。

## VLM 生成骨架 JSON（结构）
- 约束输出为固定 JSON/DSL：`automaton.var/mode/edge/input`（示例见 `LAMBDA_JSON_GUIDE.md`、`example_lambda_to_json.py`）。
- 建议限制函数族（线性、多项式、abs、饱和、阈值等），减少幻觉与不合法表达式。
- 产出多候选 JSON，做语法与可仿真性校验后进入下一步。

## 参数提取与拟合
- 将 `mode.eq`、`edge.condition/reset` 中的数值字面量提取为占位符 `{p_k}`，组成参数向量 `p`（脚本已实现自动模板化）。
- 目标函数：以鲁棒指标为主，默认 `nchi_mean + 0.05*rmse_mean`，其中 `nchi_mean` 为归一化卡方（参见 `llmlex/fit.py`）。
- 优化器：默认 Nelder–Mead（无需梯度，稳定易用），必要时可替换为 `differential_evolution` 等全局方法。

## 仿真、绘图与指标
- 仿真：`Dainarx_code/src/HybridAutomata.py:46` 的 `HybridAutomata.from_json` 加载 JSON，Runge–Kutta 步进。
- 指标：按变量计算 `RMSE` 与 `n-chi^2`，并给出均值。
- 可视化：叠加真值与预测曲线，保存对比图；这些图与指标用于反馈给 VLM 调整结构。

## 岛屿模型进化搜索（Island Model）
- 多岛并行：每岛保留精英个体，其余由变异产生：
  - 结构变异（可选）：将“对比图 + 指标 + 当前 JSON”喂给 VLM，请其在既定 DSL 下小步调整（增删项、微调守卫/重置形式）。
  - 数值变异（本地）：在模板参数上加噪后重拟合。
- 迁移：每隔若干代按环形迁移各岛最优个体，提升多样性与收敛速度。

## 快速上手（脚本）
- 脚本：`island_ha_vlm.py`。
- Duffing 实测数据：
  ```bash
  # 例如：2000 步，抽样 stride=10，加速演示
  python island_ha_vlm.py \
      --data data_duffing/test_data0.npz \
      --steps 2000 --stride 10 \
      --islands 2 --pop 2 --gens 2
  ```
- 启用 VLM 结构变异（需 OpenRouter）：
  ```bash
  export OPENROUTER_API_KEY=...  # 可选：OPENROUTER_BASE_URL
  python island_ha_vlm.py --use-vlm --data data_duffing/test_data0.npz
  ```
- 核心 CLI 参数：
  - `--data`: NPZ 文件（需包含 `state` 与 `input`）。
  - `--dt`: 可覆盖默认离散步长（默认 0.001）。
  - `--steps` / `--stride`: 控制截取长度与下采样，平衡精度与运行时间。
  - `--islands` / `--pop` / `--gens`: 岛屿数量、种群规模、迭代代数。

## 注意事项与建议
- 约束 VLM：严格 JSON 模式与函数白名单，多候选+校验，避免不合法结构。
- 守卫/重置：建议初期用简单形式（阈值、仿射重置），由拟合与反馈逐步复杂化。
- 正则化：在目标中加入切换惩罚/最小驻留时间可提升稳定性（可扩展到 EM/维特比式软分配）。
- 复杂任务：增大 `--gens/--islands`，或引入更强的全局/分层搜索；必要时结合传统弱监督分割做热启动。
