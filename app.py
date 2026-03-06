"""
HUNTER PROTOCOL — 재민의 자동 저점 매수 계산기
Streamlit + yfinance | 비밀번호 보호 + 인라인 종목 추가/삭제
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
# CSS — 흰 배경 + 명확한 글자색
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    /* 앱 배경 */
    .stApp {
        background: linear-gradient(145deg, #eef2ff 0%, #f8fafc 50%, #ecfdf5 100%) !important;
    }
    /* 모든 텍스트 기본 색 강제 */
    p, div, span, label, h1, h2, h3, h4, h5, li {
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
    /* 버튼 */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        color: #1e293b !important;
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
    /* dataframe */
    .stDataFrame { border-radius: 16px !important; }
    /* info / success / warning */
    .stAlert { border-radius: 14px !important; }
    .stAlert p { color: #1e293b !important; }
    /* 카드 공통 */
    .scard {
        background: white;
        border-radius: 18px;
        padding: 18px;
        border: 1.5px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .scard-label { color: #64748b; font-size: 0.7rem; margin-bottom: 2px; }
    .scard-value { color: #0f172a; font-weight: 700; font-size: 0.95rem; }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
        margin-bottom: 10px;
    }
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
    .team-hdr {
        border-radius: 20px;
        padding: 18px 24px;
        margin-bottom: 16px;
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
      <div style="color:#64748b;font-size:0.9rem;margin:10px 0 28px;">재민의 폭락장 저점 매수 시스템</div>
    </div>
    """, unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        pw = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
        if st.button("🔓 입장하기", use_container_width=True, type="primary"):
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
    {"stage": 2, "label": "2단계: 부대 전진", "hunter_msg": "전장 확인 — 본격 포지션 구축",
     "drop_threshold": 35, "pct": 0.25, "color": "#059669", "bg": "#f0fdf4", "emoji": "🟢"},
    {"stage": 3, "label": "3단계: 주력군 투입", "hunter_msg": "전면전 개시 — 핵심 물량 확보",
     "drop_threshold": 50, "pct": 0.35, "color": "#d97706", "bg": "#fffbeb", "emoji": "🟡"},
    {"stage": 4, "label": "4단계: 총력전 대비", "hunter_msg": "항복 신호 포착 — 전 자본 집결 준비",
     "drop_threshold": 60, "pct": 0.25, "color": "#dc2626", "bg": "#fef2f2", "emoji": "🔴"},
]

# ─────────────────────────────────────────
# 세션 상태 초기화
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
# 유틸 함수
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
            "ath": round(float(ath), 2) if ath else None,
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


def calc_buy(budget, weight_pct, stage):
    return budget * (weight_pct / 100) * stage["pct"]


# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.markdown("<span style='color:#94a3b8!important;font-size:0.85rem'>재민의 폭락장 자동 사냥기</span>", unsafe_allow_html=True)
    st.divider()
    st.markdown("#### 💰 포트폴리오 설정")
    total_seed = st.number_input("전체 시드 (USD $)", min_value=1000, max_value=10_000_000, value=100_000, step=1000, format="%d")
    exchange_rate = st.number_input("환율 (USD→KRW)", min_value=1000, max_value=2000, value=1380, step=10)
    white_ratio = st.slider("화이트 팀 비중 (%)", 0, 100, 50, 5)
    blue_ratio = 100 - white_ratio
    st.caption(f"블루 팀: {blue_ratio}%")
    st.divider()
    if st.button("🔄 데이터 새로고침", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.success("캐시 초기화!")
        time.sleep(0.4)
        st.rerun()
    if st.button("🚪 로그아웃", use_container_width=True):
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
    st.markdown('<div class="hunter-title">🎯 HUNTER PROTOCOL</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#475569;font-size:0.95rem;'>재민의 자동 저점 매수 계산기 — 폭락은 두려움이 아니라 기회다</p>", unsafe_allow_html=True)
with hc2:
    st.metric("전체 시드", f"${total_seed:,.0f}")
st.divider()

# 요약 지표
st.markdown("### ⚡ 포트폴리오 요약")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🛡 화이트 예산", f"${white_budget:,.0f}", f"{white_ratio}%")
m2.metric("🚀 블루 예산", f"${blue_budget:,.0f}", f"{blue_ratio}%")
m3.metric("💱 원화 환산", f"₩{total_seed * exchange_rate:,.0f}")
m4.metric("📌 총 종목 수", f"{len(st.session_state.white_tickers) + len(st.session_state.blue_tickers)}개")
st.divider()

# 단계 가이드
with st.expander("📖 매수 단계 가이드 (클릭하여 펼치기)", expanded=False):
    g1, g2, g3, g4 = st.columns(4)
    for gcol, s in zip([g1, g2, g3, g4], STAGES):
        with gcol:
            lbl = f"집행 {int(s['pct']*100)}%" if s['stage'] < 4 else f"보유 {int(s['pct']*100)}%"
            st.markdown(
                f"""<div style="background:{s['bg']};border:1.5px solid {s['color']}55;border-radius:14px;padding:14px;text-align:center;">
                <div style="font-size:1.4rem">{s['emoji']}</div>
                <div style="font-weight:900;color:{s['color']};font-size:0.85rem;margin-top:4px">{s['label']}</div>
                <div style="color:#475569;font-size:0.75rem;margin-top:4px">ATH -{s['drop_threshold']}% 이상</div>
                <div style="font-weight:900;color:{s['color']};font-size:1.1rem;margin-top:6px">{lbl}</div>
                <div style="color:#64748b;font-size:0.7rem;margin-top:2px">{s['hunter_msg']}</div>
                </div>""", unsafe_allow_html=True)
st.divider()


# ─────────────────────────────────────────
# 팀 렌더 함수
# ─────────────────────────────────────────
def render_team(team_key, team_label, team_budget, team_color, team_emoji):
    tickers = st.session_state[f"{team_key}_tickers"]
    eq_w = 100 / len(tickers) if tickers else 0
    is_white = team_key == "white"
    grad = "linear-gradient(135deg,#eff6ff,#dbeafe)" if is_white else "linear-gradient(135deg,#f0fdf4,#dcfce7)"

    st.markdown(
        f"""<div class="team-hdr" style="background:{grad};border:2px solid {team_color}33;">
        <span style="font-size:1.4rem">{team_emoji}</span>
        <span style="font-weight:900;color:{team_color};font-size:1.15rem;margin-left:8px">{team_label}</span>
        <span style="color:#475569;font-size:0.88rem;margin-left:12px">예산:
        <strong style="color:#0f172a">${team_budget:,.0f}</strong>
        &nbsp;(≈ ₩{team_budget * exchange_rate:,.0f})</span>
        </div>""", unsafe_allow_html=True)

    summary_rows = []

    for i in range(0, max(len(tickers), 1), 2):
        batch = tickers[i:i+2]
        cols = st.columns(len(batch)) if batch else []

        for col, ticker in zip(cols, batch):
            with col:
                data = fetch_stock_data(ticker)

                if not data["success"]:
                    st.error(f"❌ {ticker} 로드 실패")
                    if st.button(f"🗑 {ticker} 삭제", key=f"del_err_{team_key}_{ticker}"):
                        st.session_state[f"{team_key}_tickers"].remove(ticker)
                        st.rerun()
                    continue

                current = data["current"]
                ath = data["ath"]
                drop = ((ath - current) / ath * 100) if (current and ath) else None
                stage = get_stage(drop) if drop is not None else None
                buy_usd = calc_buy(team_budget, eq_w, stage) if (stage and stage["stage"] < 4) else 0
                buy_krw = buy_usd * exchange_rate

                c_border = (stage["color"] + "55") if stage else "#e2e8f0"
                c_bg = stage["bg"] if stage else "#f8fafc"
                drop_str = f"-{drop:.1f}%" if drop is not None else "—"
                drop_clr = stage["color"] if stage else "#94a3b8"

                if stage:
                    badge = f'<span class="badge" style="background:{stage["bg"]};color:{stage["color"]};border:1.5px solid {stage["color"]}44;">{stage["emoji"]} {stage["label"]}</span>'
                elif drop is not None:
                    badge = '<span class="badge" style="background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;">⏳ 사냥터 접근 전</span>'
                else:
                    badge = '<span class="badge" style="background:#f1f5f9;color:#64748b;border:1px solid #e2e8f0;">— 데이터 없음</span>'

                if stage and stage["stage"] < 4 and buy_usd > 0:
                    buy_block = f"""
                    <div style="background:white;border-radius:12px;padding:12px;border:2px solid {stage['color']}33;margin-top:10px;">
                      <div style="color:#64748b;font-size:0.7rem;margin-bottom:3px;">🎯 이 단계 추천 매수 금액</div>
                      <div style="font-weight:900;color:{stage['color']};font-size:1.2rem;">${buy_usd:,.0f}</div>
                      <div style="color:#475569;font-size:0.8rem;">≈ ₩{buy_krw:,.0f}</div>
                      <div style="color:#94a3b8;font-size:0.7rem;margin-top:4px;">{stage['hunter_msg']}</div>
                    </div>"""
                elif drop is not None:
                    wait = f"ATH 대비 {drop:.1f}% 하락 — 20% 초과 시 1단계 진입" if drop < 20 else "상태 확인 중..."
                    buy_block = f'<div style="color:#64748b;font-size:0.8rem;padding:8px 0;">{wait}</div>'
                else:
                    buy_block = '<div style="color:#94a3b8;font-size:0.8rem;padding:8px 0;">가격 데이터 없음</div>'

                st.markdown(
                    f"""<div class="scard" style="border-color:{c_border};background:{c_bg};">
                    {badge}
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                      <div style="min-width:42px;height:42px;border-radius:12px;background:{team_color};
                      display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:0.72rem;">{ticker[:4]}</div>
                      <div style="flex:1;min-width:0;">
                        <div style="font-weight:900;color:#0f172a;font-size:0.98rem;">{ticker}</div>
                        <div style="color:#64748b;font-size:0.75rem;">{data['name'][:26]}</div>
                      </div>
                      <div style="text-align:right;">
                        <div style="font-weight:900;color:#0f172a;font-size:1.05rem;">${current:,.2f}</div>
                        <div style="font-weight:700;color:{drop_clr};font-size:0.85rem;">{drop_str}</div>
                      </div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                      <div style="background:white;border-radius:10px;padding:8px 10px;border:1px solid #e2e8f0;">
                        <div class="scard-label">52주 ATH</div>
                        <div class="scard-value">${f'{ath:,.2f}' if ath else '—'}</div>
                      </div>
                      <div style="background:white;border-radius:10px;padding:8px 10px;border:1px solid #e2e8f0;">
                        <div class="scard-label">팀 내 비중</div>
                        <div class="scard-value">{eq_w:.1f}%</div>
                      </div>
                    </div>
                    {buy_block}
                    </div>""", unsafe_allow_html=True)

                # 삭제 버튼
                _, del_col = st.columns([5, 1])
                with del_col:
                    if st.button("🗑 삭제", key=f"del_{team_key}_{ticker}", use_container_width=True):
                        st.session_state[f"{team_key}_tickers"].remove(ticker)
                        st.cache_data.clear()
                        st.rerun()

                summary_rows.append({
                    "팀": "🛡 화이트" if is_white else "🚀 블루",
                    "티커": ticker,
                    "종목명": data["name"][:18],
                    "현재가($)": f"${current:,.2f}" if current else "—",
                    "ATH($)": f"${ath:,.2f}" if ath else "—",
                    "하락률": f"{drop:.1f}%" if drop is not None else "—",
                    "단계": stage["label"] if stage else "대기",
                    "매수($)": f"${buy_usd:,.0f}" if buy_usd > 0 else "—",
                    "매수(₩)": f"₩{buy_krw:,.0f}" if buy_usd > 0 else "—",
                })

    # ── 종목 추가 UI ──
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    add_key = f"show_add_{team_key}"

    if not st.session_state[add_key]:
        if st.button(f"➕ {team_label}에 종목 추가", key=f"open_{team_key}", use_container_width=True):
            st.session_state[add_key] = True
            st.rerun()
    else:
        st.markdown(
            f"""<div style="background:white;border-radius:16px;padding:16px 20px;
            border:2px dashed {team_color}77;margin-bottom:8px;">
            <div style="font-weight:700;color:{team_color};font-size:0.95rem;margin-bottom:8px;">
            {team_emoji} 새 종목 추가</div>
            </div>""", unsafe_allow_html=True)

        ac1, ac2, ac3 = st.columns([3, 1, 1])
        with ac1:
            new_tk = st.text_input("티커", placeholder="예: TSLA, AMZN...", key=f"inp_{team_key}", label_visibility="collapsed")
        with ac2:
            if st.button("✅ 추가", key=f"confirm_{team_key}", type="primary", use_container_width=True):
                tk = new_tk.strip().upper()
                if tk and tk not in st.session_state[f"{team_key}_tickers"]:
                    st.session_state[f"{team_key}_tickers"].append(tk)
                    st.cache_data.clear()
                    st.session_state[add_key] = False
                    st.rerun()
                elif tk:
                    st.warning(f"{tk} 이미 존재")
        with ac3:
            if st.button("❌ 취소", key=f"cancel_{team_key}", use_container_width=True):
                st.session_state[add_key] = False
                st.rerun()

    return summary_rows


# ─────────────────────────────────────────
# 화이트 팀
# ─────────────────────────────────────────
st.markdown("### 🛡 화이트 팀 (White Team) — 방어 / 배당")
with st.spinner("화이트 팀 로딩 중..."):
    white_rows = render_team("white", "화이트 팀", white_budget, "#2563eb", "🛡")

st.divider()

# ─────────────────────────────────────────
# 블루 팀
# ─────────────────────────────────────────
st.markdown("### 🚀 블루 팀 (Blue Team) — 성장 / 미래")
with st.spinner("블루 팀 로딩 중..."):
    blue_rows = render_team("blue", "블루 팀", blue_budget, "#10b981", "🚀")

st.divider()

# ─────────────────────────────────────────
# 종합 테이블
# ─────────────────────────────────────────
st.markdown("### 📊 전체 포트폴리오 집행 현황")
all_rows = white_rows + blue_rows

if all_rows:
    df = pd.DataFrame(all_rows)

    def hl(val):
        v = str(val)
        if "1단계" in v: return "background-color:#eff6ff;color:#2563eb;font-weight:bold"
        if "2단계" in v: return "background-color:#f0fdf4;color:#059669;font-weight:bold"
        if "3단계" in v: return "background-color:#fffbeb;color:#d97706;font-weight:bold"
        if "4단계" in v: return "background-color:#fef2f2;color:#dc2626;font-weight:bold"
        return "color:#1e293b"

    st.dataframe(df.style.applymap(hl, subset=["단계"]), use_container_width=True, hide_index=True)

    active = [r for r in all_rows if r["매수($)"] != "—"]
    if active:
        total_usd = sum(float(r["매수($)"].replace("$","").replace(",","")) for r in active)
        st.success(f"✅ **{len(active)}개 종목 매수 구간 진입** | 총 집행 금액: **${total_usd:,.0f}** (≈ ₩{total_usd * exchange_rate:,.0f})")
    else:
        st.info("⏳ 현재 매수 구간 종목 없음 — 사냥감을 기다리는 중...")

# ─────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────
st.divider()
st.markdown(
    """<div style="text-align:center;padding:16px 0;">
    <span style="color:#94a3b8;font-size:0.78rem;">
    <strong style="color:#475569;">HUNTER PROTOCOL</strong> — 폭락은 두려움이 아니라 기회다<br>
    📌 yfinance 52주 기준 | 투자는 본인 책임
    </span></div>""", unsafe_allow_html=True)
