"""
HUNTER PROTOCOL v5 — 윌리엄 분미프 매뉴얼 완벽 적용판
Streamlit + yfinance | S&P500 듀얼 트리거 + 10분할 매수 시스템 + 자산 분리
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="HUNTER PROTOCOL | 분미프",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CSS (밝은 테마 및 카드 스타일)
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }

    .stApp { background: linear-gradient(145deg, #eef2ff 0%, #f8fafc 50%, #ecfdf5 100%) !important; }
    p, div, span, label, h1, h2, h3, h4, h5, li, td, th { color: #1e293b !important; }

    /* 사이드바 */
    [data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #334155 !important; font-weight: 500 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5 { color: #0f172a !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] input { background: #f8fafc !important; border: 1px solid #cbd5e1 !important; color: #0f172a !important; border-radius: 10px !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 1px #3b82f6 !important; }
    [data-testid="stSidebar"] hr { border-bottom-color: #e2e8f0 !important; }

    /* 메트릭 및 컨테이너 */
    [data-testid="metric-container"] { background: white !important; border: 1px solid #e2e8f0 !important; border-radius: 16px !important; padding: 16px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important; }
    [data-testid="stMetricLabel"] p { color: #64748b !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 900 !important; }
    [data-testid="stMetricDelta"] { color: #059669 !important; }

    .stButton > button { border-radius: 12px !important; font-weight: 700 !important; font-family: 'Noto Sans KR', sans-serif !important; border: 1.5px solid #e2e8f0 !important; color: #334155 !important; background: white !important; transition: all 0.2s !important; }
    .stButton > button:hover { border-color: #94a3b8 !important; background: #f8fafc !important; color: #0f172a !important; }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #2563eb, #1d4ed8) !important; color: white !important; border: none !important; }
    .stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #1d4ed8, #1e40af) !important; color: white !important; }
    .del-btn > button { background: #fef2f2 !important; border: 1.5px solid #fca5a5 !important; color: #dc2626 !important; border-radius: 10px !important; font-size: 0.8rem !important; padding: 4px 8px !important; }
    .del-btn > button:hover { background: #fee2e2 !important; border-color: #f87171 !important; color: #b91c1c !important; }
    .add-btn > button { background: #f0fdf4 !important; border: 2px dashed #86efac !important; color: #16a34a !important; border-radius: 12px !important; font-weight: 700 !important; }
    .add-btn > button:hover { background: #dcfce7 !important; border-color: #4ade80 !important; color: #15803d !important; }
    div[data-testid="stExpander"] { background: white !important; border-radius: 16px !important; border: 1px solid #e2e8f0 !important; }
    .stTextInput input { color: #1e293b !important; background: white !important; border-radius: 10px !important; border: 1.5px solid #e2e8f0 !important; }

    .stDataFrame { border-radius: 16px !important; overflow: hidden !important; }
    .stDataFrame table { border-collapse: separate !important; border-spacing: 0 !important; }
    .stDataFrame thead tr th { background: #1e293b !important; color: white !important; font-weight: 700 !important; padding: 12px 16px !important; font-size: 0.85rem !important; }
    .stDataFrame tbody tr:nth-child(even) td { background: #f8fafc !important; }
    .stDataFrame tbody tr:hover td { background: #eff6ff !important; }
    .stDataFrame tbody tr td { color: #1e293b !important; font-size: 0.88rem !important; padding: 10px 16px !important; }

    .hunter-title { font-family: 'IBM Plex Mono', monospace !important; font-weight: 700; font-size: 2rem; background: linear-gradient(135deg, #2563eb, #0ea5e9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -1px; }

    /* 라디오 버튼 커스텀 (트리거 선택용) */
    div.row-widget.stRadio > div { background: white; padding: 10px 20px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; gap: 20px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 비밀번호 보호
# ─────────────────────────────────────────
PASSWORD = "1116"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width:400px;margin:80px auto;background:white;border-radius:24px; padding:48px 40px;box-shadow:0 8px 40px rgba(0,0,0,0.12);border:1px solid #e2e8f0;text-align:center;">
      <div style="font-size:3rem;margin-bottom:8px">🎯</div>
      <div class="hunter-title">HUNTER PROTOCOL</div>
      <div style="color:#64748b !important;font-size:0.9rem;margin:10px 0 24px;">재민의 폭락장 저점 매수 시스템</div>
    </div>
    """, unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        pw = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
        if st.button("🔓  입장하기", use_container_width=True, type="primary"):
            if pw == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# ─────────────────────────────────────────
