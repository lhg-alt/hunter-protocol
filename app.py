"""
HUNTER PROTOCOL — 재민의 자동 저점 매수 계산기
Streamlit + yfinance | 비밀번호 보호 + 인라인 종목 추가/삭제
HTML 렌더링 버그 완전 수정 버전
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
    page_title="HUNTER PROTOCOL",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }

    .stApp {
        background: linear-gradient(145deg, #eef2ff 0%, #f8fafc 50%, #ecfdf5 100%) !important;
    }

    /* 전체 텍스트 기본 다크 */
    p, div, span, label, h1, h2, h3, h4, h5, li, td, th {
        color: #1e293b !important;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
    [data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: #f1f5f9 !important;
        border-radius: 10px !important;
    }

    /* 메트릭 카드 */
    [data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }
    [data-testid="stMetricLabel"] p { color: #64748b !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 900 !important; }
    [data-testid="stMetricDelta"] { color: #059669 !important; }

    /* 버튼 기본 */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        border: 1.5px solid #e2e8f0 !important;
        color: #334155 !important;
        background: white !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        border-color: #94a3b8 !important;
        background: #f8fafc !important;
        color: #0f172a !important;
    }
    /* primary 버튼 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        color: white !important;
    }

    /* 삭제 버튼 전용 (빨간 테마) */
    .del-btn > button {
        background: #fef2f2 !important;
        border: 1.5px solid #fca5a5 !important;
        color: #dc2626 !important;
        border-radius: 10px !important;
        font-size: 0.8rem !important;
        padding: 4px 8px !important;
    }
    .del-btn > button:hover {
        background: #fee2e2 !important;
        border-color: #f87171 !important;
        color: #b91c1c !important;
    }

    /* 추가 버튼 전용 */
    .add-btn > button {
        background: #f0fdf4 !important;
        border: 2px dashed #86efac !important;
        color: #16a34a !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }
    .add-btn > button:hover {
        background: #dcfce7 !important;
        border-color: #4ade80 !important;
        color: #15803d !important;
    }

    /* expander */
    div[data-testid="stExpander"] {
        background: white !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* text input */
    .stTextInput input {
        color: #1e293b !important;
        background: white !important;
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    /* 테이블 */
    .stDataFrame { border-radius: 16px !important; overflow: hidden !important; }
    .stDataFrame table { border-collapse: separate !important; border-spacing: 0 !important; }
    .stDataFrame thead tr th {
        background: #1e293b !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px 16px !important;
        font-size: 0.85rem !important;
    }
    .stDataFrame tbody tr:nth-child(even) td { background: #f8fafc !important; }
    .stDataFrame tbody tr:hover td { background: #eff6ff !important; }
    .stDataFrame tbody tr td {
        color: #1e293b !important;
        font-size: 0.88rem !important;
        padding: 10px 16px !important;
    }

    /* alerts */
    .stAlert { border-radius: 14px !important; }
    .stAlert p { color: #1e293b !important; }

    /* 헤더 */
    .hunter-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 700;
        font-size: 2rem;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
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
    <div style="max-width:400px;margin:80px auto;background:white;border-radius:24px;
    padding:48px 40px;box-shadow:0 8px 40px rgba(0,0,0,0.12);border:1px solid #e2e8f0;text-align:center;">
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
# 매수 원칙
# ─────────────────────────────────────────
STAGES = [
    {"stage": 1, "label": "1단계: 정찰병 배치", "hunter_msg": "적의 움직임 포착 — 소량 선제 진입",
     "drop_threshold": 20, "pct": 0.15, "color": "#2563eb", "bg": "#eff6ff", "emoji": "🔵"},
    {"stage": 2, "label": "2단계: 부대 전진",   "hunter_msg": "전장 확인 — 본격 포지션 구축",
     "drop_threshold": 35, "pct": 0.25, "color": "#059669", "bg": "#f0fdf4", "emoji": "🟢"},
    {"stage": 3, "label": "3단계: 주력군 투입", "hunter_msg": "전면전 개시 — 핵심 물량 확보",
     "drop_threshold": 50, "pct": 0.35, "color": "#d97706", "bg": "#fffbeb", "emoji": "🟡"},
    {"stage": 4, "label": "4단계: 총력전 대비", "hunter_msg": "항복 신호 포착 — 전 자본 집결 준비",
     "drop_threshold": 60, "pct": 0.25, "color": "#dc2626", "bg": "#fef2f2", "emoji": "🔴"},
]

# ─────────────────────────────────────────
# 세션 상태
# ─────────────────────────────────────────
if "white_tickers" not in st.session_state:
    st.session_state.white_tickers = ["NEE", "CEG", "WEC", "SO"]
if "blue_tickers" not in st.session_state:
    st.session_state.blue_tickers = ["CRWD", "PLTR", "NVDA", "META"]
if "show_add_white" not in st.session_state:
    st.session_state.show_add_white = False
if "show_add_blue" not in st.session_state:
    st.session_state.show_add_blue = False

# ─────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        if current is None and not hist.empty:
            current = float(hist["Close"].iloc[-1])
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
    if drop_pct < 20:
        return None
    for s in reversed(STAGES[:3]):
        if drop_pct >= s["drop_threshold"]:
            return s
    return STAGES[0]


def fmt_usd(v):
    return "${:,.0f}".format(v)

def fmt_krw(v):
    return "₩{:,.0f}".format(v)


# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.caption("재민의 폭락장 자동 사냥기")
    st.divider()
    st.markdown("#### 💰 포트폴리오 설정")
    total_seed    = st.number_input("전체 시드 (USD $)", min_value=1000, max_value=10_000_000, value=100_000, step=1000, format="%d")
    exchange_rate = st.number_input("환율 (USD→KRW)",    min_value=1000, max_value=2000,        value=1380,   step=10)
    white_ratio   = st.slider("화이트 팀 비중 (%)", 0, 100, 50, 5)
    blue_ratio    = 100 - white_ratio
    st.caption(f"블루 팀: {blue_ratio}%")
    st.divider()
    if st.button("🔄  데이터 새로고침", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.success("캐시 초기화 완료!")
        time.sleep(0.4)
        st.rerun()
    if st.button("🚪  로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.caption(f"업데이트: {datetime.now().strftime('%H:%M:%S')}")

white_budget = total_seed * (white_ratio / 100)
blue_budget  = total_seed * (blue_ratio  / 100)

# ─────────────────────────────────────────
# 메인 헤더
# ─────────────────────────────────────────
hc1, hc2 = st.columns([3, 1])
with hc1:
    st.markdown('<p class="hunter-title">🎯 HUNTER PROTOCOL</p>', unsafe_allow_html=True)
    st.markdown("재민의 자동 저점 매수 계산기 — **폭락은 두려움이 아니라 기회다**")
with hc2:
    st.metric("전체 시드", fmt_usd(total_seed))
st.divider()

st.markdown("### ⚡ 포트폴리오 요약")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🛡 화이트 예산", fmt_usd(white_budget), f"{white_ratio}%")
m2.metric("🚀 블루 예산",   fmt_usd(blue_budget),  f"{blue_ratio}%")
m3.metric("💱 원화 환산",   fmt_krw(total_seed * exchange_rate))
m4.metric("📌 총 종목 수",  f"{len(st.session_state.white_tickers) + len(st.session_state.blue_tickers)}개")
st.divider()

# 단계 가이드
with st.expander("📖 매수 단계 가이드 (클릭하여 펼치기)", expanded=False):
    g1, g2, g3, g4 = st.columns(4)
    for gcol, s in zip([g1, g2, g3, g4], STAGES):
        with gcol:
            lbl = "집행 {}%".format(int(s['pct']*100)) if s['stage'] < 4 else "보유 {}%".format(int(s['pct']*100))
            st.markdown(
                "<div style='background:{bg};border:1.5px solid {c}55;border-radius:14px;"
                "padding:14px;text-align:center;'>"
                "<div style='font-size:1.4rem'>{emoji}</div>"
                "<div style='font-weight:900;color:{c};font-size:0.85rem;margin-top:4px'>{label}</div>"
                "<div style='color:#475569;font-size:0.75rem;margin-top:4px'>ATH -{th}% 이상</div>"
                "<div style='font-weight:900;color:{c};font-size:1.1rem;margin-top:6px'>{lbl}</div>"
                "<div style='color:#64748b;font-size:0.7rem;margin-top:2px'>{msg}</div>"
                "</div>".format(
                    bg=s['bg'], c=s['color'], emoji=s['emoji'],
                    label=s['label'], th=s['drop_threshold'],
                    lbl=lbl, msg=s['hunter_msg']
                ), unsafe_allow_html=True)
st.divider()


# ─────────────────────────────────────────
# 종목 카드 렌더 (HTML 없이 Streamlit 네이티브)
# ─────────────────────────────────────────
def render_stock_card(ticker, data, stage, drop, buy_usd, buy_krw, eq_w, team_color, team_key):
    current = data["current"]
    ath     = data["ath"]

    # 카드 배경색 결정
    bg_map = {"#2563eb": "#eff6ff", "#059669": "#f0fdf4", "#d97706": "#fffbeb", "#dc2626": "#fef2f2"}
    card_bg = stage["bg"] if stage else "#f8fafc"

    with st.container():
        # ── 배지 + 헤더 행 ──
        badge_cols = st.columns([1, 1])
        with badge_cols[0]:
            if stage:
                st.markdown(
                    "<span style='display:inline-block;padding:4px 12px;border-radius:20px;"
                    "font-weight:700;font-size:0.78rem;"
                    "background:{bg};color:{c};border:1.5px solid {c}66;'>"
                    "{emoji} {label}</span>".format(
                        bg=stage['bg'], c=stage['color'],
                        emoji=stage['emoji'], label=stage['label']
                    ), unsafe_allow_html=True)
            elif drop is not None:
                st.markdown(
                    "<span style='display:inline-block;padding:4px 12px;border-radius:20px;"
                    "font-weight:700;font-size:0.78rem;"
                    "background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'>"
                    "⏳ 사냥터 접근 전</span>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<span style='display:inline-block;padding:4px 12px;border-radius:20px;"
                    "font-weight:700;font-size:0.78rem;"
                    "background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;'>"
                    "— 데이터 없음</span>", unsafe_allow_html=True)

        # ── 가격 정보 ──
        info_c1, info_c2 = st.columns(2)
        with info_c1:
            drop_str  = "-{:.1f}%".format(drop) if drop is not None else "—"
            drop_color = stage["color"] if stage else "#94a3b8"
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;"
                "border:1.5px solid {border};box-shadow:0 2px 8px rgba(0,0,0,0.04);'>"
                "<div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>"
                "<div style='min-width:40px;height:40px;border-radius:10px;background:{tc};"
                "display:flex;align-items:center;justify-content:center;"
                "color:white;font-weight:900;font-size:0.72rem;'>{tick}</div>"
                "<div>"
                "<div style='font-weight:900;color:#0f172a;font-size:1rem;'>{ticker}</div>"
                "<div style='color:#64748b;font-size:0.75rem;'>{name}</div>"
                "</div>"
                "</div>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-end;'>"
                "<div>"
                "<div style='color:#64748b;font-size:0.7rem;'>현재가</div>"
                "<div style='font-weight:900;color:#0f172a;font-size:1.15rem;'>{cur}</div>"
                "</div>"
                "<div style='text-align:right;'>"
                "<div style='color:#64748b;font-size:0.7rem;'>ATH 대비</div>"
                "<div style='font-weight:900;color:{dc};font-size:1.15rem;'>{ds}</div>"
                "</div>"
                "</div>"
                "</div>".format(
                    border=(stage["color"] + "44") if stage else "#e2e8f0",
                    tc=team_color,
                    tick=ticker[:4], ticker=ticker,
                    name=data['name'][:22],
                    cur="${:,.2f}".format(current) if current else "—",
                    dc=drop_color, ds=drop_str
                ), unsafe_allow_html=True)

        with info_c2:
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;"
                "border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.04);height:100%;'>"
                "<div style='color:#64748b;font-size:0.7rem;margin-bottom:4px;'>52주 ATH</div>"
                "<div style='font-weight:900;color:#0f172a;font-size:1rem;margin-bottom:10px;'>{ath}</div>"
                "<div style='color:#64748b;font-size:0.7rem;margin-bottom:4px;'>팀 내 비중</div>"
                "<div style='font-weight:700;color:#0f172a;font-size:1rem;'>{w:.1f}%</div>"
                "</div>".format(
                    ath="${:,.2f}".format(ath) if ath else "—",
                    w=eq_w
                ), unsafe_allow_html=True)

        # ── 매수 금액 블록 ──
        if stage and stage["stage"] < 4 and buy_usd > 0:
            st.markdown(
                "<div style='background:white;border-radius:14px;padding:14px 16px;"
                "border:2px solid {c}44;margin-top:6px;'>"
                "<div style='color:#64748b;font-size:0.72rem;margin-bottom:4px;'>🎯 이 단계 추천 매수 금액</div>"
                "<div style='font-weight:900;color:{c};font-size:1.3rem;'>{usd}</div>"
                "<div style='color:#475569;font-size:0.85rem;margin-top:2px;'>{krw}</div>"
                "<div style='color:#94a3b8;font-size:0.72rem;margin-top:6px;"
                "padding-top:6px;border-top:1px solid #f1f5f9;'>{msg}</div>"
                "</div>".format(
                    c=stage['color'],
                    usd="${:,.0f}".format(buy_usd),
                    krw="≈ ₩{:,.0f}".format(buy_krw),
                    msg=stage['hunter_msg']
                ), unsafe_allow_html=True)
        elif drop is not None and drop < 20:
            st.info("ATH 대비 {:.1f}% 하락 — 20% 초과 시 1단계 진입".format(drop), icon="⏳")

        # ── 삭제 버튼 ──
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        del_c1, del_c2 = st.columns([4, 1])
        with del_c2:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("🗑 삭제", key="del_{}_{}".format(team_key, ticker), use_container_width=True):
                st.session_state["{}_tickers".format(team_key)].remove(ticker)
                st.cache_data.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 팀 렌더 함수
# ─────────────────────────────────────────
def render_team(team_key, team_label, team_budget, team_color, team_emoji):
    tickers = st.session_state["{}_tickers".format(team_key)]
    eq_w    = 100 / len(tickers) if tickers else 0
    is_white = team_key == "white"
    grad = ("linear-gradient(135deg,#eff6ff,#dbeafe)"
            if is_white else "linear-gradient(135deg,#f0fdf4,#dcfce7)")

    # 팀 헤더
    st.markdown(
        "<div style='border-radius:20px;padding:18px 24px;margin-bottom:16px;"
        "background:{grad};border:2px solid {c}33;'>"
        "<span style='font-size:1.4rem'>{emoji}</span>"
        "<span style='font-weight:900;color:{c};font-size:1.15rem;margin-left:8px;'>{label}</span>"
        "<span style='color:#475569;font-size:0.88rem;margin-left:12px;'>"
        "예산: <strong style='color:#0f172a;'>{budget}</strong>&nbsp;(≈ {krw})</span>"
        "</div>".format(
            grad=grad, c=team_color, emoji=team_emoji, label=team_label,
            budget="${:,.0f}".format(team_budget),
            krw="₩{:,.0f}".format(team_budget * exchange_rate)
        ), unsafe_allow_html=True)

    summary_rows = []

    # 2열 그리드
    for i in range(0, max(len(tickers), 1), 2):
        batch = tickers[i:i+2]
        if not batch:
            break
        cols = st.columns(len(batch))

        for col, ticker in zip(cols, batch):
            with col:
                data = fetch_stock_data(ticker)

                if not data["success"]:
                    st.error("❌ {} 로드 실패".format(ticker))
                    if st.button("🗑 {} 삭제".format(ticker), key="del_err_{}_{}".format(team_key, ticker)):
                        st.session_state["{}_tickers".format(team_key)].remove(ticker)
                        st.rerun()
                    continue

                current = data["current"]
                ath     = data["ath"]
                drop    = ((ath - current) / ath * 100) if (current and ath) else None
                stage   = get_stage(drop) if drop is not None else None
                buy_usd = team_budget * (eq_w / 100) * stage["pct"] if (stage and stage["stage"] < 4) else 0
                buy_krw = buy_usd * exchange_rate

                render_stock_card(ticker, data, stage, drop, buy_usd, buy_krw, eq_w, team_color, team_key)

                summary_rows.append({
                    "팀":       "🛡 화이트" if is_white else "🚀 블루",
                    "티커":     ticker,
                    "종목명":   data["name"][:18],
                    "현재가":   "${:,.2f}".format(current) if current else "—",
                    "ATH":      "${:,.2f}".format(ath)     if ath     else "—",
                    "하락률":   "{:.1f}%".format(drop)     if drop is not None else "—",
                    "단계":     stage["label"]             if stage           else "대기 중",
                    "매수(USD)":"${:,.0f}".format(buy_usd) if buy_usd > 0     else "—",
                    "매수(KRW)":"₩{:,.0f}".format(buy_krw) if buy_usd > 0    else "—",
                })

    # ── 종목 추가 UI ──
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    add_key = "show_add_{}".format(team_key)

    if not st.session_state[add_key]:
        st.markdown('<div class="add-btn">', unsafe_allow_html=True)
        if st.button("➕  {} 종목 추가".format(team_emoji), key="open_{}".format(team_key), use_container_width=True):
            st.session_state[add_key] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='background:white;border-radius:16px;padding:16px 20px;"
            "border:2px dashed {c}88;margin-bottom:8px;'>"
            "<span style='font-weight:700;color:{c};font-size:0.95rem;'>"
            "{emoji} 새 종목 티커 입력</span>"
            "</div>".format(c=team_color, emoji=team_emoji),
            unsafe_allow_html=True)

        ac1, ac2, ac3 = st.columns([3, 1, 1])
        with ac1:
            new_tk = st.text_input(
                "티커", placeholder="예: TSLA, AMZN...",
                key="inp_{}".format(team_key),
                label_visibility="collapsed")
        with ac2:
            if st.button("✅  추가", key="confirm_{}".format(team_key),
                         type="primary", use_container_width=True):
                tk = new_tk.strip().upper()
                if tk and tk not in st.session_state["{}_tickers".format(team_key)]:
                    st.session_state["{}_tickers".format(team_key)].append(tk)
                    st.cache_data.clear()
                    st.session_state[add_key] = False
                    st.rerun()
                elif tk:
                    st.warning("{} 는 이미 등록된 종목입니다.".format(tk))
        with ac3:
            if st.button("✖  취소", key="cancel_{}".format(team_key), use_container_width=True):
                st.session_state[add_key] = False
                st.rerun()

    return summary_rows


# ─────────────────────────────────────────
# 팀 섹션 렌더
# ─────────────────────────────────────────
st.markdown("### 🛡 화이트 팀 (White Team) — 방어 / 배당")
with st.spinner("화이트 팀 데이터 로딩 중..."):
    white_rows = render_team("white", "화이트 팀", white_budget, "#2563eb", "🛡")

st.divider()

st.markdown("### 🚀 블루 팀 (Blue Team) — 성장 / 미래")
with st.spinner("블루 팀 데이터 로딩 중..."):
    blue_rows = render_team("blue", "블루 팀", blue_budget, "#10b981", "🚀")

st.divider()

# ─────────────────────────────────────────
# 종합 테이블
# ─────────────────────────────────────────
st.markdown("### 📊 전체 포트폴리오 집행 현황")
all_rows = white_rows + blue_rows

if all_rows:
    df = pd.DataFrame(all_rows)

    def style_row(row):
        styles = [""] * len(row)
        stage_idx = df.columns.get_loc("단계")
        v = str(row.iloc[stage_idx])
        if   "1단계" in v: color, bg = "#1d4ed8", "#dbeafe"
        elif "2단계" in v: color, bg = "#065f46", "#d1fae5"
        elif "3단계" in v: color, bg = "#92400e", "#fef3c7"
        elif "4단계" in v: color, bg = "#991b1b", "#fee2e2"
        else:               color, bg = "#334155", "#f8fafc"
        base = "color:{};background-color:{};".format(color, bg)
        styles[stage_idx] = "font-weight:800;" + base
        # 하락률 색상
        drop_idx = df.columns.get_loc("하락률")
        d_val = str(row.iloc[drop_idx]).replace("%","")
        try:
            d = float(d_val)
            if   d >= 50: styles[drop_idx] = "color:#dc2626;font-weight:700;"
            elif d >= 35: styles[drop_idx] = "color:#d97706;font-weight:700;"
            elif d >= 20: styles[drop_idx] = "color:#2563eb;font-weight:700;"
        except: pass
        return styles

    styled = (df.style
              .apply(style_row, axis=1)
              .set_properties(**{"color": "#1e293b", "font-size": "0.88rem"})
              .set_table_styles([
                  {"selector": "thead th",
                   "props": [("background-color","#1e293b"),("color","white"),
                              ("font-weight","700"),("font-size","0.85rem"),
                              ("padding","12px 16px"),("text-align","center")]},
                  {"selector": "tbody td",
                   "props": [("padding","10px 16px"),("text-align","center"),
                              ("border-bottom","1px solid #f1f5f9")]},
                  {"selector": "tbody tr:hover td",
                   "props": [("background-color","#f0f9ff !important")]},
              ]))

    st.dataframe(styled, use_container_width=True, hide_index=True)

    active = [r for r in all_rows if r["매수(USD)"] != "—"]
    if active:
        total_usd = sum(
            float(r["매수(USD)"].replace("$","").replace(",",""))
            for r in active
        )
        st.success(
            "✅ **{}개 종목 매수 구간 진입** | "
            "총 집행 금액: **{}** (≈ {})".format(
                len(active),
                "${:,.0f}".format(total_usd),
                "₩{:,.0f}".format(total_usd * exchange_rate)
            ))
    else:
        st.info("⏳ 현재 매수 구간 종목 없음 — 사냥감을 기다리는 중...")

# ─────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;padding:16px 0;'>"
    "<span style='color:#94a3b8;font-size:0.78rem;'>"
    "<strong style='color:#475569;'>HUNTER PROTOCOL</strong>"
    " — 폭락은 두려움이 아니라 기회다<br>"
    "📌 yfinance 52주 기준 | 투자는 본인 책임"
    "</span></div>",
    unsafe_allow_html=True)
