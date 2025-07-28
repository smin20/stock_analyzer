import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from stock_analyzer import StockAnalyzer
import time

# 페이지 설정
st.set_page_config(
    page_title="미국 주식 분석기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 기본 닫힘
)

# 주요 미국 주식 티커 목록 (알파벳순 정렬)
MAJOR_TICKERS = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
    "AVGO", "AXP", "BA", "BAC", "BIIB", "BK", "BKNG", "BLK", "BMY", "BRK-B",
    "C", "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO",
    "CVS", "CVX", "DHR", "DIS", "DOW", "DUK", "EMR", "EXC", "F", "FB", "FDX",
    "GD", "GE", "GILD", "GM", "GOOGL", "GS", "HD", "HON", "IBM", "INTC",
    "JNJ", "JPM", "KHC", "KO", "LLY", "LMT", "LOW", "MA", "MCD", "MDLZ",
    "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT", "MU", "NFLX",
    "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM", "RTX",
    "SBUX", "SNOW", "SO", "SPY", "T", "TGT", "TMO", "TSLA", "TXN", "UNH",
    "UNP", "UPS", "V", "VZ", "WFC", "WMT", "XOM"
]

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .strategy-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-text {
        color: #dc3545;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 애플리케이션 초기화
@st.cache_resource
def get_analyzer():
    return StockAnalyzer()

analyzer = get_analyzer()

# 메인 헤더
st.markdown('<h1 class="main-header">📊 미국 주식 분석기</h1>', unsafe_allow_html=True)

# 상단 탭 네비게이션
tab1, tab2, tab3 = st.tabs(["🔍 단일 종목 분석", "📈 멀티 종목 비교", "🎯 종목 추천"])

# 캔들스틱 차트 생성 함수
def create_candlestick_chart(ticker, period="3mo"):
    """캔들스틱 차트 생성"""
    hist_data = analyzer.get_price_history(ticker, period)
    
    if hist_data is not None and not hist_data.empty:
        fig = go.Figure()
        
        # 캔들스틱 차트
        fig.add_trace(go.Candlestick(
            x=hist_data.index,
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name=f"{ticker} 주가"
        ))
        
        fig.update_layout(
            title=f"{ticker} 주가 차트 ({period})",
            xaxis_title="날짜",
            yaxis_title="주가 ($)",
            xaxis_rangeslider_visible=False,
            height=500,
            showlegend=False
        )
        
        # 주말 빈 공간 제거
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),  # 토요일-월요일 (주말) 제거
            ]
        )
        
        return fig
    
    return None