# 매수 원칙 및 지수 트리거
# ─────────────────────────────────────────
STAGES = [
    {"stage": 1, "label": "1단계: 정찰병 배치", "hunter_msg": "적의 움직임 포착 — 소량 선제 진입", "drop_threshold": 20, "pct": 0.15, "color": "#2563eb", "bg": "#eff6ff", "emoji": "🔵"},
    {"stage": 2, "label": "2단계: 부대 전진",   "hunter_msg": "전장 확인 — 본격 포지션 구축", "drop_threshold": 35, "pct": 0.25, "color": "#059669", "bg": "#f0fdf4", "emoji": "🟢"},
    {"stage": 3, "label": "3단계: 주력군 투입", "hunter_msg": "전면전 개시 — 핵심 물량 확보 (VIX 60 이상)", "drop_threshold": 50, "pct": 0.35, "color": "#d97706", "bg": "#fffbeb", "emoji": "🟡"},
    {"stage": 4, "label": "4단계: 총력전 대비", "hunter_msg": "시스템 위기 — 최후의 유동성", "drop_threshold": 60, "pct": 0.25, "color": "#dc2626", "bg": "#fef2f2", "emoji": "🔴"},
]

# ─────────────────────────────────────────
# 세션 상태
# ─────────────────────────────────────────
if "white_stocks" not in st.session_state:
    st.session_state.white_stocks = [
        {"ticker": "NEE", "type": "일반"}, {"ticker": "CEG", "type": "일반"},
        {"ticker": "WEC", "type": "일반"}, {"ticker": "SO", "type": "일반"}
    ]
if "blue_stocks" not in st.session_state:
    st.session_state.blue_stocks = [
        {"ticker": "CRWD", "type": "일반"}, {"ticker": "PLTR", "type": "일반"},
        {"ticker": "NVDA", "type": "일반"}, {"ticker": "IONQ", "type": "특수"}
    ]
if "show_add_white" not in st.session_state: st.session_state.show_add_white = False
if "show_add_blue" not in st.session_state: st.session_state.show_add_blue = False

