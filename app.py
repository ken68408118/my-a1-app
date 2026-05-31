import streamlit as st
import akshare as ak
import numpy as np
import time
from datetime import datetime
import pytz  # 引入时区控制工具

# 1. 设置网页标题和图标
st.set_page_config(page_title="A股实时中位数看板", page_icon="📊", layout="centered")
st.title("📊 A股每日实时中位数看板")
st.caption("数据每 30 秒自动刷新一次，支持工作日盘中实时监控")

# 2. 获取并计算数据
@st.fragment(run_every=30)
def show_data():
    # --- 【核心修复】强制获取北京时间 ---
    bj_tz = pytz.timezone('Asia/Shanghai')
    now_bj = datetime.now(bj_tz)
    
    # 获取当前是星期几用于判断周末
    current_text_day = now_bj.strftime("%A")
    is_weekend = current_text_day in ["Saturday", "Sunday"]
    
    # 区分周末模拟与工作日真实数据
    if is_weekend:
        all_pct_changes = np.random.uniform(-10.0, 10.0, 5300)
        st.toast("⚠️ 当前为周末，正在展示模拟测试数据", icon="ℹ️")
    else:
        try:
            df = ak.stock_zh_a_spot_em()
            valid_stocks = df[(df['最新价'] > 0) & (df['涨跌幅'].notna())]
            all_pct_changes = valid_stocks['涨跌幅'].values
        except Exception as e:
            st.error(f"数据抓取失败: {e}")
            return

    # 计算各项指标
    median_value = np.median(all_pct_changes)
    up_count = int(np.sum(all_pct_changes > 0))
    down_count = int(np.sum(all_pct_changes < 0))
    flat_count = int(np.sum(all_pct_changes == 0))

    # 4. 在网页上展现（使用格式化后的北京时间）
    st.markdown(f"### 🕒 刷新时间: `{now_bj.strftime('%Y-%m-%d %H:%M:%S')}`")
    
    # 全A中位数大字显示
    color = "red" if median_value >= 0 else "green"
    st.markdown(f"## 全A涨跌幅中位数: <span style='color:{color}; font-size:40px; font-weight:bold;'>{median_value:+.2f}%</span>", unsafe_allow_html=True)
    
    st.divider() # 画一条分割线

    # 三栏布局
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📈 上涨家数", value=f"{up_count} 家", delta=f"+{up_count}")
    with col2:
        st.metric(label="↔️ 平盘家数", value=f"{flat_count} 家")
    with col3:
        st.metric(label="📉 下跌家数", value=f"{down_count} 家", delta=f"-{down_count}", delta_color="inverse")

# 运行展现函数
show_data()
