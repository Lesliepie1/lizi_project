import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

# =========================
# 全局样式
# =========================
# 加载同级目录的 SimHei.ttf
my_font = font_manager.FontProperties(fname="SimHei.ttf")

plt.rcParams['font.family'] = my_font.get_name()
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="产品价格差额可视化", layout="wide")
st.title("🛒 产品价格比较与动态差额可视化")

# =========================
# 上传 Excel
# =========================
uploaded_file = st.file_uploader("📁 上传 Excel 文件", type=['xlsx', 'xls'])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    required_cols = {'产品名', '数量'}
    if not required_cols.issubset(df.columns):
        st.error("Excel 必须包含 '产品名' 和 '数量' 列")
    else:
        dealer_cols = [col for col in df.columns if col not in ['产品名', '数量']]
        if len(dealer_cols) < 2:
            st.error("至少需要两个经销商价格列")
        else:
            products = df['产品名'].tolist()
            n_products = len(products)
            x = np.arange(n_products)
            width = 0.8 / len(dealer_cols)  # 每个经销商宽度均分

            # =========================
            # 静态柱状图（显示所有经销商价格）
            # =========================
            st.subheader("📊 Excel 数据")
            st.dataframe(df)

            fig1, ax1 = plt.subplots(figsize=(max(12, n_products * 0.6), 6))
            for i, dealer in enumerate(dealer_cols):
                df[dealer] = pd.to_numeric(df[dealer], errors='coerce')
                ax1.bar(x - 0.4 + i*width + width/2, df[dealer], width, label=dealer, alpha=0.8, edgecolor='k')

            ax1.set_xticks(x)
            ax1.set_xticklabels(products, rotation=0, ha='center', fontsize=10)
            ax1.set_ylabel('价格', fontsize=11)
            ax1.set_title('静态产品价格（所有经销商）', fontsize=14)
            ax1.legend(fontsize=10)
            ax1.grid(axis='y', linestyle='--', alpha=0.3)
            plt.tight_layout()
            st.subheader("📈 静态柱状图")
            st.pyplot(fig1)

            # =========================
            # 动态总差额柱状图（用户选择经销商）
            # =========================
            st.subheader("⚡ 动态总差额柱状图")

            selected_dealers = st.multiselect(
                "选择两个经销商进行差额计算",
                dealer_cols,
                default=dealer_cols[:2]
            )

            if len(selected_dealers) != 2:
                st.warning("请选中 **两个** 经销商")
            else:
                dealer1_sel, dealer2_sel = selected_dealers
                df[dealer1_sel] = pd.to_numeric(df[dealer1_sel], errors='coerce')
                df[dealer2_sel] = pd.to_numeric(df[dealer2_sel], errors='coerce')
                df['差额选定'] = df[dealer1_sel] - df[dealer2_sel]

                # 创建滑块调整数量
                quantities = {}
                for product in products:
                    default_qty = int(df.loc[df['产品名'] == product, '数量'].values[0])
                    quantities[product] = st.slider(
                        f"{product} 数量",
                        min_value=0,
                        max_value=10000,
                        value=default_qty,
                        step=1
                    )

                df['数量'] = df['产品名'].map(quantities)
                df['总差额'] = df['差额选定'] * df['数量']
                total_diff = df['总差额'].sum()
                st.write(f"所有产品总差额: {total_diff:.0f}")

                # 绘制动态总差额柱状图
                fig2, ax2 = plt.subplots(figsize=(max(12, n_products * 0.6), 6))
                colors = ['#e74c3c' if val > 0 else '#2ecc71' for val in df['差额选定']]
                ax2.bar(x, df['总差额'].abs(), width, color=colors, alpha=0.9, edgecolor='k')

                # 右上角显示每个产品动态总差额
                diff_text = "\n".join([f"{products[i]}: {df['总差额'][i]:+.0f}" for i in range(n_products)])
                ax2.text(
                    1.02, 0.95, diff_text, transform=ax2.transAxes, fontsize=10,
                    verticalalignment='top', horizontalalignment='left',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray')
                )

                ax2.set_xticks(x)
                ax2.set_xticklabels(products, rotation=0, ha='center', fontsize=10)
                ax2.set_ylabel('总差额', fontsize=11)
                ax2.set_title(f'动态总差额 (总合={total_diff:.0f})', fontsize=14)
                ax2.grid(axis='y', linestyle='--', alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig2)


