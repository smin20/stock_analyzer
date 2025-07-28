import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        self.stock_data = {}
        
    def get_stock_info(self, ticker):
        """주식 기본 정보 및 재무 데이터 수집"""
        try:
            stock = yf.Ticker(ticker)
            
            # 기본 정보
            info = stock.info
            
            # 재무제표 데이터
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # 주가 데이터 (최근 1년)
            hist_data = stock.history(period="1y")
            
            self.stock_data[ticker] = {
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'price_history': hist_data
            }
            
            return True
            
        except Exception as e:
            print(f"데이터 수집 실패 ({ticker}): {e}")
            return False
    
    def calculate_financial_ratios(self, ticker):
        """주요 재무비율 계산"""
        if ticker not in self.stock_data:
            print(f"{ticker} 데이터가 없습니다. 먼저 get_stock_info()를 실행하세요.")
            return None
            
        data = self.stock_data[ticker]
        info = data['info']
        
        ratios = {}
        
        try:
            # 기본 정보에서 추출 가능한 지표들
            ratios['현재가'] = info.get('currentPrice', 'N/A')
            ratios['시가총액'] = info.get('marketCap', 'N/A')
            ratios['PER'] = info.get('forwardPE', info.get('trailingPE', 'N/A'))
            ratios['PBR'] = info.get('priceToBook', 'N/A')
            ratios['PSR'] = info.get('priceToSalesTrailing12Months', 'N/A')
            ratios['ROE'] = info.get('returnOnEquity', 'N/A')
            ratios['ROA'] = info.get('returnOnAssets', 'N/A')
            ratios['부채비율'] = info.get('debtToEquity', 'N/A')
            ratios['배당수익률'] = info.get('dividendYield', 'N/A')
            ratios['52주_최고가'] = info.get('fiftyTwoWeekHigh', 'N/A')
            ratios['52주_최저가'] = info.get('fiftyTwoWeekLow', 'N/A')
            
            # 추가 계산 지표들
            if 'N/A' not in [ratios['현재가'], ratios['52주_최고가'], ratios['52주_최저가']]:
                ratios['52주_고점대비'] = round((ratios['현재가'] / ratios['52주_최고가']) * 100, 2)
                ratios['52주_저점대비'] = round((ratios['현재가'] / ratios['52주_최저가']) * 100, 2)
            
            # 수익성 등급 계산
            ratios['수익성_점수'] = self._calculate_profitability_score(ratios)
            ratios['안정성_점수'] = self._calculate_stability_score(ratios)
            ratios['가치평가_점수'] = self._calculate_valuation_score(ratios)
            ratios['종합_점수'] = round((ratios['수익성_점수'] + ratios['안정성_점수'] + ratios['가치평가_점수']) / 3, 1)
            
        except Exception as e:
            print(f"재무비율 계산 중 오류: {e}")
            
        return ratios
    
    def _calculate_profitability_score(self, ratios):
        """수익성 점수 계산 (0-100)"""
        score = 50  # 기본 점수
        
        # ROE 점수
        roe = ratios.get('ROE', 'N/A')
        if roe != 'N/A' and roe is not None:
            if roe > 0.20:  # 20% 이상
                score += 20
            elif roe > 0.15:  # 15% 이상
                score += 15
            elif roe > 0.10:  # 10% 이상
                score += 10
            elif roe < 0:  # 음수
                score -= 20
                
        # ROA 점수
        roa = ratios.get('ROA', 'N/A')
        if roa != 'N/A' and roa is not None:
            if roa > 0.10:  # 10% 이상
                score += 15
            elif roa > 0.05:  # 5% 이상
                score += 10
            elif roa < 0:  # 음수
                score -= 15
                
        return max(0, min(100, score))
    
    def _calculate_stability_score(self, ratios):
        """안정성 점수 계산 (0-100)"""
        score = 50  # 기본 점수
        
        # 부채비율 점수
        debt_ratio = ratios.get('부채비율', 'N/A')
        if debt_ratio != 'N/A' and debt_ratio is not None:
            if debt_ratio < 0.3:  # 30% 미만
                score += 20
            elif debt_ratio < 0.5:  # 50% 미만
                score += 10
            elif debt_ratio > 1.0:  # 100% 초과
                score -= 20
                
        # 배당수익률 점수 (안정성 지표로 활용)
        dividend_yield = ratios.get('배당수익률', 'N/A')
        if dividend_yield != 'N/A' and dividend_yield is not None:
            if dividend_yield > 0.03:  # 3% 이상
                score += 15
            elif dividend_yield > 0.02:  # 2% 이상
                score += 10
                
        return max(0, min(100, score))
    
    def _calculate_valuation_score(self, ratios):
        """가치평가 점수 계산 (0-100)"""
        score = 50  # 기본 점수
        
        # PER 점수
        per = ratios.get('PER', 'N/A')
        if per != 'N/A' and per is not None and per > 0:
            if per < 10:  # 저평가
                score += 20
            elif per < 15:
                score += 15
            elif per < 20:
                score += 10
            elif per > 30:  # 고평가
                score -= 15
                
        # PBR 점수
        pbr = ratios.get('PBR', 'N/A')
        if pbr != 'N/A' and pbr is not None and pbr > 0:
            if pbr < 1:  # 저평가
                score += 15
            elif pbr < 1.5:
                score += 10
            elif pbr > 3:  # 고평가
                score -= 10
                
        return max(0, min(100, score))
    
    def get_recommendation(self, ticker):
        """종목 추천 의견 생성"""
        ratios = self.calculate_financial_ratios(ticker)
        if not ratios:
            return None
            
        score = ratios.get('종합_점수', 0)
        
        if score >= 80:
            recommendation = "강력 매수"
            reason = "뛰어난 재무 성과와 합리적인 밸류에이션"
        elif score >= 70:
            recommendation = "매수"
            reason = "양호한 재무 지표와 적정한 가격"
        elif score >= 60:
            recommendation = "보유"
            reason = "평균적인 재무 성과, 추가 관찰 필요"
        elif score >= 40:
            recommendation = "관망"
            reason = "다소 아쉬운 재무 지표, 신중한 접근 필요"
        else:
            recommendation = "매도"
            reason = "약한 재무 성과 또는 높은 밸류에이션"
            
        return {
            'ticker': ticker,
            'recommendation': recommendation,
            'score': score,
            'reason': reason,
            'ratios': ratios
        }
    
    def compare_stocks(self, tickers):
        """여러 종목 비교 분석"""
        results = []
        
        for ticker in tickers:
            if self.get_stock_info(ticker):
                recommendation = self.get_recommendation(ticker)
                if recommendation:
                    results.append(recommendation)
        
        # 점수 순으로 정렬
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def strategy_recommend(self, tickers, strategy='comprehensive'):
        """투자 전략별 종목 추천"""
        results = []
        
        for ticker in tickers:
            if self.get_stock_info(ticker):
                ratios = self.calculate_financial_ratios(ticker)
                if ratios:
                    result = {
                        'ticker': ticker,
                        'ratios': ratios,
                        'score': self._calculate_strategy_score(ratios, strategy)
                    }
                    results.append(result)
        
        # 전략별 점수 순으로 정렬
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # 상위 10개만 반환
        return results[:10]
    
    def _calculate_strategy_score(self, ratios, strategy):
        """전략별 점수 계산"""
        if strategy == 'low_per':
            return self._low_per_strategy(ratios)
        elif strategy == 'low_pbr':
            return self._low_pbr_strategy(ratios)
        elif strategy == 'high_roe':
            return self._high_roe_strategy(ratios)
        elif strategy == 'high_dividend':
            return self._high_dividend_strategy(ratios)
        elif strategy == 'growth':
            return self._growth_strategy(ratios)
        else:  # comprehensive
            return ratios.get('종합_점수', 0)
    
    def _low_per_strategy(self, ratios):
        """저PER 가치투자 전략"""
        score = 50
        per = ratios.get('PER', 'N/A')
        
        if per != 'N/A' and per is not None and per > 0:
            if per < 8:
                score += 40
            elif per < 12:
                score += 30
            elif per < 15:
                score += 20
            elif per < 20:
                score += 10
            elif per > 30:
                score -= 20
        
        # ROE가 양수인지 확인 (수익성 있는 기업)
        roe = ratios.get('ROE', 'N/A')
        if roe != 'N/A' and roe is not None and roe > 0:
            score += 10
        
        return max(0, min(100, score))
    
    def _low_pbr_strategy(self, ratios):
        """저PBR 자산가치 투자 전략"""
        score = 50
        pbr = ratios.get('PBR', 'N/A')
        
        if pbr != 'N/A' and pbr is not None and pbr > 0:
            if pbr < 0.8:
                score += 40
            elif pbr < 1.0:
                score += 30
            elif pbr < 1.5:
                score += 20
            elif pbr < 2.0:
                score += 10
            elif pbr > 4:
                score -= 20
        
        # 부채비율 확인 (건전한 재무구조)
        debt_ratio = ratios.get('부채비율', 'N/A')
        if debt_ratio != 'N/A' and debt_ratio is not None and debt_ratio < 0.5:
            score += 10
        
        return max(0, min(100, score))
    
    def _high_roe_strategy(self, ratios):
        """고ROE 수익성 투자 전략"""
        score = 50
        roe = ratios.get('ROE', 'N/A')
        
        if roe != 'N/A' and roe is not None:
            if roe > 0.25:  # 25% 이상
                score += 40
            elif roe > 0.20:  # 20% 이상
                score += 30
            elif roe > 0.15:  # 15% 이상
                score += 20
            elif roe > 0.10:  # 10% 이상
                score += 10
            elif roe < 0:
                score -= 30
        
        # ROA도 확인
        roa = ratios.get('ROA', 'N/A')
        if roa != 'N/A' and roa is not None and roa > 0.05:
            score += 10
        
        return max(0, min(100, score))
    
    def _high_dividend_strategy(self, ratios):
        """고배당 투자 전략"""
        score = 50
        dividend_yield = ratios.get('배당수익률', 'N/A')
        
        if dividend_yield != 'N/A' and dividend_yield is not None:
            if dividend_yield > 0.05:  # 5% 이상
                score += 40
            elif dividend_yield > 0.04:  # 4% 이상
                score += 30
            elif dividend_yield > 0.03:  # 3% 이상
                score += 20
            elif dividend_yield > 0.02:  # 2% 이상
                score += 10
            else:
                score -= 10
        else:
            score -= 20  # 배당 없음
        
        # 안정성 확인 (배당 지속가능성)
        debt_ratio = ratios.get('부채비율', 'N/A')
        if debt_ratio != 'N/A' and debt_ratio is not None and debt_ratio < 0.6:
            score += 10
        
        return max(0, min(100, score))
    
    def _growth_strategy(self, ratios):
        """성장 투자 전략"""
        score = 50
        
        # ROE 기반 성장성 평가
        roe = ratios.get('ROE', 'N/A')
        if roe != 'N/A' and roe is not None and roe > 0.15:
            score += 20
        
        # PSR로 성장주 특성 확인 (높은 PSR은 성장 기대)
        psr = ratios.get('PSR', 'N/A')
        if psr != 'N/A' and psr is not None:
            if psr > 3 and psr < 8:  # 적당한 성장 프리미엄
                score += 15
            elif psr > 8:  # 과도한 프리미엄
                score -= 10
        
        # 현재가와 52주 최고가 비교 (모멘텀)
        current_vs_high = ratios.get('52주_고점대비', 'N/A')
        if current_vs_high != 'N/A' and current_vs_high > 90:  # 고점 근처
            score += 15
        
        return max(0, min(100, score))
    
    def get_strategy_description(self, strategy):
        """전략 설명 반환"""
        descriptions = {
            'low_per': {
                'name': '저PER 가치투자',
                'description': '낮은 주가수익비율(PER)을 가진 저평가된 우량주를 찾는 전략',
                'criteria': 'PER < 15, ROE > 0'
            },
            'low_pbr': {
                'name': '저PBR 자산가치투자',
                'description': '낮은 주가순자산비율(PBR)을 가진 자산 대비 저평가된 종목을 찾는 전략',
                'criteria': 'PBR < 2.0, 부채비율 < 50%'
            },
            'high_roe': {
                'name': '고ROE 수익성투자',
                'description': '높은 자기자본이익률(ROE)을 가진 수익성이 뛰어난 기업을 찾는 전략',
                'criteria': 'ROE > 15%, ROA > 5%'
            },
            'high_dividend': {
                'name': '고배당 투자',
                'description': '높은 배당수익률을 제공하는 안정적인 배당주를 찾는 전략',
                'criteria': '배당수익률 > 3%, 부채비율 < 60%'
            },
            'growth': {
                'name': '성장주 투자',
                'description': '높은 성장 잠재력을 가진 기업을 찾는 전략',
                'criteria': 'ROE > 15%, 현재가가 52주 최고가 근처'
            },
            'comprehensive': {
                'name': '종합 투자',
                'description': '수익성, 안정성, 가치평가를 종합적으로 고려한 전략',
                'criteria': '종합점수 기준'
            }
        }
        return descriptions.get(strategy, descriptions['comprehensive'])
    
    def get_price_history(self, ticker, period="6mo"):
        """주가 히스토리 데이터 가져오기 (캔들스틱 차트용)"""
        try:
            if ticker not in self.stock_data:
                self.get_stock_info(ticker)
            
            stock = yf.Ticker(ticker)
            hist_data = stock.history(period=period)
            
            if not hist_data.empty:
                # 인덱스를 datetime으로 변환
                hist_data.index = pd.to_datetime(hist_data.index)
                return hist_data
            else:
                return None
                
        except Exception as e:
            print(f"주가 데이터 수집 실패 ({ticker}): {e}")
            return None
    
    def print_analysis(self, ticker):
        """분석 결과 출력"""
        # 먼저 데이터 수집
        if not self.get_stock_info(ticker):
            print(f"{ticker} 분석 실패")
            return
            
        recommendation = self.get_recommendation(ticker)
        if not recommendation:
            print(f"{ticker} 분석 실패")
            return
            
        print(f"\n{'='*50}")
        print(f"📊 {ticker} 주식 분석 결과")
        print(f"{'='*50}")
        
        ratios = recommendation['ratios']
        
        print(f"💰 현재가: ${ratios.get('현재가', 'N/A')}")
        print(f"📈 시가총액: ${ratios.get('시가총액', 'N/A'):,}" if ratios.get('시가총액') != 'N/A' else "📈 시가총액: N/A")
        
        print(f"\n📋 주요 재무비율:")
        print(f"   PER: {ratios.get('PER', 'N/A')}")
        print(f"   PBR: {ratios.get('PBR', 'N/A')}")
        print(f"   PSR: {ratios.get('PSR', 'N/A')}")
        print(f"   ROE: {ratios.get('ROE', 'N/A')}")
        print(f"   ROA: {ratios.get('ROA', 'N/A')}")
        print(f"   부채비율: {ratios.get('부채비율', 'N/A')}")
        print(f"   배당수익률: {ratios.get('배당수익률', 'N/A')}")
        
        print(f"\n📊 종합 평가:")
        print(f"   수익성 점수: {ratios.get('수익성_점수', 'N/A')}/100")
        print(f"   안정성 점수: {ratios.get('안정성_점수', 'N/A')}/100")
        print(f"   가치평가 점수: {ratios.get('가치평가_점수', 'N/A')}/100")
        print(f"   종합 점수: {ratios.get('종합_점수', 'N/A')}/100")
        
        print(f"\n🎯 투자 의견: {recommendation['recommendation']}")
        print(f"💡 근거: {recommendation['reason']}")
        
        # 52주 고저점 정보
        if ratios.get('52주_고점대비') != 'N/A':
            print(f"\n📈 52주 기준:")
            print(f"   최고가 대비: {ratios.get('52주_고점대비', 'N/A')}%")
            print(f"   최저가 대비: {ratios.get('52주_저점대비', 'N/A')}%")