# 탭 1: 단일 종목 분석
with tab1:
    # 헤더 스타일링
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #1f77b4 0%, #17a2b8 50%, #20c997 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            🔍 AI 주식 분석기
        </h1>
        <p style="color: #666; font-size: 1.1rem;">개별 종목의 심층 분석과 투자 의견을 제공합니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 입력 섹션을 카드 스타일로 개선
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: #495057; margin-bottom: 1.5rem; text-align: center;">
                🎯 종목 선택
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 검색 가능한 티커 선택
        ticker = st.selectbox(
            "🔍 티커 검색 및 선택",
            options=MAJOR_TICKERS,
            index=MAJOR_TICKERS.index("AAPL"),
            help="티커를 타이핑하면 자동으로 검색됩니다"
        )
        
        # 직접 입력 옵션도 제공
        custom_ticker = st.text_input(
            "💡 또는 직접 입력",
            placeholder="예: AAPL, MSFT, GOOGL"
        ).upper()
        
        # 직접 입력한 값이 있으면 그것을 사용
        if custom_ticker:
            ticker = custom_ticker
        
        # 차트 기간 선택
        chart_period = st.selectbox(
            "📈 차트 기간 설정",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=1,
            format_func=lambda x: {"1mo": "1개월", "3mo": "3개월", "6mo": "6개월", "1y": "1년", "2y": "2년"}[x]
        )
        
        # 분석 버튼을 크고 눈에 띄게
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button(
            f"🚀 {ticker} 종목 분석 시작",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3cd, #ffeaa7); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: #856404; margin-bottom: 1.5rem; text-align: center;">
                ⭐ 인기 종목 바로가기
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 인기 종목을 더 예쁜 버튼으로 만들기
        popular_stocks = [
            {"ticker": "AAPL", "name": "애플", "color": "#007AFF", "icon": "🍎"},
            {"ticker": "MSFT", "name": "마이크로소프트", "color": "#00BCF2", "icon": "💻"},
            {"ticker": "GOOGL", "name": "구글", "color": "#4285F4", "icon": "🔍"},
            {"ticker": "AMZN", "name": "아마존", "color": "#FF9900", "icon": "📦"},
            {"ticker": "TSLA", "name": "테슬라", "color": "#CC0000", "icon": "🚗"},
            {"ticker": "NVDA", "name": "엔비디아", "color": "#76B900", "icon": "🎮"},
            {"ticker": "META", "name": "메타", "color": "#1877F2", "icon": "📱"},
            {"ticker": "NFLX", "name": "넷플릭스", "color": "#E50914", "icon": "🎬"}
        ]
        
        cols = st.columns(2)
        for i, stock in enumerate(popular_stocks):
            with cols[i % 2]:
                if st.button(
                    f"{stock['icon']} {stock['ticker']}\n{stock['name']}", 
                    key=f"pop_{stock['ticker']}",
                    use_container_width=True
                ):
                    ticker = stock['ticker']
                    analyze_btn = True
    
    if analyze_btn and ticker:
        with st.spinner(f"📡 {ticker} 데이터 수집 및 분석 중..."):
            if analyzer.get_stock_info(ticker):
                recommendation = analyzer.get_recommendation(ticker)
                
                if recommendation:
                    ratios = recommendation['ratios']
                    
                    # 결과 헤더
                    st.markdown(f"""
                    <div style="text-align: center; margin: 2rem 0;">
                        <h2 style="background: linear-gradient(135deg, #1f77b4, #17a2b8); 
                                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                                   font-size: 2rem; font-weight: bold;">
                            📊 {ticker} 분석 결과
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 기본 정보를 카드 스타일로 표시
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        current_price = ratios.get('현재가', 'N/A')
                        price_display = f"${current_price}" if current_price != 'N/A' else 'N/A'
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; 
                                    padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">💰</div>
                            <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.3rem;">{price_display}</div>
                            <small style="opacity: 0.9;">현재가</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        market_cap = ratios.get('시가총액', 'N/A')
                        if market_cap != 'N/A':
                            market_cap_b = market_cap / 1e9
                            cap_display = f"${market_cap_b:.1f}B"
                        else:
                            cap_display = "N/A"
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #17a2b8, #6f42c1); color: white; 
                                    padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">📈</div>
                            <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.3rem;">{cap_display}</div>
                            <small style="opacity: 0.9;">시가총액</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        score = recommendation['score']
                        if score >= 80:
                            score_color = "linear-gradient(135deg, #28a745, #20c997)"
                        elif score >= 60:
                            score_color = "linear-gradient(135deg, #fd7e14, #ffc107)"
                        else:
                            score_color = "linear-gradient(135deg, #dc3545, #e83e8c)"
                        
                        st.markdown(f"""
                        <div style="background: {score_color}; color: white; 
                                    padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🎯</div>
                            <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.3rem;">{score}/100</div>
                            <small style="opacity: 0.9;">종합점수</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        recommendation_text = recommendation['recommendation']
                        reason = recommendation['reason']
                        
                        rec_colors = {
                            '강력 매수': "linear-gradient(135deg, #28a745, #20c997)",
                            '매수': "linear-gradient(135deg, #17a2b8, #20c997)",
                            '보유': "linear-gradient(135deg, #ffc107, #fd7e14)",
                            '관망': "linear-gradient(135deg, #fd7e14, #e83e8c)",
                            '매도': "linear-gradient(135deg, #dc3545, #e83e8c)"
                        }
                        
                        rec_color = rec_colors.get(recommendation_text, "linear-gradient(135deg, #6c757d, #495057)")
                        
                        st.markdown(f"""
                        <div style="background: {rec_color}; color: white; 
                                    padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🎯</div>
                            <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.3rem;">{recommendation_text}</div>
                            <small style="opacity: 0.9; font-size: 0.8rem;">{reason}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 캔들스틱 차트와 재무 지표를 나란히 배치
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📈 주가 차트")
                        candlestick_chart = create_candlestick_chart(ticker, chart_period)
                        if candlestick_chart:
                            st.plotly_chart(candlestick_chart, use_container_width=True)
                        else:
                            st.error("차트 데이터를 불러올 수 없습니다.")
                    
                    with col2:
                        st.subheader("📋 주요 재무비율")
                        
                        financial_data = {
                            "지표": ["PER", "PBR", "PSR", "ROE (%)", "ROA (%)", "부채비율 (%)", "배당수익률 (%)"],
                            "값": [
                                f"{ratios.get('PER', 'N/A'):.2f}" if ratios.get('PER') != 'N/A' and ratios.get('PER') is not None else 'N/A',
                                f"{ratios.get('PBR', 'N/A'):.2f}" if ratios.get('PBR') != 'N/A' and ratios.get('PBR') is not None else 'N/A',
                                f"{ratios.get('PSR', 'N/A'):.2f}" if ratios.get('PSR') != 'N/A' and ratios.get('PSR') is not None else 'N/A',
                                f"{ratios.get('ROE', 'N/A')*100:.1f}" if ratios.get('ROE') != 'N/A' and ratios.get('ROE') is not None else 'N/A',
                                f"{ratios.get('ROA', 'N/A')*100:.1f}" if ratios.get('ROA') != 'N/A' and ratios.get('ROA') is not None else 'N/A',
                                f"{ratios.get('부채비율', 'N/A')*100:.1f}" if ratios.get('부채비율') != 'N/A' and ratios.get('부채비율') is not None else 'N/A',
                                f"{ratios.get('배당수익률', 'N/A')*100:.2f}" if ratios.get('배당수익률') != 'N/A' and ratios.get('배당수익률') is not None else 'N/A'
                            ]
                        }
                        
                        df_financial = pd.DataFrame(financial_data)
                        st.dataframe(df_financial, hide_index=True)
                        
                        # 점수 차트
                        st.subheader("📊 세부 점수")
                        scores = {
                            '수익성': ratios.get('수익성_점수', 0),
                            '안정성': ratios.get('안정성_점수', 0),
                            '가치평가': ratios.get('가치평가_점수', 0)
                        }
                        
                        fig = go.Figure(data=go.Bar(
                            x=list(scores.keys()),
                            y=list(scores.values()),
                            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
                        ))
                        
                        fig.update_layout(
                            yaxis_range=[0, 100],
                            height=300,
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # 52주 정보
                    if ratios.get('52주_고점대비') != 'N/A':
                        st.subheader("📈 52주 기준 정보")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("최고가 대비", f"{ratios.get('52주_고점대비', 'N/A')}%")
                        
                        with col2:
                            st.metric("최저가 대비", f"{ratios.get('52주_저점대비', 'N/A')}%")
                        
                        with col3:
                            high_low_ratio = ratios.get('52주_고점대비', 0)
                            if high_low_ratio > 95:
                                st.success("🔥 고점 근처")
                            elif high_low_ratio > 80:
                                st.info("📈 상승 구간")
                            elif high_low_ratio < 70:
                                st.warning("📉 조정 구간")
                            else:
                                st.info("📊 중간 구간")
                
                else:
                    st.error(f"❌ {ticker} 분석에 실패했습니다.")
            else:
                st.error(f"❌ {ticker} 데이터를 찾을 수 없습니다.")

# 탭 2: 멀티 종목 비교
with tab2:
    # 헤더 스타일링
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 50%, #ff7675 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            📈 스마트 종목 비교
        </h1>
        <p style="color: #666; font-size: 1.1rem;">여러 종목을 동시에 비교하여 최적의 투자 기회를 발견하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: #2e7d32; margin-bottom: 1.5rem; text-align: center;">
                🎯 비교할 종목 선택
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 다중 선택 가능한 티커 선택
        selected_tickers = st.multiselect(
            "🔍 티커 검색 및 선택 (다중 선택 가능)",
            options=MAJOR_TICKERS,
            default=["AAPL", "MSFT", "GOOGL"],
            help="여러 종목을 선택할 수 있습니다. 티커를 타이핑하면 자동으로 검색됩니다"
        )
        
        # 직접 입력 옵션도 제공
        custom_tickers_input = st.text_input(
            "💡 또는 직접 입력 (쉼표로 구분)",
            placeholder="예: AAPL,MSFT,GOOGL,AMZN",
            key="compare_custom_tickers"
        )
        
        # 직접 입력한 값이 있으면 그것을 사용
        if custom_tickers_input:
            tickers = [t.strip().upper() for t in custom_tickers_input.split(',') if t.strip()]
        else:
            tickers = selected_tickers
        
        # 선택된 종목 수 표시
        if tickers:
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
                <span style="color: #1976d2; font-weight: bold;">📊 선택된 종목: {len(tickers)}개</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 비교 분석 버튼
        compare_btn = st.button("🚀 멀티 종목 비교 분석", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: #e65100; margin-bottom: 1.5rem; text-align: center;">
                ⚡ 빠른 비교 그룹
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 비교 그룹을 카드 스타일로 만들기
        preset_groups = [
            {"name": "테크 대장주", "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"], "icon": "💻", "color": "#4285F4"},
            {"name": "클라우드", "tickers": ["MSFT", "AMZN", "GOOGL", "CRM"], "icon": "☁️", "color": "#34A853"},
            {"name": "반도체", "tickers": ["NVDA", "AMD", "INTC"], "icon": "🔧", "color": "#EA4335"},
            {"name": "전기차", "tickers": ["TSLA"], "icon": "🚗", "color": "#FBBC04"},
            {"name": "금융", "tickers": ["JPM", "BAC", "WFC", "C"], "icon": "🏦", "color": "#9C27B0"}
        ]
        
        for group in preset_groups:
            if st.button(
                f"{group['icon']} {group['name']}\n({len(group['tickers'])}개 종목)", 
                key=f"preset_compare_{group['name']}",
                use_container_width=True
            ):
                selected_tickers = group['tickers']
                tickers = group['tickers']
                compare_btn = True
    
    if compare_btn and tickers:
        with st.spinner(f"📡 {len(tickers)}개 종목 데이터 수집 및 분석 중..."):
            results = analyzer.compare_stocks(tickers)
            
            if results:
                # 결과 헤더
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                               font-size: 2rem; font-weight: bold;">
                        📊 {len(results)}개 종목 비교 결과
                    </h2>
                    <p style="color: #666; font-size: 1.1rem;">
                        종합적인 분석을 통한 순위별 비교 결과입니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # 상위 3개 종목 하이라이트
                if len(results) >= 3:
                    st.markdown("### 🏆 TOP 3 종목")
                    
                    cols = st.columns(3)
                    medals = ["🥇", "🥈", "🥉"]
                    colors = [
                        "linear-gradient(135deg, #FFD700, #FFA500)",
                        "linear-gradient(135deg, #C0C0C0, #A9A9A9)", 
                        "linear-gradient(135deg, #CD7F32, #8B4513)"
                    ]
                    
                    for i in range(min(3, len(results))):
                        result = results[i]
                        with cols[i]:
                            st.markdown(f"""
                            <div style="background: {colors[i]}; color: white; text-align: center; 
                                        padding: 2rem; border-radius: 15px; margin-bottom: 1rem;
                                        box-shadow: 0 6px 20px rgba(0,0,0,0.3);">
                                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{medals[i]}</div>
                                <h3 style="margin: 0.5rem 0; font-size: 1.5rem;">{result['ticker']}</h3>
                                <div style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">{result['score']:.1f}</div>
                                <div style="font-size: 1rem; margin-top: 0.5rem;">{result['recommendation']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 결과 데이터프레임 생성 (더 세련되게)
                st.markdown("### 📋 상세 비교 결과")
                
                comparison_data = []
                for i, result in enumerate(results):
                    ratios = result['ratios']
                    
                    # 순위에 따른 배지
                    if i == 0:
                        rank_badge = "🥇 1위"
                    elif i == 1:
                        rank_badge = "🥈 2위"
                    elif i == 2:
                        rank_badge = "🥉 3위"
                    else:
                        rank_badge = f"📊 {i+1}위"
                    
                    comparison_data.append({
                        '순위': rank_badge,
                        '티커': result['ticker'],
                        '현재가': f"${ratios.get('현재가', 'N/A')}" if ratios.get('현재가') != 'N/A' else 'N/A',
                        'PER': f"{ratios.get('PER', 'N/A'):.1f}" if ratios.get('PER') != 'N/A' and ratios.get('PER') is not None else 'N/A',
                        'PBR': f"{ratios.get('PBR', 'N/A'):.1f}" if ratios.get('PBR') != 'N/A' and ratios.get('PBR') is not None else 'N/A',
                        'ROE(%)': f"{ratios.get('ROE', 'N/A')*100:.1f}" if ratios.get('ROE') != 'N/A' and ratios.get('ROE') is not None else 'N/A',
                        '종합점수': f"{result['score']:.1f}",
                        '투자의견': result['recommendation']
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, hide_index=True, use_container_width=True, height=400)
                
                # 시각화
                col1, col2 = st.columns(2)
                
                with col1:
                    # 종합점수 비교 차트
                    fig_scores = go.Figure(data=go.Bar(
                        x=[r['ticker'] for r in results],
                        y=[r['score'] for r in results],
                        marker_color='lightblue'
                    ))
                    
                    fig_scores.update_layout(
                        title="🎯 종합점수 비교",
                        yaxis_range=[0, 100],
                        height=400
                    )
                    
                    st.plotly_chart(fig_scores, use_container_width=True)
                
                with col2:
                    # PER vs PBR 산점도
                    per_values = []
                    pbr_values = []
                    ticker_names = []
                    
                    for result in results:
                        ratios = result['ratios']
                        per = ratios.get('PER', None)
                        pbr = ratios.get('PBR', None)
                        
                        if per is not None and per != 'N/A' and pbr is not None and pbr != 'N/A':
                            per_values.append(per)
                            pbr_values.append(pbr)
                            ticker_names.append(result['ticker'])
                    
                    if per_values and pbr_values:
                        fig_scatter = go.Figure(data=go.Scatter(
                            x=per_values,
                            y=pbr_values,
                            mode='markers+text',
                            text=ticker_names,
                            textposition="top center",
                            marker=dict(size=12, color='orange')
                        ))
                        
                        fig_scatter.update_layout(
                            title="📊 PER vs PBR",
                            xaxis_title="PER",
                            yaxis_title="PBR",
                            height=400
                        )
                        
                        st.plotly_chart(fig_scatter, use_container_width=True)
                
                # 다중 종목 캔들스틱 차트
                st.subheader("📈 주가 비교 차트")
                chart_period_compare = st.selectbox(
                    "차트 기간 선택",
                    ["1mo", "3mo", "6mo", "1y"],
                    index=1,
                    format_func=lambda x: {"1mo": "1개월", "3mo": "3개월", "6mo": "6개월", "1y": "1년"}[x],
                    key="compare_chart_period"
                )
                
                # 정규화된 주가 비교 차트
                fig_multi = go.Figure()
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
                
                for i, result in enumerate(results):
                    ticker = result['ticker']
                    hist_data = analyzer.get_price_history(ticker, chart_period_compare)
                    
                    if hist_data is not None and not hist_data.empty:
                        # 첫 날을 100으로 정규화
                        normalized_price = (hist_data['Close'] / hist_data['Close'].iloc[0]) * 100
                        
                        fig_multi.add_trace(go.Scatter(
                            x=hist_data.index,
                            y=normalized_price,
                            mode='lines',
                            name=ticker,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))
                
                fig_multi.update_layout(
                    title=f"주가 수익률 비교 ({chart_period_compare}, 기준점=100)",
                    xaxis_title="날짜",
                    yaxis_title="정규화된 주가 (%)",
                    height=500,
                    hovermode='x unified'
                )
                
                # 주말 빈 공간 제거
                fig_multi.update_xaxes(
                    rangebreaks=[
                        dict(bounds=["sat", "mon"]),  # 토요일-월요일 (주말) 제거
                    ]
                )
                
                st.plotly_chart(fig_multi, use_container_width=True)
            
            else:
                st.error("❌ 비교할 수 있는 데이터가 없습니다.")

# 탭 3: 종목 추천
with tab3:
    # 헤더 스타일링
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            🎯 AI 투자 전략 추천
        </h1>
        <p style="color: #666; font-size: 1.1rem;">인공지능이 분석한 맞춤형 투자 전략으로 최적의 종목을 찾아보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 투자 전략 선택 카드들
    st.markdown("### 🎨 투자 전략 선택")
    
    strategies = {
        'low_per': {
            'name': '저PER 가치투자',
            'icon': '💎',
            'color': '#28a745',
            'description': '저평가된 우량주 발굴',
            'criteria': 'PER 15 이하, 안정적 수익성'
        },
        'low_pbr': {
            'name': '저PBR 자산가치투자', 
            'icon': '🏗️',
            'color': '#17a2b8',
            'description': '자산 대비 저평가 종목',
            'criteria': 'PBR 2 이하, 견고한 자산 기반'
        },
        'high_roe': {
            'name': '고ROE 수익성투자',
            'icon': '📈',
            'color': '#fd7e14',
            'description': '높은 자기자본수익률',
            'criteria': 'ROE 15% 이상, 지속적 성장'
        },
        'high_dividend': {
            'name': '고배당 투자',
            'icon': '💰',
            'color': '#6f42c1',
            'description': '안정적인 배당 수익',
            'criteria': '배당수익률 3% 이상, 배당 지속성'
        },
        'growth': {
            'name': '성장주 투자',
            'icon': '🚀',
            'color': '#e83e8c',
            'description': '빠른 성장 잠재력',
            'criteria': '매출·이익 고성장, 미래 가치'
        },
        'comprehensive': {
            'name': '종합 투자',
            'icon': '🎯',
            'color': '#6610f2',
            'description': '균형잡힌 종합 분석',
            'criteria': '가치·성장·수익성 종합 평가'
        }
    }
    
    # 전략 카드들을 2x3 그리드로 배치
    cols = st.columns(3)
    selected_strategy = None
    
    for i, (strategy_key, strategy_data) in enumerate(strategies.items()):
        with cols[i % 3]:
            if st.button(
                f"{strategy_data['icon']} {strategy_data['name']}", 
                key=f"strategy_{strategy_key}",
                use_container_width=True
            ):
                selected_strategy = strategy_key
    
    # 선택된 전략이 없으면 기본값 설정
    if selected_strategy is None:
        selected_strategy = 'comprehensive'
    
    # 선택된 전략 정보 표시
    strategy_info = strategies[selected_strategy]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {strategy_info['color']}15, {strategy_info['color']}25); 
                border-left: 5px solid {strategy_info['color']}; 
                padding: 1.5rem; border-radius: 10px; margin: 2rem 0;">
        <h3 style="color: {strategy_info['color']}; margin-bottom: 1rem;">
            {strategy_info['icon']} {strategy_info['name']}
        </h3>
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem; color: #333;">
            <strong>전략 설명:</strong> {strategy_info['description']}
        </p>
        <p style="color: #666; margin-bottom: 0;">
            <strong>선별 기준:</strong> {strategy_info['criteria']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 종목 풀 선택 (간소화)
    st.markdown("### 📊 분석 범위 설정")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 기본 종목 풀 (주요 대형주들)
        default_pool = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", 
                       "CRM", "ADBE", "JPM", "JNJ", "PG", "KO", "V", "MA", "HD", "UNH", "PFE", "WMT"]
        
        ticker_pool_list = st.multiselect(
            "🔍 분석할 종목 선택 (기본 20개 대형주 포함)",
            options=MAJOR_TICKERS,
            default=default_pool,
            help="더 많은 종목을 선택할수록 더 정확한 분석이 가능합니다"
        )
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center;">
            <h4 style="color: #495057; margin-bottom: 0.5rem;">✨ 분석 품질</h4>
            <p style="font-size: 1.2rem; font-weight: bold; color: #28a745; margin-bottom: 0;">
                {count}개 종목
            </p>
            <small style="color: #6c757d;">선택된 종목 수</small>
        </div>
        """.format(count=len(ticker_pool_list)), unsafe_allow_html=True)
    
    # 분석 시작 버튼 (크고 눈에 띄게)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        recommend_btn = st.button(
            f"🚀 {strategy_info['name']} 분석 시작",
            type="primary",
            use_container_width=True
        )
    
    if recommend_btn and ticker_pool_list:
        with st.spinner(f"🔍 {strategy_info['name']} 전략으로 {len(ticker_pool_list)}개 종목 분석 중..."):
            recommendations = analyzer.strategy_recommend(ticker_pool_list, selected_strategy)
            
            if recommendations:
                # 결과 헤더
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <h2 style="background: linear-gradient(135deg, {strategy_info['color']}, {strategy_info['color']}aa); 
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                               font-size: 2rem; font-weight: bold;">
                        {strategy_info['icon']} {strategy_info['name']} 분석 결과
                    </h2>
                    <p style="color: #666; font-size: 1.1rem;">
                        총 {len(recommendations)}개 종목 중 상위 추천 종목들입니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # 상위 5개 종목 하이라이트 (더 세련되게)
                st.markdown("### 🏆 TOP 5 추천 종목")
                
                cols = st.columns(5)
                for i, rec in enumerate(recommendations[:5]):
                    with cols[i]:
                        score = rec['score']
                        ticker = rec['ticker']
                        
                        if score >= 80:
                            color = "#28a745"
                            gradient = "linear-gradient(135deg, #28a745, #20c997)"
                            emoji = "🥇" if i == 0 else "🟢"
                        elif score >= 60:
                            color = "#fd7e14"
                            gradient = "linear-gradient(135deg, #fd7e14, #ffc107)"
                            emoji = "🟡"
                        else:
                            color = "#dc3545"
                            gradient = "linear-gradient(135deg, #dc3545, #e83e8c)"
                            emoji = "🔴"
                        
                        rank_suffix = ["st", "nd", "rd", "th", "th"][i]
                        
                        st.markdown(f"""
                        <div style="background: {gradient}; color: white; text-align: center; 
                                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;
                                    box-shadow: 0 4px 15px rgba(0,0,0,0.2); transform: scale(1.02);">
                            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{emoji}</div>
                            <h3 style="margin: 0.5rem 0; font-size: 1.3rem;">{ticker}</h3>
                            <div style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{score:.1f}</div>
                            <small style="opacity: 0.9;">{i+1}{rank_suffix} 순위</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 전체 결과 테이블 (스타일링 개선)
                st.markdown("### 📊 상세 분석 결과")
                
                recommendation_data = []
                for i, rec in enumerate(recommendations):
                    ratios = rec['ratios']
                    
                    # 점수에 따른 등급 표시
                    score = rec['score']
                    if score >= 80:
                        grade = "🥇 S"
                        grade_color = "#28a745"
                    elif score >= 70:
                        grade = "🥈 A"
                        grade_color = "#17a2b8"
                    elif score >= 60:
                        grade = "🥉 B"
                        grade_color = "#fd7e14"
                    elif score >= 50:
                        grade = "📊 C"
                        grade_color = "#ffc107"
                    else:
                        grade = "📉 D"
                        grade_color = "#dc3545"
                    
                    recommendation_data.append({
                        '순위': f"{i + 1}위",
                        '티커': rec['ticker'],
                        '등급': grade,
                        '점수': f"{rec['score']:.1f}",
                        'PER': f"{ratios.get('PER', 'N/A'):.1f}" if ratios.get('PER') != 'N/A' and ratios.get('PER') is not None else 'N/A',
                        'PBR': f"{ratios.get('PBR', 'N/A'):.1f}" if ratios.get('PBR') != 'N/A' and ratios.get('PBR') is not None else 'N/A',
                        'ROE(%)': f"{ratios.get('ROE', 'N/A')*100:.1f}" if ratios.get('ROE') != 'N/A' and ratios.get('ROE') is not None else 'N/A',
                        '배당률(%)': f"{ratios.get('배당수익률', 'N/A')*100:.2f}" if ratios.get('배당수익률') != 'N/A' and ratios.get('배당수익률') is not None else 'N/A',
                        '현재가': f"${ratios.get('현재가', 'N/A')}" if ratios.get('현재가') != 'N/A' else 'N/A'
                    })
                
                df_recommendations = pd.DataFrame(recommendation_data)
                
                # 스타일링된 테이블 표시
                st.dataframe(
                    df_recommendations, 
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
                
                # 차트와 요약 통계를 나란히 배치
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # 추천 점수 차트 (더 예쁘게)
                    colors = []
                    for rec in recommendations:
                        score = rec['score']
                        if score >= 80:
                            colors.append('#28a745')
                        elif score >= 70:
                            colors.append('#17a2b8')
                        elif score >= 60:
                            colors.append('#fd7e14')
                        elif score >= 50:
                            colors.append('#ffc107')
                        else:
                            colors.append('#dc3545')
                    
                    fig_recommendations = go.Figure(data=go.Bar(
                        x=[rec['ticker'] for rec in recommendations],
                        y=[rec['score'] for rec in recommendations],
                        marker_color=colors,
                        marker_line=dict(width=2, color='white'),
                        text=[f"{rec['score']:.1f}" for rec in recommendations],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>점수: %{y:.1f}<extra></extra>'
                    ))
                    
                    fig_recommendations.update_layout(
                        title=f"📈 {strategy_info['name']} 종목별 점수",
                        yaxis_range=[0, min(100, max([rec['score'] for rec in recommendations]) + 10)],
                        height=450,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        title_font_size=16
                    )
                    
                    fig_recommendations.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig_recommendations.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    
                    st.plotly_chart(fig_recommendations, use_container_width=True)
                
                with col2:
                    # 분석 요약
                    avg_score = sum([rec['score'] for rec in recommendations]) / len(recommendations)
                    high_grade_count = len([rec for rec in recommendations if rec['score'] >= 70])
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                                padding: 2rem; border-radius: 15px; margin-top: 1rem;">
                        <h4 style="color: #495057; text-align: center; margin-bottom: 1.5rem;">
                            📊 분석 요약
                        </h4>
                        
                        <div style="text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 2rem; font-weight: bold; color: {strategy_info['color']};">
                                {avg_score:.1f}
                            </div>
                            <small style="color: #6c757d;">평균 점수</small>
                        </div>
                        
                        <div style="text-align: center; margin-bottom: 1rem;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">
                                {high_grade_count}개
                            </div>
                            <small style="color: #6c757d;">우수 등급 (70점 이상)</small>
                        </div>
                        
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #17a2b8;">
                                {len(recommendations)}개
                            </div>
                            <small style="color: #6c757d;">총 분석 종목</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.error("❌ 추천할 종목이 없습니다.")

# 사이드바 정보 (최소화)
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #1f77b4; margin-bottom: 1rem;">📊 AI 주식 분석기</h2>
        <p style="color: #666; font-size: 0.9rem;">프리미엄 투자 분석 도구</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 주요 기능")
    st.markdown("""
    **🔍 단일 종목 분석**
    - 실시간 주가 및 재무비율 분석
    - AI 기반 투자 의견 제공
    - 인터랙티브 캔들스틱 차트
    
    **📈 멀티 종목 비교**
    - 여러 종목 동시 비교 분석
    - TOP 3 종목 하이라이트
    - 산업별 그룹 비교 지원
    
    **🎯 AI 투자 전략 추천**
    - 6가지 전문 투자 전략
    - 등급별 종목 분류 (S~D등급)
    - 맞춤형 포트폴리오 제안
    """)

    st.markdown("### 🚀 새로운 기능")
    st.markdown("""
    - ✨ **검색 가능한 티커 선택**
    - 🎨 **모던한 UI/UX 디자인**
    - 📊 **실시간 데이터 시각화**
    - 🏆 **순위별 등급 시스템**
    """)

    st.markdown("### ⚠️ 투자 유의사항")
    st.markdown("""
    - 본 서비스는 **투자 참고용**입니다
    - 실제 투자 시 **추가 분석** 필요
    - 투자 결정은 **본인 책임**입니다
    - 데이터 출처: **Yahoo Finance**
    """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <small>💡 Powered by Yahoo Finance API</small><br>
        <small>🤖 AI-Enhanced Analysis</small>
    </div>
    """, unsafe_allow_html=True) 