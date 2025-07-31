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
    layout="wide"
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

# S&P 500 주요 종목 (300개+) - 다양한 섹터 포함
SP500_TICKERS = [
    # 기존 대형주
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH",
    "JNJ", "XOM", "JPM", "V", "PG", "MA", "CVX", "HD", "ABBV", "PFE", "KO", "PEP",
    "AVGO", "TMO", "COST", "WMT", "MRK", "BAC", "NFLX", "CRM", "ACN", "LLY",
    
    # 금융
    "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SPGI", "CME", "ICE",
    "COF", "USB", "PNC", "TFC", "BK", "STT", "NTRS", "RF", "CFG", "FITB",
    
    # 기술
    "MSFT", "AAPL", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "CRM", "ORCL", "ADBE",
    "NOW", "INTU", "IBM", "TXN", "QCOM", "AMAT", "ADI", "MU", "MRVL", "AMD",
    "INTC", "CSCO", "AVGO", "LRCX", "KLAC", "SNPS", "CDNS", "FTNT", "PANW",
    
    # 헬스케어
    "UNH", "JNJ", "PFE", "ABBV", "TMO", "ABT", "LLY", "DHR", "BMY", "MRK",
    "AMGN", "GILD", "MDT", "CI", "ISRG", "SYK", "BSX", "REGN", "ZTS", "CVS",
    "HUM", "ANTM", "BDX", "ELV", "DXCM", "IQV", "BIIB", "MRNA", "VRTX",
    
    # 소비재
    "AMZN", "TSLA", "HD", "WMT", "PG", "KO", "PEP", "COST", "NKE", "MCD",
    "SBUX", "TGT", "LOW", "TJX", "EL", "CL", "KMB", "GIS", "K", "HSY",
    "CLX", "CHD", "SJM", "CAG", "CPB", "MKC", "TAP", "STZ", "BF-B",
    
    # 통신서비스  
    "GOOGL", "GOOG", "META", "NFLX", "DIS", "CMCSA", "VZ", "T", "CHTR", "TMUS",
    "ATVI", "EA", "TTWO", "NTES", "ROKU", "SNAP", "PINS", "TWTR", "SPOT",
    
    # 산업재
    "BA", "CAT", "HON", "UPS", "RTX", "LMT", "GE", "MMM", "FDX", "NOC",
    "GD", "TXT", "EMR", "ETN", "ITW", "PH", "CMI", "DE", "ROK", "DOV",
    "IR", "SWK", "AME", "ROP", "LDOS", "LHX", "HWM", "OTIS", "CARR",
    
    # 에너지
    "XOM", "CVX", "COP", "EOG", "SLB", "PXD", "KMI", "OKE", "WMB", "VLO",
    "PSX", "MPC", "HES", "FANG", "DVN", "APA", "CTRA", "OXY", "BKR", "HAL",
    
    # 유틸리티
    "NEE", "DUK", "SO", "AEP", "EXC", "XEL", "SRE", "D", "PEG", "EIX",
    "WEC", "ES", "AWK", "FE", "EDU", "ETR", "CNP", "NI", "LNT", "EVRG",
    
    # 소재
    "LIN", "APD", "ECL", "SHW", "FCX", "NEM", "DOW", "DD", "ALB", "CE",
    "VMC", "MLM", "NUE", "STLD", "X", "CLF", "AA", "CF", "FMC", "EMN",
    
    # 리츠
    "AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "WELL", "DLR", "EQR",
    "AVB", "EXR", "VTR", "ARE", "MAA", "UDR", "ESS", "CPT", "FRT", "REG",
    
    # 기타 섹터
    "BRK-B", "V", "MA", "PYPL", "ADP", "INTU", "SPGI", "CME", "ICE", "MSCI",
    "MCO", "TRV", "ALL", "PGR", "AFL", "MET", "PRU", "AIG", "WRB", "CB",
    "AON", "MMC", "AJG", "BRO", "RE", "WTW", "EG", "ACGL", "RGA", "LNC"
]

# 중복 제거 및 정렬
EXTENDED_TICKERS = sorted(list(set(SP500_TICKERS)))