# ─────────────────────────────────────────
# 데이터 패치 유틸리티
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_macro_data():
    try:
        spy = yf.Ticker("SPY")
        vix = yf.Ticker("^VIX")
        
        def get_drop(t):
            hist = t.history(period="1y")
            cur = t.info.get("currentPrice", float(hist["Close"].iloc[-1]) if not hist.empty else 0)
            ath = t.info.get("fiftyTwoWeekHigh", float(hist["High"].max()) if not hist.empty else 0)
            if ath == 0: return 0, cur, ath
            return ((ath - cur) / ath * 100), cur, ath
            
        spy_drop, spy_cur, spy_ath = get_drop(spy)
        vix_cur = vix.info.get("currentPrice", float(vix.history(period="5d")["Close"].iloc[-1]))
        
        return {
            "SPY": {"drop": spy_drop, "current": spy_cur, "ath": spy_ath},
            "VIX": {"current": vix_cur},
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        if current is None and not hist.empty: current = float(hist["Close"].iloc[-1])
        ath_52w = float(hist["High"].max()) if not hist.empty else None
        ath = info.get("fiftyTwoWeekHigh") or ath_52w
        name = info.get("shortName") or info.get("longName") or ticker
        return {
            "ticker": ticker.upper(), "name": name,
            "current": round(float(current), 2) if current else None,
            "ath":     round(float(ath),     2) if ath     else None,
            "success": True,
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "success": False, "error": str(e)}

def get_stage(drop_pct):
    if drop_pct < 20: return None
    for s in reversed(STAGES[:3]):
        if drop_pct >= s["drop_threshold"]: return s
    return STAGES[0]

def fmt_usd(v): return "${:,.0f}".format(v)
def fmt_krw(v): return "₩{:,.0f}".format(v)

# ─────────────────────────────────────────
# 사이드바 (투입 시드 설정)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.caption("분할매수! 미래섹터! 프레임 탈출!")
    st.divider()
    
    st.markdown("#### 💰 투자 목표(Target) 세팅")
    total_seed    = st.number_input("전체 가용 시드 (USD $)", min_value=1000, max_value=10_000_000, value=100_000, step=1000, format="%d", help="시장에 최종적으로 투입할 전체 금액")
    exchange_rate = st.number_input("환율 (USD→KRW)", min_value=1000, max_value=2000, value=1380, step=10)
    
    st.divider()
    st.markdown("##### ⚖️ 팀별 목표 비중 (Target %)")
    white_ratio = st.slider("🛡 백팀(안전금고) 목표 비중", 0, 100, 50, 5)
    blue_ratio  = 100 - white_ratio
    st.caption(f"🚀 청팀(세포분열) 목표 비중: **{blue_ratio}%**")
    
    st.divider()
    if st.button("🔄  데이터 새로고침", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.success("캐시 초기화 완료!")
        time.sleep(0.4)
        st.rerun()
    if st.button("🚪  로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ─────────────────────────────────────────
# 메인 헤더 및 분미프 매뉴얼 요약
# ─────────────────────────────────────────
hc1, hc2 = st.columns([3, 1])
with hc1:
    st.markdown('<p class="hunter-title">🎯 HUNTER PROTOCOL</p>', unsafe_allow_html=True)
    st.markdown("재민의 퀀트 대시보드 — **거대 자본(상어)을 어군탐지기로 써라!**")
with hc2:
    st.metric("가용 시드 총액", fmt_usd(total_seed))

with st.expander("📜 윌리엄의 분미프 핵심 매뉴얼 요약 (클릭하여 읽기)", expanded=False):
    st.markdown("""
    1. **자산은 평생 백팀과 청팀 50:50 유지:** 백팀은 돈을 지켜줄 금고, 청팀은 돈을 불려줄 세포분열 공간이다.
    2. **수익의 재배치:** 청팀에서 발생한 수익은 즉시 백팀(안전금고)으로 보관한다.
    3. **청팀 1군(양장우) 30%룰:** 양자컴퓨터, 장수과학, 우주경제 핵심 대장주에 청팀 예산의 30%(전체의 15%)를 최우선 할당한다.
    4. **10분할 분할매수 절대 원칙:** 한 기업이 저점에 올 때마다 해당 기업 예산의 1/10씩, **주 1회 원칙**으로 **최소 3개월간** 분할 매수한다.
    5. **10~20개 종목 제한:** 스스로 컨트롤 가능한 범위를 넘어선 오만을 버려라. 물 새는 바가지가 된다.
    """)
st.divider()

# ─────────────────────────────────────────
# 거시 경제 레이더 및 트리거 전환 (S&P 500 단일화)
# ─────────────────────────────────────────
macro_data = fetch_macro_data()
market_max_drop = 0
if macro_data["success"]:
    spy_drop = macro_data["SPY"]["drop"]
    vix_val = macro_data["VIX"]["current"]
    market_max_drop = spy_drop  # 시장 지수는 S&P 500 기준 단일화
    
    idx_alert = "🟢 시장 정상"
    if spy_drop >= 40: idx_alert = "🔴 금융위기 (Capitulation)"
    elif spy_drop >= 25: idx_alert = "🟠 폭락장 (Panic)"
    elif spy_drop >= 10: idx_alert = "🟡 일반 조정장"
    
    st.markdown(f"### 📡 시장 거시 레이더 (Market Radar) : {idx_alert}")
    r1, r2 = st.columns(2)
    
    r1.markdown(
        f"<div style='background:white;border-radius:16px;padding:20px;border:1px solid #e2e8f0;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>"
        f"<div style='color:#64748b;font-weight:700;font-size:0.9rem;margin-bottom:8px;'>S&P 500 (SPY) — 시장의 나침반</div>"
        f"<div style='color:#0f172a;font-weight:900;font-size:1.8rem;'>${macro_data['SPY']['current']:.2f}</div>"
        f"<div style='color:{'#dc2626' if spy_drop>=10 else '#059669'};font-weight:700;font-size:1rem;margin-top:4px;'>ATH 대비 -{spy_drop:.1f}%</div>"
        f"</div>", unsafe_allow_html=True
    )
    r2.markdown(
        f"<div style='background:white;border-radius:16px;padding:20px;border:1px solid #e2e8f0;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>"
        f"<div style='color:#64748b;font-weight:700;font-size:0.9rem;margin-bottom:8px;'>공포 지수 (VIX) — 대중의 탐욕과 공포</div>"
        f"<div style='color:#0f172a;font-weight:900;font-size:1.8rem;'>{vix_val:.2f}</div>"
        f"<div style='color:{'#dc2626' if vix_val>=60 else ('#d97706' if vix_val>=30 else '#059669')};font-weight:700;font-size:1rem;margin-top:4px;'>{'위기 수준 (60 이상)' if vix_val>=60 else ('불안 수준 (30 이상)' if vix_val>=30 else '안정 수준')}</div>"
        f"</div>", unsafe_allow_html=True
    )

st.markdown("<br>### 🎛️ 사냥 기준(Trigger) 모드 선택", unsafe_allow_html=True)
trigger_mode = st.radio(
    "매수 단계를 판별할 기준 지표를 선택하세요:",
    ["종목별 전고점 (ATH) 기준", "시장 지수 (S&P 500) 기준"],
    horizontal=True,
    label_visibility="collapsed"
)
is_index_mode = "S&P 500" in trigger_mode

if is_index_mode:
    st.info(f"💡 현재 **S&P 500 지수 기준** 모드입니다. 개별 종목과 무관하게, 시장 지수 하락률(-{market_max_drop:.1f}%)을 기준으로 모든 포트폴리오에 일괄 매수 단계가 적용됩니다.", icon="📊")
else:
    st.success("💡 현재 **개별 종목 전고점 기준** 모드입니다. 각 종목의 52주 전고점 대비 하락률에 따라 개별적으로 매수 단계가 계산됩니다.", icon="🎯")

st.divider()

# ─────────────────────────────────────────
# 백그라운드 데이터 사전 계산 (Current Status 파악용)
# ─────────────────────────────────────────
target_white_budget = total_seed * (white_ratio / 100)
target_blue_budget  = total_seed * (blue_ratio  / 100)

current_white_invested = 0
current_blue_invested = 0
stock_cache = {}
allocations = {"white": {}, "blue": {}}

# 화이트팀 계산
w_stocks = st.session_state.white_stocks
if w_stocks:
    eq_w = 100 / len(w_stocks)
    alloc_amt = target_white_budget * (eq_w / 100)
    for s in w_stocks:
        tk = s["ticker"]
        allocations["white"][tk] = {"weight": eq_w, "budget": alloc_amt}
        data = fetch_stock_data(tk)
        stock_cache[tk] = data
        if data["success"] and data["current"] and data["ath"]:
            stock_drop = ((data["ath"] - data["current"]) / data["ath"] * 100)
            effective_drop = market_max_drop if is_index_mode else stock_drop
            stage = get_stage(effective_drop)
            if stage and stage["stage"] < 4:
                # 현재 단계 권장 누적 매수금액 (보수적 집계)
                current_white_invested += alloc_amt * stage["pct"]

# 블루팀 계산 (15% 1군 양장우 포함)
b_stocks = st.session_state.blue_stocks
if b_stocks:
    special_stocks = [s for s in b_stocks if s.get("type") == "특수"]
    normal_stocks  = [s for s in b_stocks if s.get("type") != "특수"]
    sp_total_w = 30 if special_stocks and normal_stocks else (100 if special_stocks else 0) # 청팀 예산의 30% = 전체 시드의 15%
    nm_total_w = 70 if special_stocks and normal_stocks else (100 if normal_stocks else 0)
    
    for s in special_stocks:
        tk = s["ticker"]
        w = sp_total_w / len(special_stocks)
        allocations["blue"][tk] = {"weight": w, "budget": target_blue_budget * (w / 100)}
    for s in normal_stocks:
        tk = s["ticker"]
        w = nm_total_w / len(normal_stocks)
        allocations["blue"][tk] = {"weight": w, "budget": target_blue_budget * (w / 100)}
        
    for s in b_stocks:
        tk = s["ticker"]
        data = fetch_stock_data(tk)
        stock_cache[tk] = data
        if data["success"] and data["current"] and data["ath"]:
            stock_drop = ((data["ath"] - data["current"]) / data["ath"] * 100)
            effective_drop = market_max_drop if is_index_mode else stock_drop
            stage = get_stage(effective_drop)
            if stage and stage["stage"] < 4:
                current_blue_invested += allocations["blue"][tk]["budget"] * stage["pct"]

current_total_invested = current_white_invested + current_blue_invested
current_cash_remaining = total_seed - current_total_invested

# ─────────────────────────────────────────
# 자산 분리 대시보드 (Target vs Current)
# ─────────────────────────────────────────
st.markdown("### ⚡ 포트폴리오 자산 배분 분석")
tc1, tc2 = st.columns(2)

with tc1:
    st.markdown(
        f"<div style='background:white;border-radius:20px;padding:24px;border:2px solid #cbd5e1;box-shadow:0 4px 12px rgba(0,0,0,0.05);height:100%;'>"
        f"<div style='color:#1e293b;font-weight:900;font-size:1.1rem;margin-bottom:4px;'>🎯 목표 비중 (Target Allocation)</div>"
        f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:16px;'>모든 시드가 시장에 투입되었을 때의 평생 유지 나침반</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:8px;'>"
        f"<div><span style='color:#2563eb;font-weight:800;'>🛡 백팀 (안전금고)</span> <span style='font-weight:700;'>{white_ratio}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(target_white_budget)}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:16px;'>"
        f"<div><span style='color:#10b981;font-weight:800;'>🚀 청팀 (세포분열)</span> <span style='font-weight:700;'>{blue_ratio}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(target_blue_budget)}</div>"
        f"</div>"
        f"<div style='width:100%;height:12px;border-radius:6px;display:flex;overflow:hidden;'>"
        f"<div style='width:{white_ratio}%;background:#3b82f6;'></div>"
        f"<div style='width:{blue_ratio}%;background:#10b981;'></div>"
        f"</div>"
        f"</div>", unsafe_allow_html=True
    )

with tc2:
    cur_w_pct = (current_white_invested / total_seed) * 100 if total_seed > 0 else 0
    cur_b_pct = (current_blue_invested / total_seed) * 100 if total_seed > 0 else 0
    cur_c_pct = (current_cash_remaining / total_seed) * 100 if total_seed > 0 else 0
    
    st.markdown(
        f"<div style='background:white;border-radius:20px;padding:24px;border:2px solid #3b82f6;box-shadow:0 4px 12px rgba(59,130,246,0.15);height:100%;'>"
        f"<div style='color:#1e293b;font-weight:900;font-size:1.1rem;margin-bottom:4px;'>📊 현재 집행 상태 (Current Status)</div>"
        f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:16px;'>매수 신호에 의해 현재 시드가 시장에 투입된 실제 비율</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
        f"<div><span style='color:#2563eb;font-weight:800;'>🛡 집행된 백팀</span> <span style='font-weight:700;'>{cur_w_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(current_white_invested)}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
        f"<div><span style='color:#10b981;font-weight:800;'>🚀 집행된 청팀</span> <span style='font-weight:700;'>{cur_b_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(current_blue_invested)}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:16px;'>"
        f"<div><span style='color:#64748b;font-weight:800;'>🏦 대기 현금(보루)</span> <span style='font-weight:700;'>{cur_c_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(current_cash_remaining)}</div>"
        f"</div>"
        f"<div style='width:100%;height:12px;border-radius:6px;display:flex;overflow:hidden;background:#e2e8f0;'>"
        f"<div style='width:{cur_w_pct}%;background:#3b82f6;'></div>"
        f"<div style='width:{cur_b_pct}%;background:#10b981;'></div>"
        f"</div>"
        f"</div>", unsafe_allow_html=True
    )

st.divider()

# ─────────────────────────────────────────
# 종목 카드 및 팀 렌더 함수 (10분할 로직 추가)
# ─────────────────────────────────────────
def render_stock_card(ticker, data, stage, stock_drop, effective_drop, alloc_budget, alloc_w, team_color, team_key, is_special=False, is_idx_mode=False):
    current = data["current"]
    ath     = data["ath"]
    ath_str = "${:,.2f}".format(ath) if ath else "—"

    # 매뉴얼 10분할 매수 로직 (종목당 총 예산의 1/10)
    split_10_usd = alloc_budget / 10
    split_10_krw = split_10_usd * exchange_rate

    with st.container():
        badge_cols = st.columns([1, 1])
        with badge_cols[0]:
            if stage:
                st.markdown(
                    "<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:{bg};color:{c};border:1.5px solid {c}66;'>{emoji} {label}</span>".format(bg=stage['bg'], c=stage['color'], emoji=stage['emoji'], label=stage['label']), unsafe_allow_html=True)
            elif effective_drop is not None:
                st.markdown("<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'>⏳ 사냥터 접근 전</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;'>— 데이터 없음</span>", unsafe_allow_html=True)

        info_c1, info_c2 = st.columns(2)
        with info_c1:
            drop_str  = "-{:.1f}%".format(stock_drop) if stock_drop is not None else "—"
            drop_color = "#dc2626" if (stock_drop is not None and stock_drop >= 20) else "#059669"
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;border:1.5px solid {border};box-shadow:0 2px 8px rgba(0,0,0,0.04);'>"
                "<div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>"
                "<div style='min-width:40px;height:40px;border-radius:10px;background:{tc};display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:0.72rem;'>{tick}</div>"
                "<div><div style='font-weight:900;color:#0f172a;font-size:1rem;'>{ticker}</div>"
                "<div style='color:#64748b;font-size:0.75rem;'>{name}</div></div></div>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-end;'>"
                "<div><div style='color:#64748b;font-size:0.7rem;'>현재가</div>"
                "<div style='font-weight:900;color:#0f172a;font-size:1.15rem;'>{cur}</div></div>"
                "<div style='text-align:right;'><div style='color:#64748b;font-size:0.7rem;'>실제 종목 하락률</div>"
                "<div style='font-weight:900;color:{dc};font-size:1.15rem;'>{ds}</div></div></div></div>".format(
                    border=(stage["color"] + "44") if stage else "#e2e8f0", tc=team_color, tick=ticker[:4], ticker=ticker, name=data['name'][:22], cur="${:,.2f}".format(current) if current else "—", dc=drop_color, ds=drop_str
                ), unsafe_allow_html=True)

        with info_c2:
            special_badge = "<div style='display:inline-block; padding:2px 6px; background:#e0e7ff; color:#4f46e5; border-radius:4px; font-size:0.65rem; margin-bottom:4px; font-weight:700;'>✨ 1군 전략 섹터 (양·장·우)</div><br>" if is_special else ""
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);height:100%;'>"
                f"{special_badge}"
                "<div style='color:#64748b;font-size:0.7rem;margin-bottom:2px;'>팀 내 목표 비중 (이 종목 총 예산)</div>"
                "<div style='font-weight:900;color:#0f172a;font-size:1rem;margin-bottom:10px;'>{w:.1f}% <span style='font-size:0.8rem;color:#64748b;font-weight:400;'>(${budget:,.0f})</span></div>"
                "<div style='color:#64748b;font-size:0.7rem;margin-bottom:2px;'>52주 ATH</div>"
                "<div style='font-weight:700;color:#0f172a;font-size:1rem;'>{ath}</div></div>".format(w=alloc_w, budget=alloc_budget, ath=ath_str), unsafe_allow_html=True)

        # 10분할 매수 권장액 블록 노출
        if stage and stage["stage"] < 4:
            basis_text = "S&P 500 시장 지수 하락분" if is_idx_mode else "개별 종목 고점 하락분"
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;border:2px solid {c}44;margin-top:8px;'>"
                "<div style='color:#64748b;font-size:0.72rem;margin-bottom:4px;'>🔥 <b>{basis} 반영</b> | 10분할 중 1회 권장 매수액</div>"
                "<div style='display:flex; justify-content:space-between; align-items:center;'>"
                "<div><div style='font-weight:900;color:{c};font-size:1.3rem;'>{usd}</div>"
                "<div style='color:#475569;font-size:0.85rem;margin-top:2px;'>{krw}</div></div>"
                "<div style='text-align:right; font-size:0.75rem; color:#64748b; background:#f1f5f9; padding:6px 10px; border-radius:8px;'><b>매뉴얼: 주 1회 원칙</b><br>최소 3개월 분할</div>"
                "</div>"
                "</div>".format(c=stage['color'], basis=basis_text, usd="${:,.0f}".format(split_10_usd), krw="≈ ₩{:,.0f}".format(split_10_krw)), unsafe_allow_html=True)
        elif effective_drop is not None and effective_drop < 20:
            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
            st.info(f"현재 적용 하락률 {effective_drop:.1f}% — 20% 초과 시 매수 개시", icon="⏳")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        del_c1, del_c2 = st.columns([4, 1])
        with del_c2:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("🗑 삭제", key="del_{}_{}".format(team_key, ticker), use_container_width=True):
                st.session_state["{}_stocks".format(team_key)] = [s for s in st.session_state["{}_stocks".format(team_key)] if s["ticker"] != ticker]
                st.cache_data.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

