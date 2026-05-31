import streamlit as st
import akshare as ak
import numpy as np
import time

# 1. 设置网页标题和图标
st.set_page_config(page_title="A股实时中位数看板", page_icon="📊", layout="centered")
st.title("📊 A股每日实时中位数看板")
st.caption("数据每 30 秒自动刷新一次，支持工作日盘中实时监控")

# 2. 网页自动刷新机制（每30秒刷新一次）
# 利用 streamlit 的 rerun 机制实现定时器
if "fragment_rerun" not in st.session_state:
    st.session_state.fragment_rerun = True

# 3. 获取并计算数据
@st.fragment(run_every=30)
def show_data():
    current_text_day = time.strftime("%A")
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

    # 4. 在网页上画出精美的大屏组件（Metric 仪表盘）
    st.markdown(f"### 🕒 刷新时间: `{time.strftime('%Y-%m-%d %H:%M:%S')}`")
    
    # 全A中位数大字显示
    # 如果中位数大于0显示红色，小于0显示绿色
    color = "red" if median_value >= 0 else "green"
    st.markdown(f"## 全A涨跌幅中位数: <span style='color:{color}; font-size:40px; font-weight:bold;'>{median_value:+.2f}%</span>", unsafe_allow_html=True)
    
    st.divider() # 画一条分割线

    # 三栏布局，显示上涨、平盘、下跌家数
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📈 上涨家数", value=f"{up_count} 家", delta=f"+{up_count}")
    with col2:
        st.metric(label="↔️ 平盘家数", value=f"{flat_count} 家")
    with col3:
        st.metric(label="📉 下跌家数", value=f"{down_count} 家", delta=f"-{down_count}", delta_color="inverse")

# 运行展现函数
show_data()