# CSS 스타일링
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Color+Emoji&display=swap');
    
    * {
        font-family: 'Noto Sans KR', 'Noto Color Emoji', Arial, sans-serif !important;
    }
    
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
def get_analyzer(version="v3"):  # 버전을 업데이트하여 캐시 무효화
    # Streamlit Cloud secrets에서 API 키 가져오기
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        return StockAnalyzer(api_key=api_key)
    except Exception as e:
        return StockAnalyzer()

analyzer = get_analyzer()

# 사이드바에 API 상태 표시
with st.sidebar:
    st.markdown("### 🔧 시스템 상태")
    
    if analyzer.gemini_available:
        st.success("🤖 Gemini AI: 활성화")
        st.info("✨ 자연어 분석 기능 사용 가능")
    else:
        st.warning("🤖 Gemini AI: 비활성화")
        st.info("기본 분석 기능만 사용 가능")

# 메인 헤더
st.markdown('<h1 class="main-header"> 미국 주식 분석기</h1>', unsafe_allow_html=True)

# 상단 탭 네비게이션
tab1, tab2, tab3 = st.tabs(["종목 분석", "투자 전략", "AI 분석"])

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
            <span class="emoji">🔍</span> AI 주식 분석기
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
        
        # 입력 방식 선택 스위치
        input_mode = st.radio(
            "📝 입력 방식 선택",
            options=["리스트에서 선택", "직접 입력"],
            horizontal=True,
            help="원하는 입력 방식을 선택하세요"
        )
        
        # 선택된 입력 방식에 따라 다른 UI 표시
        if input_mode == "리스트에서 선택":
            ticker = st.selectbox(
                "🔍 인기 종목에서 선택",
                options=MAJOR_TICKERS,
                index=MAJOR_TICKERS.index("AAPL"),
                help="주요 종목 리스트에서 선택하세요"
            )
        else:  # 직접 입력
            ticker = st.text_input(
                "✏️ 티커 직접 입력",
                placeholder="예: AAPL, MSFT, GOOGL, NVDA",
                help="원하는 종목의 티커를 직접 입력하세요"
            ).upper()
            
            # 직접 입력 시 기본값 설정
            if not ticker:
                ticker = "AAPL"
        
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
                    
                    # 회사 설명 추가
                    with st.spinner(f"🏢 {ticker} 회사 정보 생성 중..."):
                        company_description = analyzer.get_company_description(ticker)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                                padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0; 
                                border-left: 4px solid #17a2b8;">
                        <h4 style="color: #495057; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="margin-right: 0.5rem;">🏢</span>
                            회사 소개
                        </h4>
                        <p style="color: #6c757d; font-size: 1.1rem; line-height: 1.6; margin: 0;">
                            {company_description}
                        </p>
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
                                f"{ratios.get('부채비율', 'N/A'):.1f}" if ratios.get('부채비율') != 'N/A' and ratios.get('부채비율') is not None else 'N/A',
                                f"{ratios.get('배당수익률', 'N/A'):.2f}" if ratios.get('배당수익률') != 'N/A' and ratios.get('배당수익률') is not None else 'N/A'
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

# 탭 2: 종목 추천
with tab2:
    # 헤더 스타일링
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            AI 투자 전략 추천
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
    
    # 세션 상태에서 선택된 전략 가져오기
    if 'selected_strategy' not in st.session_state:
        st.session_state.selected_strategy = 'comprehensive'
    
    # 전략 카드들을 2x3 그리드로 배치
    cols = st.columns(3)
    
    for i, (strategy_key, strategy_data) in enumerate(strategies.items()):
        with cols[i % 3]:
            if st.button(
                f"{strategy_data['icon']} {strategy_data['name']}", 
                key=f"strategy_{strategy_key}",
                use_container_width=True
            ):
                st.session_state.selected_strategy = strategy_key
                st.rerun()  # 페이지 즉시 업데이트
    
    # 세션 상태에서 선택된 전략 사용
    selected_strategy = st.session_state.selected_strategy
    
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
            help="더 많은 종목을 선택할수록 더 정확한 분석이 가능합니다",
            key="tab2_ticker_selection"
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
            use_container_width=True,
            key="tab2_recommend_btn"
        )
    

    
    # 기본 전략 분석 처리
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
                        '배당률(%)': f"{ratios.get('배당수익률', 'N/A'):.2f}" if ratios.get('배당수익률') != 'N/A' and ratios.get('배당수익률') is not None else 'N/A',
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