def main():
    """메인 실행 함수"""
    analyzer = StockAnalyzer()
    
    print("🚀 미국 주식 분석기에 오신 것을 환영합니다!")
    print("=" * 50)
    
    while True:
        print("\n옵션을 선택하세요:")
        print("1. 단일 종목 분석")
        print("2. 여러 종목 비교")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            ticker = input("분석할 티커를 입력하세요 (예: AAPL): ").strip().upper()
            if ticker:
                print(f"\n📡 {ticker} 데이터 수집 중...")
                analyzer.print_analysis(ticker)
                
        elif choice == '2':
            tickers_input = input("비교할 티커들을 쉼표로 구분해서 입력하세요 (예: AAPL,MSFT,GOOGL): ").strip()
            if tickers_input:
                tickers = [t.strip().upper() for t in tickers_input.split(',')]
                print(f"\n📡 {len(tickers)}개 종목 데이터 수집 중...")
                
                results = analyzer.compare_stocks(tickers)
                
                print(f"\n{'='*60}")
                print(f"📊 종목 비교 결과 (점수 순)")
                print(f"{'='*60}")
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['ticker']}: {result['recommendation']} (점수: {result['score']}/100)")
                    print(f"   💡 {result['reason']}\n")
                    
        elif choice == '3':
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main() 