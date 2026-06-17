"""
乳液制备配比计算器 — Emulsion Calculator
===========================================
核心逻辑：已知目标乳液总体积、水油比、目标乳化剂浓度、储备液浓度，
计算水相体积、储备液体积、纯油体积。

核心公式：
  V_water_total = V_total × R_water / (R_water + R_oil)
  V_oil_total   = V_total × R_oil   / (R_water + R_oil)
  V_stock       = V_total × C_target / C_stock
  V_pure_oil    = V_oil_total - V_stock

边界条件：
  - 所有输入 > 0
  - V_pure_oil >= 0，否则报错"储备液浓度过低"
"""

import streamlit as st

# ============================================================
#  核心计算模块
#  后续如需在水相中加入溶质（如乙酸），只需扩展此函数
# ============================================================

def calculate_emulsion(
    v_total: float,
    r_water: float,
    r_oil: float,
    c_target: float,
    c_stock: float,
) -> dict:
    """
    计算乳液各组分的精确用量。

    Parameters
    ----------
    v_total  : 目标乳液总体积 (mL)
    r_water  : 水相比例（无量纲）
    r_oil    : 油相比例（无量纲）
    c_target : 目标乳化剂浓度 — 质量/体积百分比 (%), 例如 0.1 表示 0.1%
    c_stock  : 储备液乳化剂浓度 — 质量/体积百分比 (%), 例如 1.0 表示 1%

    Returns
    -------
    dict : {
        v_water_total, v_oil_total, v_stock, v_pure_oil
    }
    """

    # 1. 总体积按水油比拆分
    ratio_sum = r_water + r_oil
    v_water_total = v_total * r_water / ratio_sum
    v_oil_total   = v_total * r_oil   / ratio_sum

    # 2. 乳化剂溶质守恒：C_target * V_total = C_stock * V_stock
    #    此处百分比需转换为小数（/ 100），分子分母的 /100 抵消
    v_stock = v_total * c_target / c_stock

    # 3. 纯油 = 油相总体积 − 储备液体积
    v_pure_oil = v_oil_total - v_stock

    return {
        "v_water_total": round(v_water_total, 4),
        "v_oil_total":   round(v_oil_total, 4),
        "v_stock":       round(v_stock, 4),
        "v_pure_oil":    round(v_pure_oil, 4),
        "ratio_sum":     ratio_sum,
    }


def validate_inputs(v_total, r_water, r_oil, c_target, c_stock) -> str | None:
    """边界检查。返回 None=通过，否则返回错误信息。"""
    if v_total <= 0:
        return "目标乳液总体积必须大于 0"
    if r_water <= 0:
        return "水相比例必须大于 0"
    if r_oil <= 0:
        return "油相比例必须大于 0"
    if c_target <= 0:
        return "目标乳化剂浓度必须大于 0"
    if c_stock <= 0:
        return "储备液乳化剂浓度必须大于 0"
    return None


# ============================================================
#  Streamlit UI
# ============================================================

st.set_page_config(
    page_title="乳液配比计算器",
    page_icon="🧪",
    layout="centered",
)

st.title("🧪 乳液制备配比计算器")
st.caption("Emulsion Preparation Calculator — 水/油/乳化剂一体计算")

# ------------------- 输入区 -------------------
st.markdown("### 📐 输入参数")

col1, col2 = st.columns(2)

with col1:
    v_total = st.number_input(
        "目标乳液总体积 (mL)",
        min_value=0.01,
        value=100.0,
        step=10.0,
        format="%.2f",
        help="你最终要配制的乳液总量",
    )

    r_water = st.number_input(
        "水相比例（水）",
        min_value=0.01,
        value=7.0,
        step=0.5,
        format="%.1f",
        help="R_water，例如水:油 = 7:3 则填 7",
    )

with col2:
    c_target = st.number_input(
        "目标乳化剂浓度 (%)",
        min_value=0.0001,
        value=0.1,
        step=0.05,
        format="%.4f",
        help="例如 PGPR 目标浓度 0.1%，填 0.1",
    )

    c_stock = st.number_input(
        "储备液乳化剂浓度 (%)",
        min_value=0.0001,
        value=1.0,
        step=0.1,
        format="%.2f",
        help="例如 1% PGPR 椰子油储备液，填 1",
    )