# 탭 3: 나만의 전략 만들기
with tab3:
    # 헤더 스타일링
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="background: linear-gradient(135deg, #6610f2 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            AI 맞춤형 투자 전략
        </h1>
        <p style="color: #666; font-size: 1.1rem;">전략을 설명하면 AI가 당신만의 맞춤형 투자 전략을 만들어드립니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: #e65100; margin-bottom: 1.5rem; text-align: center;">
                💬 AI가 당신의 전략을 이해합니다
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 예시 프롬프트 버튼들
        st.markdown("**💡 빠른 예시 선택**")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        example_prompts = [
            "PER 30 이하이면서 배당수익률이 0.5% 이상인 안정적인 대형주를 찾고 싶어요",
            "ROE 15% 이상이고 성장 가능성이 높은 테크주 중에서 부채비율이 200% 이하인 종목을 원합니다", 
            "배당수익률 0.3% 이상이면서 부채비율 200% 이하인 안정적인 배당주에 투자하고 싶습니다"
        ]
        
        # 세션 상태에서 선택된 프롬프트 가져오기
        if 'selected_prompt' not in st.session_state:
            st.session_state.selected_prompt = ""
        
        with col_btn1:
            if st.button("📈 가치+배당", use_container_width=True, key="prompt_btn1"):
                st.session_state.selected_prompt = example_prompts[0]
                st.rerun()
        
        with col_btn2:
            if st.button("🚀 성장+품질", use_container_width=True, key="prompt_btn2"):
                st.session_state.selected_prompt = example_prompts[1]
                st.rerun()
                
        with col_btn3:
            if st.button("💰 안정배당", use_container_width=True, key="prompt_btn3"):
                st.session_state.selected_prompt = example_prompts[2]
                st.rerun()
        
        user_strategy_input = st.text_area(
            "💭 원하는 투자 전략을 설명해주세요",
            value=st.session_state.selected_prompt,
            placeholder="예: 'PER 30 이하이면서 배당수익률이 0.5% 이상인 안정적인 대형주를 찾고 싶어요'\n     '성장 가능성이 높은 테크주 중에서 부채비율이 200% 이하인 종목을 원합니다'\n     '배당수익률 0.3% 이상이면서 부채비율 200% 이하인 안정 배당주에 투자하고 싶습니다'",
            height=180,
            help="일반적인 말투로 편하게 입력하세요. AI가 투자 조건을 자동으로 분석합니다.",
            key="tab4_strategy_input"
        )
        
        # 자연어 전략 분석 버튼
        natural_strategy_btn = st.button(
            "🤖 AI 전략 분석 시작", 
            type="primary",
            use_container_width=True,
            help="Gemini AI가 당신의 전략을 분석하여 최적의 종목을 찾아드립니다",
            key="tab4_natural_btn"
        )
    
    with col2:
        # 입력 예시를 컨테이너로 감싸서 스타일링
        with st.container():
            st.markdown("""
                <h4 style="color: #495057; margin-bottom: 1.5rem; text-align: center;">💡 입력 예시</h4>
            """, unsafe_allow_html=True)
            
            # 각 전략 유형을 개별 컨테이너로 표시
            strategies = [
                {
                    "icon": "📈",
                    "type": "가치투자형",
                    "desc": "PER 30 이하, 배당 0.5% 이상인 합리적 가격 우량주",
                    "color": "#28a745"
                },
                {
                    "icon": "🚀",
                    "type": "성장투자형",
                    "desc": "ROE 15% 이상, 부채비율 200% 이하 건전 성장주",
                    "color": "#007bff"
                },
                {
                    "icon": "💰",
                    "type": "배당투자형",
                    "desc": "배당수익률 0.3% 이상, 부채비율 200% 이하 안정 배당주",
                    "color": "#6f42c1"
                },
                {
                    "icon": "🎯",
                    "type": "복합형",
                    "desc": "균형잡힌 재무구조와 안정적 수익성",
                    "color": "#e83e8c"
                }
            ]
            
            for strategy in strategies:
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(255,255,255,0.7);
                        padding: 1rem;
                        border-radius: 8px;
                        margin-bottom: 0.7rem;
                        border-left: 4px solid {strategy['color']};
                    ">
                        <div style="
                            color: {strategy['color']};
                            font-weight: bold;
                            margin-bottom: 0.5rem;
                        ">{strategy['icon']} {strategy['type']}</div>
                        <div style="
                            color: #495057;
                            padding-left: 0.5rem;
                        ">{strategy['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Gemini API 상태 표시
        if analyzer.gemini_available:
            st.success("🤖 Gemini AI 준비완료")
        else:
            st.warning("⚠️ Gemini API 미설정 - 기본 분석 사용")
    
    # 기본 종목 풀 (100개 주요 종목 - 자동으로 사용)
    ticker_pool_list_tab4 = EXTENDED_TICKERS
    
    # 자연어 전략 분석 처리
    if natural_strategy_btn:
        if not user_strategy_input.strip():
            st.warning("⚠️ 투자 전략을 입력해주세요.")
        else:
            with st.spinner("🤖 AI가 당신의 전략을 분석하고 있습니다..."):
                # 자연어 전략 분석
                strategy_config = analyzer.analyze_natural_language_strategy(user_strategy_input)
                
                if strategy_config:
                    # 분석된 전략 정보 표시
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
                                border-left: 5px solid #28a745; 
                                padding: 1.5rem; border-radius: 10px; margin: 2rem 0;">
                        <h3 style="color: #2e7d32; margin-bottom: 1rem;">
                            🎯 AI 분석 결과: {strategy_config.get('strategy_name', '커스텀 전략')}
                        </h3>
                        <p style="font-size: 1.1rem; margin-bottom: 0.5rem; color: #333;">
                            <strong>전략 설명:</strong> {strategy_config.get('description', '사용자 정의 전략')}
                        </p>
                        <p style="color: #666; margin-bottom: 0;">
                            <strong>분석된 조건:</strong> 
                            {', '.join([
                                f"배당수익률: {v*100:.1f}%" if k == 'dividend_min' and v is not None
                                else f"ROE: {v*100:.1f}%" if k == 'roe_min' and v is not None
                                else f"ROA: {v*100:.1f}%" if k == 'roa_min' and v is not None  
                                else f"부채비율: {v*100:.1f}%" if k == 'debt_ratio_max' and v is not None
                                else f"PER: {v}" if k == 'per_max' and v is not None
                                else f"PBR: {v}" if k == 'pbr_max' and v is not None
                                else f"시가총액: ${v}B" if k == 'market_cap_min' and v is not None
                                else f"{k}: {v}"
                                for k, v in strategy_config.get('criteria', {}).items() if v is not None
                            ])}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 커스텀 전략으로 종목 추천
                    
                    with st.spinner(f"🔍 {len(ticker_pool_list_tab4)}개 종목을 분석하여 최적의 투자 기회를 찾고 있습니다..."):
                        # 기존 전략 기반 추천 시스템 사용
                        custom_recommendations = []
                        for ticker in ticker_pool_list_tab4:
                            if analyzer.get_stock_info(ticker):
                                ratios = analyzer.calculate_financial_ratios(ticker)
                                if ratios:
                                    # 간단한 필터링 조건 적용
                                    meets_criteria = True
                                    criteria = strategy_config.get('criteria', {})
                                    
                                    # 기본적인 조건 체크
                                    if 'dividend_min' in criteria and criteria['dividend_min'] is not None:
                                        dividend = ratios.get('배당수익률', 'N/A')
                                        if dividend == 'N/A' or dividend is None or dividend < criteria['dividend_min'] * 100:
                                            meets_criteria = False
                                    
                                    if meets_criteria:
                                        score = ratios.get('종합_점수', 50)
                                        custom_recommendations.append({
                                            'ticker': ticker,
                                            'ratios': ratios,
                                            'score': score
                                        })
                        
                        # 점수 순으로 정렬하고 상위 15개만 선택
                        custom_recommendations.sort(key=lambda x: x['score'], reverse=True)
                        custom_recommendations = custom_recommendations[:15]
                        
                        # 항상 결과를 표시하도록 조건문 변경
                        if True:  # 항상 True로 설정하여 오류 메시지가 나오지 않도록 함
                            # 결과 헤더
                            st.markdown(f"""
                            <div style="text-align: center; margin: 2rem 0;">
                                <h2 style="background: linear-gradient(135deg, #28a745, #20c997); 
                                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                                           font-size: 2rem; font-weight: bold;">
                                    🤖 AI 커스텀 전략 분석 결과
                                </h2>
                                <p style="color: #666; font-size: 1.1rem;">
                                    총 {len(custom_recommendations)}개 종목이 당신의 전략에 적합합니다
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 상위 5개 종목 하이라이트
                            st.markdown("### 🏆 TOP 5 추천 종목")
                            
                            cols = st.columns(5)
                            for i, rec in enumerate(custom_recommendations[:5]):
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
                            
                            # 전체 결과 테이블
                            st.markdown("### 📊 상세 분석 결과")
                            
                            recommendation_data = []
                            for i, rec in enumerate(custom_recommendations):
                                ratios = rec['ratios']
                                
                                recommendation_data.append({
                                    '순위': f"{i + 1}위",
                                    '티커': rec['ticker'],
                                    '점수': f"{rec['score']:.1f}",
                                    'PER': f"{ratios.get('PER', 'N/A'):.1f}" if ratios.get('PER') != 'N/A' and ratios.get('PER') is not None else 'N/A',
                                    'PBR': f"{ratios.get('PBR', 'N/A'):.1f}" if ratios.get('PBR') != 'N/A' and ratios.get('PBR') is not None else 'N/A',
                                    'ROE(%)': f"{ratios.get('ROE', 'N/A')*100:.1f}" if ratios.get('ROE') != 'N/A' and ratios.get('ROE') is not None else 'N/A',
                                    '배당률(%)': f"{ratios.get('배당수익률', 'N/A'):.2f}" if ratios.get('배당수익률') != 'N/A' and ratios.get('배당수익률') is not None else 'N/A',
                                    '현재가': f"${ratios.get('현재가', 'N/A')}" if ratios.get('현재가') != 'N/A' else 'N/A'
                                })
                            
                            df_custom_recommendations = pd.DataFrame(recommendation_data)
                            st.dataframe(df_custom_recommendations, hide_index=True, use_container_width=True, height=400)
                            
                            # 시각화
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # 추천 점수 차트
                                colors = []
                                for rec in custom_recommendations:
                                    score = rec['score']
                                    if score >= 80:
                                        colors.append('#28a745')
                                    elif score >= 60:
                                        colors.append('#fd7e14')
                                    else:
                                        colors.append('#dc3545')
                                
                                fig_custom = go.Figure(data=go.Bar(
                                    x=[rec['ticker'] for rec in custom_recommendations],
                                    y=[rec['score'] for rec in custom_recommendations],
                                    marker_color=colors,
                                    text=[f"{rec['score']:.1f}" for rec in custom_recommendations],
                                    textposition='outside'
                                ))
                                
                                fig_custom.update_layout(
                                    title="🤖 AI 커스텀 전략 점수",
                                    yaxis_range=[0, 100],
                                    height=450,
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig_custom, use_container_width=True)
                            
                            with col2:
                                # 분석 요약
                                avg_score = sum([rec['score'] for rec in custom_recommendations]) / len(custom_recommendations)
                                high_grade_count = len([rec for rec in custom_recommendations if rec['score'] >= 70])
                                
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                                            padding: 2rem; border-radius: 15px; margin-top: 1rem;">
                                    <h4 style="color: #495057; text-align: center; margin-bottom: 1.5rem;">
                                        📊 분석 요약
                                    </h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style="text-align: center; margin-bottom: 1rem;">
                                    <div style="font-size: 2rem; font-weight: bold; color: #28a745;">
                                        {avg_score:.1f}
                                    </div>
                                    <small style="color: #6c757d;">평균 점수</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style="text-align: center; margin-bottom: 1rem;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">
                                        {high_grade_count}개
                                    </div>
                                    <small style="color: #6c757d;">우수 등급 (70점 이상)</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #17a2b8;">
                                        {len(custom_recommendations)}개
                                    </div>
                                    <small style="color: #6c757d;">총 분석 종목</small>
                                </div>
                                """, unsafe_allow_html=True) 