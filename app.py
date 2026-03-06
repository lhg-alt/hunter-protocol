import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ─────────────────────────────────────────
# 페이지 설정 및 CSS (재민의 스타일 유지)
# ─────────────────────────────────────────
st.set_page_config(page_title="HUNTER PROTOCOL v2", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }
    .stApp { background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%) !important; }
    .hunter-title {
        font-family: 'IBM Plex Mono', monospace !important; font-weight: 700; font-size: 2.2rem;
        background: linear-gradient(135deg, #1e293b, #334155);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .card-container {
        background: white; border-radius: 20px; padding: 20px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 비밀번호 및 매수 원칙 
# ─────────────────────────────────────────
PASSWORD = "1116"
if "authenticated" not in st.session_state: st.session_state.authenticated = False

STAGES = [
    {"stage": 1, "label": "1단계", "drop": 20, "pct": 0.15, "color": "#2563eb", "emoji": "🔵"},
    {"stage": 2, "label": "2단계", "drop": 35, "pct": 0.25, "color": "#059669", "emoji": "🟢"},
    {"stage": 3, "label": "3단계", "drop": 50, "pct": 0.35, "color": "#d97706", "emoji": "🟡"},
    {"stage": 4, "label": "4단계", "drop": 60, "pct": 0.25, "color": "#dc2626", "emoji": "🔴"},
]

# ─────────────────────────────────────────
# 세션 데이터 (비중 및 섹터 정보 추가)
# ─────────────────────────────────────────
if "stocks" not in st.session_state:
    st.session_state.stocks = [
        {"team": "white", "ticker": "NEE", "weight": 25, "is_special": False},
        {"team": "white", "ticker": "CEG", "weight": 25, "is_special": False},
        {"team": "blue", "ticker": "IONQ", "weight": 5, "is_special": True}, # 양자
        {"team": "blue", "ticker": "CRWD", "weight": 20, "is_special": False},
    ]

# ─────────────────────────────────────────
# 사이드바: 3분할 비중 설정 (White / Blue / Cash)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.divider()
    total_seed = st.number_input("전체 시드 (USD $)", value=100000, step=1000)
    ex_rate = st.number_input("환율 (KRW)", value=1380)
    
    st.markdown("#### ⚖️ 자산 배분")
    w_ratio = st.slider("🛡 화이트 팀 (%)", 0, 100, 40)
    b_ratio = st.slider("🚀 블루 팀 (%)", 0, (100 - w_ratio), 40)
    c_ratio = 100 - w_ratio - b_ratio
    st.info(f"🏦 현금 비중: {c_ratio}%")
    
    st.divider()
    if st.button("🔄 새로고침", type="primary"): st.cache_data.clear(); st.rerun()

w_budget = total_seed * (w_ratio / 100)
b_budget = total_seed * (b_ratio / 100)
c_reserve = total_seed * (c_ratio / 100)

# ─────────────────────────────────────────
# 메인 화면
# ─────────────────────────────────────────
st.markdown('<p class="hunter-title">🎯 HUNTER PROTOCOL</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🛡 화이트 예산", f"${w_budget:,.0f}")
col2.metric("🚀 블루 예산", f"${b_budget:,.0f}")
col3.metric("🏦 현금 예비군", f"${c_reserve:,.0f}")
col4.metric("💱 원화 총액", f"₩{(total_seed * ex_rate):,.0f}")

# ─────────────────────────────────────────
# 데이터 로드 및 렌더링
# ─────────────────────────────────────────
@st.cache_data(ttl=600)
def get_data(ticker):
    try:
        t = yf.Ticker(ticker)
        return {"price": t.info['currentPrice'], "ath": t.info['fiftyTwoWeekHigh'], "name": t.info['shortName']}
    except: return None

def render_team(team_id):
    team_name = "🛡 화이트 팀" if team_id == "white" else "🚀 블루 팀"
    team_budget = w_budget if team_id == "white" else b_budget
    team_stocks = [s for s in st.session_state.stocks if s['team'] == team_id]
    
    st.subheader(f"{team_name} (예산: ${team_budget:,.0f})")
    
    # 블루팀 전략 섹터 체크
    if team_id == "blue":
        special_w = sum(s['weight'] for s in team_stocks if s['is_special'])
        st.caption(f"🧬 전략 섹터(양자/장수/우주) 현재 비중: **{special_w}%** (목표: 15%)")
        if special_w != 15: st.warning("⚠️ 전략 섹터 비중을 15%로 조정하세요.")

    for s in team_stocks:
        data = get_data(s['ticker'])
        if data:
            drop = (data['ath'] - data['price']) / data['ath'] * 100
            stock_total_budget = team_budget * (s['weight'] / 100)
            
            with st.expander(f"**{s['ticker']}** - 현재가: ${data['price']} (하락률: {drop:.1f}%)", expanded=(drop >= 20)):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write(f"**종목 할당 예산:** ${stock_total_budget:,.0f}")
                    st.write(f"**팀 내 비중:** {s['weight']}%")
                
                with c2:
                    st.markdown("**📉 단계별 매수 시뮬레이션**")
                    grid = st.columns(4)
                    for i, stage in enumerate(STAGES):
                        buy_amt = stock_total_budget * stage['pct']
                        is_active = drop >= stage['drop']
                        box_color = stage['color'] if is_active else "#f1f5f9"
                        text_color = "white" if is_active else "#94a3b8"
                        grid[i].markdown(
                            f"<div style='background:{box_color}; color:{text_color}; padding:10px; border-radius:10px; text-align:center; font-size:0.8rem; border:1px solid #e2e8f0;'>"
                            f"<b>{stage['label']}</b><br>${buy_amt:,.0f}<br>₩{(buy_amt*ex_rate):,.0f}</div>", 
                            unsafe_allow_html=True
                        )

render_team("white")
st.divider()
render_team("blue")

# 종목 추가 UI (간소화)
with st.sidebar:
    st.divider()
    st.write("➕ 종목 추가")
    new_team = st.selectbox("팀 선택", ["white", "blue"])
    new_tk = st.text_input("티커")
    new_w = st.number_input("비중 (%)", value=10)
    is_sp = st.checkbox("전략 섹터 (양자/장수/우주)")
    if st.button("추가하기"):
        st.session_state.stocks.append({"team": new_team, "ticker": new_tk.upper(), "weight": new_w, "is_special": is_sp})
        st.rerun()