def render_team(team_key, team_label, team_budget, team_color, team_emoji):
    stocks = st.session_state["{}_stocks".format(team_key)]
    is_white = team_key == "white"
    grad = ("linear-gradient(135deg,#eff6ff,#dbeafe)" if is_white else "linear-gradient(135deg,#f0fdf4,#dcfce7)")

    st.markdown(
        "<div style='border-radius:20px;padding:18px 24px;margin-bottom:16px;background:{grad};border:2px solid {c}33;'>"
        "<span style='font-size:1.4rem'>{emoji}</span><span style='font-weight:900;color:{c};font-size:1.15rem;margin-left:8px;'>{label}</span>"
        "<span style='color:#475569;font-size:0.88rem;margin-left:12px;'>목표 예산: <strong style='color:#0f172a;'>{budget}</strong>&nbsp;(≈ {krw})</span>"
        "</div>".format(grad=grad, c=team_color, emoji=team_emoji, label=team_label, budget="${:,.0f}".format(team_budget), krw="₩{:,.0f}".format(team_budget * exchange_rate)), unsafe_allow_html=True)

    summary_rows = []
    for i in range(0, max(len(stocks), 1), 2):
        batch = stocks[i:i+2]
        if not batch: break
        cols = st.columns(len(batch))

        for col, stock_dict in zip(cols, batch):
            ticker = stock_dict["ticker"]
            is_special = stock_dict.get("type") == "특수"
            alloc_data = allocations[team_key][ticker]
            data = stock_cache.get(ticker, {"success": False})
            
            with col:
                if not data["success"]:
                    st.error("❌ {} 로드 실패".format(ticker))
                    continue
                current = data["current"]
                ath = data["ath"]
                stock_drop = ((ath - current) / ath * 100) if (current and ath) else None
                effective_drop = market_max_drop if is_index_mode else stock_drop
                
                stage = get_stage(effective_drop) if effective_drop is not None else None
                
                # 테이블 요약용 권장 매수금(1회 분할 분량) 산출
                buy_usd_1_split = alloc_data["budget"] / 10 if (stage and stage["stage"] < 4) else 0
                buy_krw_1_split = buy_usd_1_split * exchange_rate

                render_stock_card(ticker, data, stage, stock_drop, effective_drop, alloc_data["budget"], alloc_data["weight"], team_color, team_key, is_special, is_index_mode)

                summary_rows.append({
                    "팀": "🛡 백팀" if is_white else "🚀 청팀", "티커": ticker, "종목명": data["name"][:18],
                    "현재가": "${:,.2f}".format(current) if current else "—", "ATH": "${:,.2f}".format(ath) if ath else "—",
                    "적용 하락률": "{:.1f}%".format(effective_drop) if effective_drop is not None else "—", "단계": stage["label"] if stage else "대기 중",
                    "1회 분할매수(USD)": "${:,.0f}".format(buy_usd_1_split) if buy_usd_1_split > 0 else "—", "1회 분할매수(KRW)": "₩{:,.0f}".format(buy_krw_1_split) if buy_usd_1_split > 0 else "—",
                })

    # 종목 추가 UI
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    add_key = "show_add_{}".format(team_key)
    if not st.session_state[add_key]:
        st.markdown('<div class="add-btn">', unsafe_allow_html=True)
        if st.button("➕  {} 종목 추가".format(team_emoji), key="open_{}".format(team_key), use_container_width=True):
            st.session_state[add_key] = True; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:white;border-radius:16px;padding:16px 20px;border:2px dashed {c}88;margin-bottom:8px;'><span style='font-weight:700;color:{c};font-size:0.95rem;'>{emoji} 새 종목 티커 입력</span></div>".format(c=team_color, emoji=team_emoji), unsafe_allow_html=True)
        ac1, ac2, ac3 = st.columns([3, 1, 1])
        with ac1:
            new_tk = st.text_input("티커", placeholder="예: TSLA, AMZN...", key="inp_{}".format(team_key), label_visibility="collapsed")
            is_special_checked = False
            if not is_white: is_special_checked = st.checkbox("✨ 1군 전략 섹터 (양자/장수/우주)", key="chk_{}".format(team_key))
        with ac2:
            if st.button("✅  추가", key="confirm_{}".format(team_key), type="primary", use_container_width=True):
                tk = new_tk.strip().upper()
                existing = [s["ticker"] for s in st.session_state["{}_stocks".format(team_key)]]
                if tk and tk not in existing:
                    st.session_state["{}_stocks".format(team_key)].append({"ticker": tk, "type": "특수" if is_special_checked else "일반"})
                    st.cache_data.clear(); st.session_state[add_key] = False; st.rerun()
                elif tk: st.warning("{} 는 이미 등록된 종목입니다.".format(tk))
        with ac3:
            if st.button("✖  취소", key="cancel_{}".format(team_key), use_container_width=True):
                st.session_state[add_key] = False; st.rerun()
    return summary_rows

