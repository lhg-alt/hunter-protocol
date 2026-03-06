"""
HUNTER PROTOCOL — 재민의 자동 저점 매수 계산기
Streamlit + yfinance 기반 자동 데이터 연동 버전
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
    page_title="HUNTER PROTOCOL — 저점 매수 계산기",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# 커스텀 CSS (밝은 테마 + Hunter 스타일)
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background: linear-gradient(145deg, #f0f4ff 0%, #fafafa 50%, #f0fdf4 100%);
    }
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #f8fafc !important; }
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    /* 메트릭 카드 */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid rgba(0,0,0,0.07);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    /* 버튼 */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s !important;
    }
    /* 커스텀 카드 */
    .stock-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    .stock-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.10); }
    .stage-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.78rem;
        margin-bottom: 6px;
    }
    .team-header {
        border-radius: 20px;
        padding: 20px 24px;
        margin-bottom: 20px;
        font-weight: 900;
    }
    .hunter-title {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 700;
        font-size: 1.8rem;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    .summary-table th {
        background: #1e293b !important;
        color: white !important;
    }
    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 매수 원칙 설정 (재민님 버전)
# ─────────────────────────────────────────
STAGES = [
    {
        "stage": 1,
        "label": "1단계: 정찰병 배치",
        "hunter_msg": "적의 움직임 포착 — 소량 선제 진입",
        "drop_threshold": 20,
        "pct": 0.15,
        "color": "#2563eb",
        "bg": "#eff6ff",
        "emoji": "🔵",
    },
    {
        "stage": 2,
        "label": "2단계: 부대 전진",
        "hunter_msg": "전장 확인 — 본격 포지션 구축",
        "drop_threshold": 35,
        "pct": 0.25,
        "color": "#059669",
        "bg": "#f0fdf4",
        "emoji": "🟢",
    },
    {
        "stage": 3,
        "label": "3단계: 주력군 투입",
        "hunter_msg": "전면전 개시 — 핵심 물량 확보",
        "drop_threshold": 50,
        "pct": 0.35,
        "color": "#d97706",
        "bg": "#fffbeb",
        "emoji": "🟡",
    },
    {
        "stage": 4,
        "label": "4단계: 총력전 / 지수 폭락 대비",
        "hunter_msg": "항복 신호 포착 — 전 자본 집결 준비",
        "drop_threshold": 60,
        "pct": 0.25,  # 보유 현금 (집행 아님)
        "color": "#dc2626",
        "bg": "#fef2f2",
        "emoji": "🔴",
    },
]

# ─────────────────────────────────────────
# 기본 종목 데이터
# ─────────────────────────────────────────
DEFAULT_WHITE = ["NEE", "CEG", "WEC", "SO"]
DEFAULT_BLUE  = ["CRWD", "PLTR", "NVDA", "META"]

# ─────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────
if "white_tickers" not in st.session_state:
    st.session_state.white_tickers = DEFAULT_WHITE.copy()
if "blue_tickers" not in st.session_state:
    st.session_state.blue_tickers = DEFAULT_BLUE.copy()
if "cache" not in st.session_state:
    st.session_state.cache = {}

# ─────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────
@st.cache_data(ttl=300)  # 5분 캐시
def fetch_stock_data(ticker: str):
    """yfinance로 현재가 + 52주 최고가 가져오기"""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")

        current = info.get("currentPrice") or info.get("regularMarketPrice")
        if current is None and not hist.empty:
            current = float(hist["Close"].iloc[-1])

        ath_52w = float(hist["High"].max()) if not hist.empty else None
        # 실제 ATH는 info에 있으면 우선 사용
        ath = info.get("fiftyTwoWeekHigh") or ath_52w

        name = info.get("shortName") or info.get("longName") or ticker
        sector = info.get("sector", "N/A")
        currency = info.get("currency", "USD")

        return {
            "ticker": ticker.upper(),
            "name": name,
            "sector": sector,
            "current": round(float(current), 2) if current else None,
            "ath": round(float(ath), 2) if ath else None,
            "currency": currency,
            "success": True,
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "success": False, "error": str(e)}


def get_stage(drop_pct: float):
    """하락률 → 단계 판별"""
    if drop_pct < 20:
        return None
    for s in reversed(STAGES[:3]):  # 3→2→1 순으로 체크 (가장 심한 단계 우선)
        if drop_pct >= s["drop_threshold"]:
            return s
    return STAGES[0]


def calc_buy_amount(team_budget: float, weight_pct: float, stage: dict) -> float:
    alloc = team_budget * (weight_pct / 100)
    return alloc * stage["pct"]


# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HUNTER PROTOCOL")
    st.markdown("**재민의 폭락장 자동 사냥기**")
    st.divider()

    st.markdown("#### 💰 포트폴리오 설정")
    total_seed = st.number_input(
        "전체 시드 (USD $)",
        min_value=1000,
        max_value=10_000_000,
        value=100_000,
        step=1000,
        format="%d",
    )
    exchange_rate = st.number_input(
        "환율 (USD → KRW)",
        min_value=1000,
        max_value=2000,
        value=1380,
        step=10,
    )
    white_ratio = st.slider("화이트 팀 비중 (%)", 0, 100, 50, 5)
    blue_ratio = 100 - white_ratio
    st.caption(f"블루 팀: {blue_ratio}%")

    st.divider()

    st.markdown("#### 🛡 화이트 팀 종목")
    white_input = st.text_input("티커 추가 (엔터)", placeholder="예: VZ", key="white_add")
    if white_input:
        tk = white_input.strip().upper()
        if tk and tk not in st.session_state.white_tickers:
            st.session_state.white_tickers.append(tk)
            st.rerun()

    white_remove = st.multiselect(
        "제거할 종목",
        st.session_state.white_tickers,
        key="white_rm",
        label_visibility="collapsed",
    )
    if white_remove:
        for t in white_remove:
            if t in st.session_state.white_tickers:
                st.session_state.white_tickers.remove(t)
        st.rerun()
    st.caption(f"현재: {', '.join(st.session_state.white_tickers)}")

    st.divider()

    st.markdown("#### 🚀 블루 팀 종목")
    blue_input = st.text_input("티커 추가 (엔터)", placeholder="예: AMD", key="blue_add")
    if blue_input:
        tk = blue_input.strip().upper()
        if tk and tk not in st.session_state.blue_tickers:
            st.session_state.blue_tickers.append(tk)
            st.rerun()

    blue_remove = st.multiselect(
        "제거할 종목",
        st.session_state.blue_tickers,
        key="blue_rm",
        label_visibility="collapsed",
    )
    if blue_remove:
        for t in blue_remove:
            if t in st.session_state.blue_tickers:
                st.session_state.blue_tickers.remove(t)
        st.rerun()
    st.caption(f"현재: {', '.join(st.session_state.blue_tickers)}")

    st.divider()
    refresh = st.button("🔄 데이터 새로고침", use_container_width=True, type="primary")
    if refresh:
        st.cache_data.clear()
        st.success("캐시 초기화 완료!")
        time.sleep(0.5)
        st.rerun()

    st.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("데이터: yfinance (52주 기준)")

# ─────────────────────────────────────────
# 메인 화면 — 헤더
# ─────────────────────────────────────────
white_budget = total_seed * (white_ratio / 100)
blue_budget  = total_seed * (blue_ratio  / 100)
equal_weight_white = 100 / len(st.session_state.white_tickers) if st.session_state.white_tickers else 0
equal_weight_blue  = 100 / len(st.session_state.blue_tickers)  if st.session_state.blue_tickers  else 0

col_title, col_ts = st.columns([3, 1])
with col_title:
    st.markdown('<div class="hunter-title">🎯 HUNTER PROTOCOL</div>', unsafe_allow_html=True)
    st.markdown("**재민의 자동 저점 매수 계산기** — 폭락은 두려움이 아니라 기회다")
with col_ts:
    st.metric("전체 시드", f"${total_seed:,.0f}")
    st.caption(f"≈ ₩{total_seed * exchange_rate:,.0f}")

st.divider()

# ─────────────────────────────────────────
# 포트폴리오 요약 메트릭
# ─────────────────────────────────────────
st.markdown("### ⚡ 전체 포트폴리오 요약")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🛡 화이트 팀 예산", f"${white_budget:,.0f}", f"{white_ratio}%")
m2.metric("🚀 블루 팀 예산", f"${blue_budget:,.0f}", f"{blue_ratio}%")
m3.metric("환율 적용 총 시드", f"₩{total_seed * exchange_rate:,.0f}")
m4.metric("종목 수", f"{len(st.session_state.white_tickers) + len(st.session_state.blue_tickers)}개")

st.divider()

# ─────────────────────────────────────────
# 단계 가이드 (한 줄)
# ─────────────────────────────────────────
with st.expander("📖 매수 단계 가이드 (클릭하여 펼치기)", expanded=False):
    g1, g2, g3, g4 = st.columns(4)
    for col, s in zip([g1, g2, g3, g4], STAGES):
        with col:
            st.markdown(
                f"""<div style="background:{s['bg']};border:1.5px solid {s['color']}33;
                border-radius:16px;padding:14px;text-align:center;">
                <div style="font-size:1.5rem">{s['emoji']}</div>
                <div style="font-weight:900;color:{s['color']};font-size:0.9rem">{s['label']}</div>
                <div style="color:#64748b;font-size:0.78rem;margin-top:4px">ATH -{s['drop_threshold']}% 이상</div>
                <div style="font-weight:700;color:{s['color']};font-size:1.1rem;margin-top:6px">
                {'집행 ' + str(int(s['pct']*100)) + '%' if s['stage'] < 4 else '보유 ' + str(int(s['pct']*100)) + '%'}</div>
                <div style="color:#94a3b8;font-size:0.72rem;margin-top:2px">{s['hunter_msg']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

st.divider()

# ─────────────────────────────────────────
# 데이터 로딩 & 팀 섹션 렌더링 함수
# ─────────────────────────────────────────
def render_team(team_name: str, tickers: list, team_budget: float, eq_weight: float, color: str, emoji: str):
    st.markdown(
        f"""<div class="team-header" style="background:{'linear-gradient(135deg,#eff6ff,#dbeafe)' if color=='#2563eb' else 'linear-gradient(135deg,#f0fdf4,#dcfce7)'};
        border:2px solid {color}33;">
        <span style="font-size:1.5rem">{emoji}</span>
        <span style="color:{color};font-size:1.2rem;margin-left:8px">{team_name}</span>
        <span style="color:#64748b;font-size:0.9rem;margin-left:12px">예산: ${team_budget:,.0f}
        (≈ ₩{team_budget * exchange_rate:,.0f})</span>
        </div>""",
        unsafe_allow_html=True,
    )

    summary_rows = []

    # 2열 그리드
    cols = st.columns(2)
    for idx, ticker in enumerate(tickers):
        data = fetch_stock_data(ticker)

        with cols[idx % 2]:
            if not data["success"]:
                st.error(f"❌ {ticker} — 데이터 로드 실패: {data.get('error', '')}")
                continue

            current = data["current"]
            ath     = data["ath"]

            if current and ath:
                drop = ((ath - current) / ath) * 100
                stage = get_stage(drop)
            else:
                drop, stage = None, None

            # 매수 금액 계산
            buy_amt_usd = calc_buy_amount(team_budget, eq_weight, stage) if stage and stage["stage"] < 4 else 0
            buy_amt_krw = buy_amt_usd * exchange_rate

            # 단계 표시
            if stage:
                badge_html = f"""<span class="stage-badge" style="background:{stage['bg']};
                color:{stage['color']};border:1.5px solid {stage['color']}44;">
                {stage['emoji']} {stage['label']}</span>"""
                card_border = stage["color"] + "44"
                card_bg = stage["bg"]
            elif drop is not None:
                badge_html = """<span class="stage-badge" style="background:#f1f5f9;color:#94a3b8;border:1px solid #e2e8f0;">
                ⏳ 사냥터 접근 전</span>"""
                card_border = "#e2e8f0"
                card_bg = "#fafafa"
            else:
                badge_html = """<span class="stage-badge" style="background:#f1f5f9;color:#94a3b8;">— 데이터 없음</span>"""
                card_border = "#e2e8f0"
                card_bg = "#fafafa"

            drop_str  = f"-{drop:.1f}%" if drop is not None else "—"
            drop_color = stage["color"] if stage else "#94a3b8"

            st.markdown(
                f"""<div class="stock-card" style="border:1.5px solid {card_border};background:{card_bg};">
                {badge_html}
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                  <div style="width:44px;height:44px;border-radius:12px;background:{color};
                  display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:0.75rem;">
                  {ticker[:4]}</div>
                  <div>
                    <div style="font-weight:900;color:#1e293b;font-size:1rem">{ticker}</div>
                    <div style="color:#64748b;font-size:0.78rem">{data['name'][:28]}</div>
                  </div>
                  <div style="margin-left:auto;text-align:right;">
                    <div style="font-weight:900;color:#1e293b;font-size:1.1rem">${current:,.2f}</div>
                    <div style="font-weight:700;color:{drop_color};font-size:0.85rem">{drop_str}</div>
                  </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
                  <div style="background:white;border-radius:10px;padding:10px;border:1px solid #f1f5f9;">
                    <div style="color:#94a3b8;font-size:0.7rem">52주 최고 (ATH)</div>
                    <div style="font-weight:700;color:#1e293b">${f'{ath:,.2f}' if ath else '—'}</div>
                  </div>
                  <div style="background:white;border-radius:10px;padding:10px;border:1px solid #f1f5f9;">
                    <div style="color:#94a3b8;font-size:0.7rem">팀 내 배분 비중</div>
                    <div style="font-weight:700;color:#1e293b">{eq_weight:.1f}%</div>
                  </div>
                </div>
                {f'''<div style="background:white;border-radius:12px;padding:12px;border:2px solid {stage["color"]}33;">
                  <div style="color:#64748b;font-size:0.72rem">🎯 이 단계 추천 매수 금액</div>
                  <div style="font-weight:900;color:{stage["color"]};font-size:1.25rem">${buy_amt_usd:,.0f}</div>
                  <div style="color:#64748b;font-size:0.78rem">≈ ₩{buy_amt_krw:,.0f}</div>
                  <div style="color:#94a3b8;font-size:0.7rem;margin-top:4px">{stage["hunter_msg"]}</div>
                </div>''' if stage and stage["stage"] < 4 else
                f'<div style="color:#94a3b8;font-size:0.8rem;padding:8px;">{"ATH 대비 " + f"{drop:.1f}% 하락 — 20% 이상 시 1단계 진입" if drop is not None else "가격 데이터 없음"}</div>'}
                </div>""",
                unsafe_allow_html=True,
            )

            summary_rows.append({
                "팀": team_name.split()[0],
                "티커": ticker,
                "종목명": data["name"][:20],
                "현재가 ($)": f"${current:,.2f}" if current else "—",
                "52주 ATH ($)": f"${ath:,.2f}" if ath else "—",
                "하락률": f"{drop:.1f}%" if drop is not None else "—",
                "진입 단계": stage["label"] if stage else "대기",
                "추천 매수 ($)": f"${buy_amt_usd:,.0f}" if buy_amt_usd > 0 else "—",
                "추천 매수 (₩)": f"₩{buy_amt_krw:,.0f}" if buy_amt_usd > 0 else "—",
            })

    return summary_rows

# ─────────────────────────────────────────
# 팀 섹션 렌더링
# ─────────────────────────────────────────
st.markdown("### 🛡 화이트 팀 (White Team) — 방어 / 배당")

with st.spinner("화이트 팀 데이터 로딩 중..."):
    white_rows = render_team(
        "화이트 팀 🛡",
        st.session_state.white_tickers,
        white_budget,
        equal_weight_white,
        "#2563eb",
        "🛡",
    )

st.divider()
st.markdown("### 🚀 블루 팀 (Blue Team) — 성장 / 미래")

with st.spinner("블루 팀 데이터 로딩 중..."):
    blue_rows = render_team(
        "블루 팀 🚀",
        st.session_state.blue_tickers,
        blue_budget,
        equal_weight_blue,
        "#10b981",
        "🚀",
    )

# ─────────────────────────────────────────
# 전체 포트폴리오 종합 테이블
# ─────────────────────────────────────────
st.divider()
st.markdown("### 📊 전체 포트폴리오 집행 현황")

all_rows = white_rows + blue_rows
if all_rows:
    df = pd.DataFrame(all_rows)

    # 스타일 함수
    def highlight_stage(val):
        if "1단계" in str(val): return f"background-color: #eff6ff; color: #2563eb; font-weight: bold;"
        if "2단계" in str(val): return f"background-color: #f0fdf4; color: #059669; font-weight: bold;"
        if "3단계" in str(val): return f"background-color: #fffbeb; color: #d97706; font-weight: bold;"
        if "4단계" in str(val): return f"background-color: #fef2f2; color: #dc2626; font-weight: bold;"
        return ""

    styled = df.style.applymap(highlight_stage, subset=["진입 단계"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # 집행 요약
    active = [r for r in all_rows if r["추천 매수 ($)"] != "—"]
    if active:
        total_buy_usd = sum(
            float(r["추천 매수 ($)"].replace("$", "").replace(",", ""))
            for r in active
        )
        st.success(
            f"✅ **현재 {len(active)}개 종목이 매수 구간 진입** | "
            f"총 추천 집행 금액: **${total_buy_usd:,.0f}** "
            f"(≈ ₩{total_buy_usd * exchange_rate:,.0f})"
        )
    else:
        st.info("⏳ 현재 매수 구간에 진입한 종목이 없습니다. 사냥감을 기다리는 중...")

# ─────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────
st.divider()
st.markdown(
    """<div style="text-align:center;color:#94a3b8;font-size:0.78rem;padding:16px 0;">
    <strong>HUNTER PROTOCOL</strong> — 재민의 폭락장 저점 매수 시스템<br>
    📌 데이터 출처: yfinance (52주 기준) | 투자는 본인 책임입니다<br>
    🚀 Streamlit Cloud 배포 후 어디서나 사용 가능
    </div>""",
    unsafe_allow_html=True,
)