r_oil = st.number_input(
    "油相比例（油）",
    min_value=0.01,
    value=3.0,
    step=0.5,
    format="%.1f",
    help="R_oil，例如水:油 = 7:3 则填 3",
)

current_ratio = f"水:油 = {r_water:.1f} : {r_oil:.1f}"
st.caption(f"当前水油比：**{current_ratio}**  ")

# ------------------- 计算按钮 -------------------
if st.button("⚡ 开始计算", type="primary", use_container_width=True):

    # 输入校验
    error = validate_inputs(v_total, r_water, r_oil, c_target, c_stock)
    if error:
        st.error(error)
    else:
        result = calculate_emulsion(v_total, r_water, r_oil, c_target, c_stock)

        # 储备液浓度过低检查
        if result["v_pure_oil"] < 0:
            st.error(
                "❌ 错误：储备液浓度过低，无法调制该目标浓度的乳液！\n\n"
                f"油相总体积仅 {result['v_oil_total']:.4f} mL，"
                f"但需要 {result['v_stock']:.4f} mL 储备液。\n"
                f"请提高储备液浓度（当前 {c_stock}%），或降低目标浓度（当前 {c_target}%）。"
            )
        else:
            # ------------------- 结果展示 -------------------
            st.markdown("---")
            st.markdown("### 📊 计算结果")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric(
                    label=f"💧 水相（如乙酸溶液）",
                    value=f"{result['v_water_total']:.2f} mL",
                )

            with col_b:
                st.metric(
                    label=f"🧴 储备液（{c_stock}% PGPR 椰子油）",
                    value=f"{result['v_stock']:.2f} mL",
                )

            with col_c:
                st.metric(
                    label="🥥 纯油（纯椰子油）",
                    value=f"{result['v_pure_oil']:.2f} mL",
                )

            # 汇总展开
            with st.expander("📋 详细计算过程", expanded=False):
                st.markdown(f"""
| 步骤 | 公式 | 数值 |
|------|------|------|
| 水相总体积 | V_total × R_water / (R_water + R_oil) | **{v_total} × {r_water} / {r_water + r_oil} = {result['v_water_total']:.4f} mL** |
| 油相总体积 | V_total × R_oil / (R_water + R_oil) | **{v_total} × {r_oil} / {r_water + r_oil} = {result['v_oil_total']:.4f} mL** |
| 储备液体积 | V_total × C_target / C_stock | **{v_total} × {c_target}% / {c_stock}% = {result['v_stock']:.4f} mL** |
| 纯油体积   | V_oil_total − V_stock | **{result['v_oil_total']:.4f} − {result['v_stock']:.4f} = {result['v_pure_oil']:.4f} mL** |
""")

                # 验证
                check_water = f"{result['v_water_total']:.4f}"
                check_oil = f"{result['v_stock']:.4f} + {result['v_pure_oil']:.4f} = {result['v_stock'] + result['v_pure_oil']:.4f}"
                check_total = f"{result['v_water_total']:.4f} + {result['v_stock'] + result['v_pure_oil']:.4f} = {result['v_water_total'] + result['v_stock'] + result['v_pure_oil']:.4f}"

                st.success(
                    f"✅ 验算通过："
                    f"水相 {check_water} mL + "
                    f"油相 ({check_oil}) mL = "
                    f"总计 {check_total} mL"
                )

            # 配比摘要
            st.info(
                f"📝 **配比摘要**：取 **{result['v_water_total']:.2f} mL** 水相，"
                f"加入 **{result['v_stock']:.2f} mL** 储备液（{c_stock}% PGPR），"
                f"再加入 **{result['v_pure_oil']:.2f} mL** 纯油，"
                f"混合均匀即得 **{v_total:.2f} mL** {c_target}% 目标乳液。"
            )

st.markdown("---")
st.caption(
    "💡 提示：后续可在 `calculate_emulsion` 函数中扩展水相溶质计算（如乙酸浓度）。"
    "所有计算逻辑集中在文件顶部的核心模块中。"
)
