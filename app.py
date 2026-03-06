"""
HUNTER PROTOCOL v9.1 — 윌리엄 이평선(MA) 저점 매수 법칙 적용 (오류 수정 완벽판)
Streamlit + yfinance | MA 200/240/365 자동 계산 + 3-Way 트리거 스위치
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
    page_title="HUNTER PROTOCOL | 부의 대이동",
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

    /* 라디오 버튼 커스텀 */
    div.row-widget.stRadio > div { background: white; padding: 10px 20px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; gap: 20px; flex-wrap: wrap; }
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
# 매수 원칙 구성 (ATH/지수 vs 이평선 모드)
# ─────────────────────────────────────────
# 기본 룰 (ATH 또는 시장 지수 하락률 기준)
STAGES_BASE = [
    {"stage": 1, "label": "1차 매수 (20%↓)", "hunter_msg": "최근 고점 대비 약 20% 하락 시", "drop_threshold": 20, "pct": 0.15, "color": "#2563eb", "bg": "#eff6ff", "emoji": "🔵"},
    {"stage": 2, "label": "2차 매수 (30%↓)",   "hunter_msg": "약 30% 이상 추가 하락 시", "drop_threshold": 30, "pct": 0.25, "color": "#059669", "bg": "#f0fdf4", "emoji": "🟢"},
    {"stage": 3, "label": "3차 매수 (패닉장)", "hunter_msg": "시장 전체 패닉 / 극단적 공포", "drop_threshold": 40, "pct": 0.35, "color": "#d97706", "bg": "#fffbeb", "emoji": "🟡"},
    {"stage": 4, "label": "유동성 대기", "hunter_msg": "전대미문의 시스템 위기 현금 보루", "drop_threshold": 60, "pct": 0.25, "color": "#dc2626", "bg": "#fef2f2", "emoji": "🔴"},
]

# 이평선(MA) 전용 룰
STAGES_MA = [
    {"stage": 1, "label": "1차 (MA 200)", "hunter_msg": "장기 추세선 도달 (기관 테스팅)", "pct": 0.20, "color": "#2563eb", "bg": "#eff6ff", "emoji": "🔵"},
    {"stage": 2, "label": "2차 (MA 240)", "hunter_msg": "연간 평균단가 붕괴 (본격 매집)", "pct": 0.25, "color": "#059669", "bg": "#f0fdf4", "emoji": "🟢"},
    {"stage": 3, "label": "3차 (MA 365)", "hunter_msg": "심리적 마지노선 (Capitulation)", "pct": 0.30, "color": "#d97706", "bg": "#fffbeb", "emoji": "🟡"},
    {"stage": 4, "label": "유동성 대기", "hunter_msg": "극단적 추가 하락 대비 탄약 보존", "pct": 0.25, "color": "#dc2626", "bg": "#fef2f2", "emoji": "🔴"},
]

# ─────────────────────────────────────────
# 세션 상태
# ─────────────────────────────────────────
if "white_stocks" not in st.session_state:
    st.session_state.white_stocks = [
        {"ticker": "GLD", "type": "안전자산"}, {"ticker": "TLT", "type": "안전자산"}, 
        {"ticker": "NEE", "type": "일반"}, {"ticker": "CEG", "type": "일반"}
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
        # 이평선(MA365)을 위해 2년(약 500 거래일) 데이터 호출
        hist = t.history(period="2y")
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        if current is None and not hist.empty: current = float(hist["Close"].iloc[-1])
        ath_52w = float(hist["High"][-252:].max()) if len(hist) >= 252 else (float(hist["High"].max()) if not hist.empty else None)
        ath = info.get("fiftyTwoWeekHigh") or ath_52w
        name = info.get("shortName") or info.get("longName") or ticker
        
        # 이동평균선 계산
        ma200 = float(hist["Close"].rolling(200).mean().iloc[-1]) if len(hist) >= 200 else None
        ma240 = float(hist["Close"].rolling(240).mean().iloc[-1]) if len(hist) >= 240 else None
        ma365 = float(hist["Close"].rolling(365).mean().iloc[-1]) if len(hist) >= 365 else None

        return {
            "ticker": ticker.upper(), "name": name,
            "current": round(float(current), 2) if current else None,
            "ath":     round(float(ath),     2) if ath     else None,
            "ma200":   round(ma200, 2) if ma200 else None,
            "ma240":   round(ma240, 2) if ma240 else None,
            "ma365":   round(ma365, 2) if ma365 else None,
            "success": True,
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "success": False, "error": str(e)}

def get_base_stage(drop_pct):
    if drop_pct < 20: return None
    for s in reversed(STAGES_BASE[:3]):
        if drop_pct >= s["drop_threshold"]: return s
    return STAGES_BASE[0]

def get_ma_stage(current, ma200, ma240, ma365):
    if ma365 and current <= ma365: return STAGES_MA[2]
    if ma240 and current <= ma240: return STAGES_MA[1]
    if ma200 and current <= ma200: return STAGES_MA[0]
    return None

def fmt_usd(v): return "${:,.0f}".format(v)
def fmt_krw(v): return "₩{:,.0f}".format(v)

# ─────────────────────────────────────────
# 사이드바 (투입 시드 및 현금 설정)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.caption("거대 자본의 흐름을 읽는 어군탐지기")
    st.divider()
    
    st.markdown("#### 💰 투자 목표(Target) 세팅")
    total_seed    = st.number_input("전체 가용 시드 (USD $)", min_value=1000, max_value=10_000_000, value=100_000, step=1000, format="%d", help="시장에 최종적으로 투입할 백팀/청팀 전체 금액")
    extra_cash    = st.number_input("여유 현금 보유액 (USD $)", min_value=0, max_value=10_000_000, value=30_000, step=1000, format="%d", help="투자와 별개로 보유 중인 최후의 보루 (비상금)")
    exchange_rate = st.number_input("환율 (USD→KRW)", min_value=1000, max_value=2000, value=1380, step=10)
    
    st.divider()
    st.markdown("##### ⚖️ 주식 시드 목표 비중 (%)")
    white_ratio = st.slider("🛡 백팀(안전금고) 목표 비중", 0, 100, 50, 5)
    blue_ratio  = 100 - white_ratio
    
    if white_ratio == 50:
        st.success(f"✅ 완벽한 50:50 황금 밸런스 유지중")
    else:
        st.warning(f"💡 백팀 금고 해제 (리밸런싱) 모드 활성화\n(현재 백 {white_ratio} : 청 {blue_ratio})\n폭락장 평단 낮추기 전용")
        
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
# 메인 헤더 및 폭락장 멘탈 케어 요약
# ─────────────────────────────────────────
hc1, hc2 = st.columns([3, 1])
with hc1:
    st.markdown('<p class="hunter-title">🎯 HUNTER PROTOCOL</p>', unsafe_allow_html=True)
    st.markdown("재민의 퀀트 대시보드 — **폭락장의 본질은 부의 대이동이다!**")
with hc2:
    st.metric("총 자산 (시드 + 현금)", fmt_usd(total_seed + extra_cash))

with st.expander("🚨 폭락장 절대 원칙 & 분미프 매뉴얼 (클릭하여 숙지)", expanded=False):
    st.markdown("""
    - **절대 금지:** 가격 급락 시 공포 매도, 자극적인 뉴스 맹신, 주변 패닉 동조 금지. 물건을 돈으로 사듯, 돈은 소중히 머무는 손님이다.
    - **3년 보유 철칙:** 최소 3년은 보유하는 습관을 들여라. 단타로는 큰 부를 만들 수 없다.
    ---
    1. **자산은 평생 백팀과 청팀 50:50 유지:** 백팀은 돈을 지켜줄 안전금고, 청팀은 돈을 불려줄 역노화 세포분열 공간.
    2. **백팀(금고) 5~7개 제한 룰:** 자신이 감당하고 기억 가능한 5~7개 이내의 금고(국채/달러 등 포함)만 유지하라.
    3. **궁극의 리밸런싱:** 하락장에서 청팀 예산 전소 시, 백팀 금고를 헐어 다시 5:5 밸런스를 맞추고 1군을 추가 매수.
    4. **이동평균선(MA) 활용:** 200일선(장기추세), 240일선(연간 평균/기관매집), 365일선(마지노선) 기준으로 상어를 탐지하라.
    5. **10분할 분할매수 절대 원칙:** 저점 도달 시마다 해당 기업 예산의 1/10씩, **주 1회 원칙**으로 최소 3개월간 기계적 매수.
    """)
st.divider()

# ─────────────────────────────────────────
# 거시 경제 레이더 및 트리거 전환 (3-WAY 스위치)
# ─────────────────────────────────────────
macro_data = fetch_macro_data()
market_max_drop = 0
if macro_data["success"]:
    spy_drop = macro_data["SPY"]["drop"]
    vix_val = macro_data["VIX"]["current"]
    market_max_drop = spy_drop
    
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
        f"<div style='color:{'#dc2626' if vix_val>=40 else ('#d97706' if vix_val>=25 else '#059669')};font-weight:700;font-size:1rem;margin-top:4px;'>{'극단적 공포 수준' if vix_val>=40 else ('불안 수준' if vix_val>=25 else '안정 수준')}</div>"
        f"</div>", unsafe_allow_html=True
    )

st.markdown("<br>### 🎛️ 사냥 기준(Trigger) 모드 선택", unsafe_allow_html=True)
trigger_mode = st.radio(
    "매수 단계를 판별할 기준 지표를 선택하세요:",
    ["종목별 전고점 (ATH) 기준", "시장 지수 (S&P 500) 기준", "이동평균선 (MA 200/240/365) 기준"],
    horizontal=True,
    label_visibility="collapsed"
)
is_index_mode = "S&P 500" in trigger_mode
is_ma_mode = "MA" in trigger_mode
active_stages = STAGES_MA if is_ma_mode else STAGES_BASE

if is_index_mode:
    st.info(f"💡 **S&P 500 지수 기준** 모드: 개별 종목과 무관하게, 시장 지수 하락률(-{market_max_drop:.1f}%)을 기준으로 모든 포트폴리오에 일괄 매수 단계가 적용됩니다.", icon="📊")
elif is_ma_mode:
    st.info("💡 **이동평균선 (MA) 기준** 모드: 윌리엄 법칙에 따라 200일선(20%), 240일선(25%), 365일선(30%) 돌파를 기준으로 거대 자본의 흐름을 쫓습니다.", icon="📈")
else:
    st.success("💡 **개별 종목 전고점 기준** 모드: 각 종목의 52주 전고점 대비 하락률에 따라 개별적으로 매수 단계가 계산됩니다.", icon="🎯")

st.divider()

# ─────────────────────────────────────────
# 백그라운드 데이터 사전 계산 (Current Status 파악용)
# ─────────────────────────────────────────
target_white_budget = total_seed * (white_ratio / 100)
target_blue_budget  = total_seed * (blue_ratio  / 100)

allocations = {"white": {}, "blue": {}}
stock_cache = {}

def process_team_data(team_stocks, team_budget, team_type):
    invested = 0
    if not team_stocks: return 0
    
    # 30% 룰 적용 (백팀:안전자산, 청팀:특수)
    special_key = "안전자산" if team_type == "white" else "특수"
    special_stocks = [s for s in team_stocks if s.get("type") == special_key]
    normal_stocks  = [s for s in team_stocks if s.get("type") != special_key]
    
    sp_total_w = 30 if special_stocks and normal_stocks else (100 if special_stocks else 0)
    nm_total_w = 70 if special_stocks and normal_stocks else (100 if normal_stocks else 0)
    
    for s in special_stocks:
        tk = s["ticker"]; w = sp_total_w / len(special_stocks)
        allocations[team_type][tk] = {"weight": w, "budget": team_budget * (w / 100)}
    for s in normal_stocks:
        tk = s["ticker"]; w = nm_total_w / len(normal_stocks)
        allocations[team_type][tk] = {"weight": w, "budget": team_budget * (w / 100)}
        
    for s in team_stocks:
        tk = s["ticker"]
        data = fetch_stock_data(tk)
        stock_cache[tk] = data
        if data["success"] and data["current"]:
            if is_ma_mode:
                stage = get_ma_stage(data["current"], data["ma200"], data["ma240"], data["ma365"])
            else:
                ath = data["ath"]
                if ath:
                    stock_drop = ((ath - data["current"]) / ath * 100)
                    effective_drop = market_max_drop if is_index_mode else stock_drop
                    stage = get_base_stage(effective_drop)
                else: stage = None
                
            if stage and stage["stage"] < 4:
                invested += allocations[team_type][tk]["budget"] * stage["pct"]
    return invested

current_white_invested = process_team_data(st.session_state.white_stocks, target_white_budget, "white")
current_blue_invested = process_team_data(st.session_state.blue_stocks, target_blue_budget, "blue")
current_total_invested = current_white_invested + current_blue_invested
current_cash_remaining = total_seed - current_total_invested

# 현금 건전성 로직
total_assets = total_seed + extra_cash
total_actual_cash = current_cash_remaining + extra_cash
cash_ratio_pct = (total_actual_cash / total_assets) * 100 if total_assets > 0 else 0

cash_status_msg = "🟢 정상 (안정적인 20~30% 확보)"
cash_status_color = "#059669"
if cash_ratio_pct >= 40:
    cash_status_msg = "🔵 위기 대비 완벽 (과열/위기장 40~50% 이상)"
    cash_status_color = "#2563eb"
elif cash_ratio_pct < 20:
    cash_status_msg = "🔴 현금 부족 (20% 미만, 리스크 주의)"
    cash_status_color = "#dc2626"

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
    cur_w_pct = (current_white_invested / total_assets) * 100 if total_assets > 0 else 0
    cur_b_pct = (current_blue_invested / total_assets) * 100 if total_assets > 0 else 0
    
    st.markdown(
        f"<div style='background:white;border-radius:20px;padding:24px;border:2px solid {cash_status_color};box-shadow:0 4px 12px rgba(0,0,0,0.15);height:100%;'>"
        f"<div style='color:#1e293b;font-weight:900;font-size:1.1rem;margin-bottom:4px;'>📊 현재 집행 상태 및 현금 건전성</div>"
        f"<div style='color:{cash_status_color};font-weight:800;font-size:0.85rem;margin-bottom:16px;'>{cash_status_msg}</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
        f"<div><span style='color:#2563eb;font-weight:800;'>🛡 집행된 백팀</span> <span style='font-weight:700;'>{cur_w_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(current_white_invested)}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
        f"<div><span style='color:#10b981;font-weight:800;'>🚀 집행된 청팀</span> <span style='font-weight:700;'>{cur_b_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(current_blue_invested)}</div>"
        f"</div>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:16px;'>"
        f"<div><span style='color:#64748b;font-weight:800;'>🏦 총 보유 현금 (미집행+여유분)</span> <span style='font-weight:700;'>{cash_ratio_pct:.1f}%</span></div>"
        f"<div style='font-weight:800;color:#0f172a;'>{fmt_usd(total_actual_cash)}</div>"
        f"</div>"
        f"<div style='width:100%;height:12px;border-radius:6px;display:flex;overflow:hidden;background:#e2e8f0;'>"
        f"<div style='width:{cur_w_pct}%;background:#3b82f6;'></div>"
        f"<div style='width:{cur_b_pct}%;background:#10b981;'></div>"
        f"<div style='width:{cash_ratio_pct}%;background:#cbd5e1;'></div>"
        f"</div>"
        f"</div>", unsafe_allow_html=True
    )

st.divider()

# ─────────────────────────────────────────
# 종목 카드 렌더 함수 
# ─────────────────────────────────────────
def render_stock_card(ticker, data, stage, effective_val, alloc_budget, alloc_w, team_color, team_key, special_type=None):
    current = data["current"]
    
    # 10분할 매수 로직
    split_10_usd = alloc_budget / 10
    split_10_krw = split_10_usd * exchange_rate

    with st.container():
        badge_cols = st.columns([1, 1])
        with badge_cols[0]:
            if stage:
                st.markdown(
                    "<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:{bg};color:{c};border:1.5px solid {c}66;'>{emoji} {label}</span>".format(bg=stage['bg'], c=stage['color'], emoji=stage['emoji'], label=stage['label']), unsafe_allow_html=True)
            elif effective_val is not None:
                st.markdown("<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'>⏳ 사냥터 접근 전</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='display:inline-block;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.78rem;background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;'>— 데이터 부족</span>", unsafe_allow_html=True)

        info_c1, info_c2 = st.columns(2)
        with info_c1:
            # MA 모드일 때는 이평선 정보를, ATH 모드일 때는 하락률을 표기
            if is_ma_mode:
                ma200 = f"${data['ma200']:.1f}" if data['ma200'] else "N/A"
                ma240 = f"${data['ma240']:.1f}" if data['ma240'] else "N/A"
                ma365 = f"${data['ma365']:.1f}" if data['ma365'] else "N/A"
                disp_label = "핵심 이평선 (200/240/365)"
                disp_val = f"<span style='font-size:0.85rem;color:#64748b;'>{ma200} | {ma240} | {ma365}</span>"
            else:
                stock_drop = ((data["ath"] - current) / data["ath"] * 100) if current and data["ath"] else None
                drop_str = f"-{stock_drop:.1f}%" if stock_drop is not None else "—"
                drop_color = "#dc2626" if (stock_drop is not None and stock_drop >= 20) else "#059669"
                disp_label = "실제 종목 하락률"
                disp_val = f"<span style='color:{drop_color};'>{drop_str}</span>"

            border_color = (stage["color"] + "44") if stage else "#e2e8f0"
            st.markdown(
                f"<div style='background:white;border-radius:14px;padding:14px 16px;border:1.5px solid {border_color};box-shadow:0 2px 8px rgba(0,0,0,0.04);'>"
                f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>"
                f"<div style='min-width:40px;height:40px;border-radius:10px;background:{team_color};display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:0.72rem;'>{ticker[:4]}</div>"
                f"<div><div style='font-weight:900;color:#0f172a;font-size:1rem;'>{ticker}</div>"
                f"<div style='color:#64748b;font-size:0.75rem;'>{data['name'][:22]}</div></div></div>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-end;'>"
                f"<div><div style='color:#64748b;font-size:0.7rem;'>현재가</div>"
                f"<div style='font-weight:900;color:#0f172a;font-size:1.15rem;'>${current:.2f}</div></div>"
                f"<div style='text-align:right;'><div style='color:#64748b;font-size:0.7rem;'>{disp_label}</div>"
                f"<div style='font-weight:900;font-size:1.15rem;'>{disp_val}</div></div></div></div>", unsafe_allow_html=True)

        with info_c2:
            special_badge = ""
            if special_type == "안전자산":
                special_badge = "<div style='display:inline-block; padding:2px 6px; background:#e0e7ff; color:#4f46e5; border-radius:4px; font-size:0.65rem; margin-bottom:4px; font-weight:700;'>✨ 안전자산 헷지 (백팀 30% 할당)</div><br>"
            elif special_type == "특수":
                special_badge = "<div style='display:inline-block; padding:2px 6px; background:#e0e7ff; color:#4f46e5; border-radius:4px; font-size:0.65rem; margin-bottom:4px; font-weight:700;'>✨ 1군 전략 섹터 (청팀 30% 할당)</div><br>"
            
            ath_str = f"${data['ath']:.2f}" if data['ath'] else "—"
            st.markdown(
                f"<div style='background:white;border-radius:14px;padding:14px 16px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);height:100%;'>"
                f"{special_badge}"
                f"<div style='color:#64748b;font-size:0.7rem;margin-bottom:2px;'>팀 내 목표 비중 (이 종목 총 예산)</div>"
                f"<div style='font-weight:900;color:#0f172a;font-size:1rem;margin-bottom:10px;'>{alloc_w:.1f}% <span style='font-size:0.8rem;color:#64748b;font-weight:400;'>(${alloc_budget:,.0f})</span></div>"
                f"<div style='color:#64748b;font-size:0.7rem;margin-bottom:2px;'>52주 ATH</div>"
                f"<div style='font-weight:700;color:#0f172a;font-size:1rem;'>{ath_str}</div></div>", unsafe_allow_html=True)

        if stage and stage["stage"] < 4:
            if is_ma_mode: basis_text = "이동평균선 (MA) 도달"
            elif is_index_mode: basis_text = "S&P 500 시장 지수 하락분"
            else: basis_text = "개별 종목 고점 하락분"
            
            st.markdown(
                f"<div style='background:white;border-radius:14px;padding:14px 16px;border:2px solid {stage['color']}44;margin-top:8px;'>"
                f"<div style='color:#64748b;font-size:0.72rem;margin-bottom:4px;'>🔥 <b>{basis_text} 반영</b> | 10분할 중 1회 권장 매수액</div>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<div><div style='font-weight:900;color:{stage['color']};font-size:1.3rem;'>${split_10_usd:,.0f}</div>"
                f"<div style='color:#475569;font-size:0.85rem;margin-top:2px;'>≈ ₩{split_10_krw:,.0f}</div></div>"
                f"<div style='text-align:right; font-size:0.75rem; color:#64748b; background:#f1f5f9; padding:6px 10px; border-radius:8px;'><b>기계적 매수: 주 1회 원칙</b><br>최소 3개월 분할</div>"
                f"</div></div>", unsafe_allow_html=True)
        elif effective_val is not None:
            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
            if is_ma_mode: st.info("현재 가격이 200일 이동평균선 위에 있습니다. (관망)", icon="⏳")
            else: st.info(f"현재 적용 하락률 {effective_val:.1f}% — 20% 초과 시 매수 개시", icon="⏳")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        del_c1, del_c2 = st.columns([4, 1])
        with del_c2:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("🗑 삭제", key=f"del_{team_key}_{ticker}", use_container_width=True):
                st.session_state[f"{team_key}_stocks"] = [s for s in st.session_state[f"{team_key}_stocks"] if s["ticker"] != ticker]
                st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

def render_team(team_key, team_label, team_budget, team_color, team_emoji):
    stocks = st.session_state[f"{team_key}_stocks"]
    is_white = team_key == "white"
    grad = ("linear-gradient(135deg,#eff6ff,#dbeafe)" if is_white else "linear-gradient(135deg,#f0fdf4,#dcfce7)")

    # 🚨 백팀 갯수 통제 경고
    if is_white:
        if len(stocks) > 7: st.error("🚨 [매뉴얼 위반] 백팀(금고) 종목 수가 7개를 초과했습니다! 관리 가능한 5~7개 이내로 통제하지 않으면 물 새는 바가지가 됩니다.")
        elif len(stocks) >= 5 and len(stocks) <= 7: st.success("✅ [매뉴얼 준수] 완벽합니다. 금고의 수가 5~7개로 안전하게 관리되고 있습니다.")
        elif len(stocks) > 0 and len(stocks) < 5: st.info("💡 [매뉴얼 권장] 백팀 금고는 5~7개로 구성하는 것이 리스크 분산에 가장 이상적입니다.")

    st.markdown(
        f"<div style='border-radius:20px;padding:18px 24px;margin-bottom:16px;background:{grad};border:2px solid {team_color}33;'>"
        f"<span style='font-size:1.4rem'>{team_emoji}</span><span style='font-weight:900;color:{team_color};font-size:1.15rem;margin-left:8px;'>{team_label}</span>"
        f"<span style='color:#475569;font-size:0.88rem;margin-left:12px;'>목표 예산: <strong style='color:#0f172a;'>${team_budget:,.0f}</strong>&nbsp;(≈ ₩{team_budget * exchange_rate:,.0f})</span>"
        f"</div>", unsafe_allow_html=True)

    summary_rows = []
    for i in range(0, max(len(stocks), 1), 2):
        batch = stocks[i:i+2]
        if not batch: break
        cols = st.columns(len(batch))

        for col, stock_dict in zip(cols, batch):
            ticker = stock_dict["ticker"]
            sp_type = stock_dict.get("type")
            alloc_data = allocations[team_key][ticker]
            data = stock_cache.get(ticker, {"success": False})
            
            with col:
                if not data["success"]:
                    st.error(f"❌ {ticker} 로드 실패")
                    continue
                current = data["current"]
                
                # 스테이지 판별 로직 적용
                if is_ma_mode:
                    stage = get_ma_stage(current, data["ma200"], data["ma240"], data["ma365"])
                    effective_val = current  # None 에러 방지용 임시값
                    disp_val = "MA 도달" if stage else "관망"
                else:
                    ath = data["ath"]
                    stock_drop = ((ath - current) / ath * 100) if (current and ath) else None
                    effective_val = market_max_drop if is_index_mode else stock_drop
                    stage = get_base_stage(effective_val) if effective_val is not None else None
                    disp_val = f"-{effective_val:.1f}%" if effective_val is not None else "—"
                
                buy_usd_1_split = alloc_data["budget"] / 10 if (stage and stage["stage"] < 4) else 0
                buy_krw_1_split = buy_usd_1_split * exchange_rate

                # 인자 9개(special_type까지) 완벽히 맞춰 호출
                render_stock_card(ticker, data, stage, effective_val, alloc_data["budget"], alloc_data["weight"], team_color, team_key, sp_type)

                summary_rows.append({
                    "팀": "🛡 백팀" if is_white else "🚀 청팀", "티커": ticker, "종목명": data["name"][:18],
                    "현재가": f"${current:.2f}" if current else "—", 
                    "적용 기준": disp_val, "단계": stage["label"] if stage else "대기 중",
                    "1회 분할매수(USD)": f"${buy_usd_1_split:,.0f}" if buy_usd_1_split > 0 else "—", 
                    "1회 분할매수(KRW)": f"₩{buy_krw_1_split:,.0f}" if buy_usd_1_split > 0 else "—",
                })

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    add_key = f"show_add_{team_key}"
    if not st.session_state[add_key]:
        st.markdown('<div class="add-btn">', unsafe_allow_html=True)
        if st.button(f"➕  {team_emoji} 종목 추가", key=f"open_{team_key}", use_container_width=True):
            st.session_state[add_key] = True; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:white;border-radius:16px;padding:16px 20px;border:2px dashed {team_color}88;margin-bottom:8px;'><span style='font-weight:700;color:{team_color};font-size:0.95rem;'>{team_emoji} 새 종목 티커 입력</span></div>", unsafe_allow_html=True)
        ac1, ac2, ac3 = st.columns([3, 1, 1])
        with ac1:
            new_tk = st.text_input("티커", placeholder="예: TSLA, AMZN, TLT...", key=f"inp_{team_key}", label_visibility="collapsed")
            is_special_checked = st.checkbox("✨ 안전자산 (국채/금 등)" if is_white else "✨ 1군 전략 섹터 (양자/장수/우주)", key=f"chk_sp_{team_key}")
        with ac2:
            if st.button("✅  추가", key=f"confirm_{team_key}", type="primary", use_container_width=True):
                tk = new_tk.strip().upper()
                existing = [s["ticker"] for s in st.session_state[f"{team_key}_stocks"]]
                if tk and tk not in existing:
                    added_type = "일반"
                    if is_special_checked: added_type = "안전자산" if is_white else "특수"
                    st.session_state[f"{team_key}_stocks"].append({"ticker": tk, "type": added_type})
                    st.cache_data.clear(); st.session_state[add_key] = False; st.rerun()
                elif tk: st.warning(f"{tk} 는 이미 등록된 종목입니다.")
        with ac3:
            if st.button("✖  취소", key=f"cancel_{team_key}", use_container_width=True):
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
    def drop_color(val_str):
        if "MA" in val_str: return "#1d4ed8"
        try:
            d = float(val_str.replace("%", "").replace("-", ""))
            if d >= 50: return "#dc2626"
            if d >= 35: return "#d97706"
            if d >= 20: return "#2563eb"
        except: pass
        return "#475569"

    rows_html = ""
    for i, r in enumerate(all_rows):
        row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        
        # 통합 스테이지 배지 처리
        stage_val = r["단계"]
        badge_html = "<span style='display:inline-block;padding:4px 10px;border-radius:20px;background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;font-weight:700;font-size:0.78rem;'>⏳ 대기 중</span>"
        for stage_dict_list in [STAGES_BASE, STAGES_MA]:
            for s_info in stage_dict_list:
                if s_info["label"] == stage_val:
                    badge_html = f"<span style='display:inline-block;padding:4px 10px;border-radius:20px;background:{s_info['bg']};color:{s_info['color']};border:1.5px solid {s_info['color']}66;font-weight:800;font-size:0.78rem;white-space:nowrap;'>{s_info['emoji']} {stage_val}</span>"
                    break

        dc = drop_color(r["적용 기준"])
        buy_val = r["1회 분할매수(USD)"]; buy_krw = r["1회 분할매수(KRW)"]
        buy_style = "font-weight:800;color:#0f172a;" if buy_val != "—" else "color:#94a3b8;"
        krw_style = "font-weight:700;color:#334155;" if buy_krw != "—" else "color:#94a3b8;"
        team_badge = "<span style='color:#2563eb;font-weight:700;'>🛡 백팀</span>" if "백팀" in r["팀"] else "<span style='color:#059669;font-weight:700;'>🚀 청팀</span>"

        rows_html += (
            f"<tr style='background:{row_bg};'>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;'>{team_badge}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:900;color:#0f172a;font-size:0.95rem;'>{r['티커']}</td>"
            f"<td style='padding:11px 14px;text-align:left;border-bottom:1px solid #f1f5f9;color:#334155;font-size:0.85rem;'>{r['종목명']}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:700;color:#0f172a;'>{r['현재가']}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;font-weight:700;color:{dc};'>{r['적용 기준']}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;'>{badge_html}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;{buy_style}'>{buy_val}</td>"
            f"<td style='padding:11px 14px;text-align:center;border-bottom:1px solid #f1f5f9;{krw_style}'>{buy_krw}</td>"
            f"</tr>"
        )

    table_html = f"""
    <div style='background:white;border-radius:20px;border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.06);margin-bottom:16px;'>
    <table style='width:100%;border-collapse:collapse;font-family:Noto Sans KR,sans-serif;'>
      <thead>
        <tr style='background:#1e293b;'>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>팀</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>티커</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:left;'>종목명</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>현재가</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>적용 기준</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>매수 단계</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>1회 권장(USD)</th>
          <th style='padding:13px 14px;color:white;font-weight:700;font-size:0.82rem;text-align:center;'>1회 권장(KRW)</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)