# ─────────────────────────────────────────
# 섹션 렌더
# ─────────────────────────────────────────
st.markdown("### 🛡 백팀 (White Team) — 돈을 지켜줄 안전 금고")
white_rows = render_team("white", "백팀 (안전금고)", target_white_budget, "#2563eb", "🛡")
st.divider()

st.markdown("### 🚀 청팀 (Blue Team) — 돈을 불려줄 세포분열 공간")
blue_rows = render_team("blue", "청팀 (세포분열)", target_blue_budget, "#10b981", "🚀")
st.divider()

# ─────────────────────────────────────────
# 종합 테이블 렌더링
# ─────────────────────────────────────────
st.markdown("### 📊 전체 포트폴리오 집행 현황 요약표")
all_rows = white_rows + blue_rows

if all_rows:
    STAGE_STYLE = {"1단계": ("🔵", "#1d4ed8", "#dbeafe", "#bfdbfe"), "2단계": ("🟢", "#065f46", "#d1fae5", "#a7f3d0"), "3단계": ("🟡", "#92400e", "#fef3c7", "#fde68a"), "4단계": ("🔴", "#991b1b", "#fee2e2", "#fecaca")}
    def drop_color(val_str):
        try:
            d = float(val_str.replace("%", ""))
            if d >= 50: return "#dc2626"
            if d >= 35: return "#d97706"
            if d >= 20: return "#2563eb"
        except: pass
        return "#475569"

    rows_html = ""
    for i, r in enumerate(all_rows):
        row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        stage_val = r["단계"]
        badge_html = "<span style='display:inline-block;padding:4px 10px;border-radius:20px;background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;font-weight:700;font-size:0.78rem;'>⏳ 대기 중</span>"
        for key, (emoji, fg, bg, border) in STAGE_STYLE.items():
            if key in stage_val:
                badge_html = "<span style='display:inline-block;padding:4px 10px;border-radius:20px;background:{bg};color:{fg};border:1.5px solid {border};font-weight:800;font-size:0.78rem;white-space:nowrap;'>{emoji} {label}</span>".format(bg=bg, fg=fg, border=border, emoji=emoji, label=stage_val)
                break

        dc = drop_color(r["적용 하락률"])
        buy_val = r["1회 분할매수(USD)"]; buy_krw = r["1회 분할매수(KRW)"]
        buy_style = "font-weight:800;color:#0f172a;" if buy_val != "—" else "color:#94a3b8;"
        krw_style = "font-weight:700;color:#334155;" if buy_krw != "—" else "color:#94a3b8;"
        team_badge = "<span style='color:#2563eb;font-weight:700;'>🛡 백팀</span>" if "백팀" in r["팀"] else "<span style='color:#059669;font-weight:700;'>🚀 청팀</span>"

        rows_html += (
            "<tr style='background:{bg};'>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;'>{team}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:900;color:#0f172a;font-size:0.95rem;'>{ticker}</td>"
            "<td style='padding:11px 14px;text-align:left;border-bottom:1px solid #f1f5f9;color:#334155;font-size:0.85rem;'>{name}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:700;color:#0f172a;'>{cur}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;color:#475569;'>{ath}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:700;color:{dc};'>{drop}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;'>{stage}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;{bs}'>{buy}</td>"
            "<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;{ks}'>{krw}</td>"
            "</tr>"
        ).format(bg=row_bg, team=team_badge, ticker=r["티커"], name=r["종목명"], cur=r["현재가"], ath=r["ATH"], dc=dc, drop=r["적용 하락률"], stage=badge_html, bs=buy_style, buy=buy_val, ks=krw_style, krw=buy_krw)

    table_html = """
    <div style='background:white;border-radius:20px;border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.06);margin-bottom:16px;'>
    <table style='width:100%;border-collapse:collapse;font-family:Noto Sans KR,sans-serif;'>
      <thead>
        <tr style='background:#1e293b;'>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>팀</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>티커</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:left;'>종목명</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>현재가</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>ATH</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>적용 하락률</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>매수 단계</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>1회 권장(USD)</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>1회 권장(KRW)</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    </div>
    """.format(rows=rows_html)

    st.markdown(table_html, unsafe_allow_html=True)
