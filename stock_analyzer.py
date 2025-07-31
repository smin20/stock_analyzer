import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
import json
import re
import pickle
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# 환경변수 로드
load_dotenv()

class StockAnalyzer:
    def __init__(self, cache_dir="stock_cache", cache_days=1, api_key=None):
        self.stock_data = {}
        self.cache_dir = Path(cache_dir)
        self.cache_days = cache_days
        
        # 캐시 디렉토리 생성
        self.cache_dir.mkdir(exist_ok=True)
        
        # Gemini API 초기화
        try:
            # API 키 우선순위: 1) 매개변수로 전달된 키, 2) 환경변수
            if not api_key:
                api_key = os.getenv('GEMINI_API_KEY')
            
            if api_key and api_key != 'your_gemini_api_key_here':
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_available = True
            else:
                self.gemini_available = False
        except Exception as e:
            self.gemini_available = False
    
    def _get_cache_path(self, ticker, data_type="info"):
        """캐시 파일 경로 생성"""
        return self.cache_dir / f"{ticker}_{data_type}.pkl"
    
    def _is_cache_valid(self, cache_path):
        """캐시 파일이 유효한지 확인 (날짜 기준)"""
        if not cache_path.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < timedelta(days=self.cache_days)
    
    def _save_to_cache(self, ticker, data, data_type="info"):
        """데이터를 캐시 파일로 저장"""
        try:
            cache_path = self._get_cache_path(ticker, data_type)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"캐시 저장 실패 ({ticker}): {e}")
    
    def _load_from_cache(self, ticker, data_type="info"):
        """캐시 파일에서 데이터 로드"""
        try:
            cache_path = self._get_cache_path(ticker, data_type)
            if self._is_cache_valid(cache_path):
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"캐시 로드 실패 ({ticker}): {e}")
        return None
    
    def preload_tickers(self, tickers, show_progress=True):
        """여러 종목의 데이터를 미리 로드하여 캐시에 저장"""
        print(f"📦 {len(tickers)}개 종목 데이터 캐싱 중...")
        
        loaded_count = 0
        cached_count = 0
        failed_count = 0
        
        for i, ticker in enumerate(tickers):
            if show_progress and (i + 1) % 10 == 0:
                print(f"진행상황: {i + 1}/{len(tickers)} ({(i + 1)/len(tickers)*100:.1f}%)")
            
            # 캐시에서 확인
            cached_data = self._load_from_cache(ticker)
            if cached_data:
                self.stock_data[ticker] = cached_data
                cached_count += 1
                continue
            
            # API에서 새로 로드
            if self._fetch_and_cache_stock_data(ticker):
                loaded_count += 1
            else:
                failed_count += 1
        
        print(f"✅ 캐싱 완료!")
        print(f"   📁 캐시에서 로드: {cached_count}개")
        print(f"   🌐 API에서 로드: {loaded_count}개")
        print(f"   ❌ 실패: {failed_count}개")
        print(f"   🚀 총 사용 가능: {len(self.stock_data)}개")
    
    def _fetch_and_cache_stock_data(self, ticker):
        """단일 종목 데이터를 API에서 가져와서 캐시에 저장"""
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
            
            stock_data = {
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'price_history': hist_data,
                'last_updated': datetime.now()
            }
            
            # 메모리와 캐시에 저장
            self.stock_data[ticker] = stock_data
            self._save_to_cache(ticker, stock_data)
            
            return True
            
        except Exception as e:
            print(f"데이터 수집 실패 ({ticker}): {e}")
            return False
    
    def get_stock_info(self, ticker):
        """주식 기본 정보 및 재무 데이터 수집 (캐시 우선 사용)"""
        # 이미 메모리에 로드되어 있는지 확인
        if ticker in self.stock_data:
            return True
        
        # 캐시에서 로드 시도
        cached_data = self._load_from_cache(ticker)
        if cached_data:
            self.stock_data[ticker] = cached_data
            return True
        
        # 캐시에 없으면 API에서 가져와서 캐시에 저장
        return self._fetch_and_cache_stock_data(ticker)
    
    def get_cache_info(self):
        """캐시 상태 정보 반환"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        valid_cache = []
        expired_cache = []
        
        for cache_file in cache_files:
            if self._is_cache_valid(cache_file):
                valid_cache.append(cache_file)
            else:
                expired_cache.append(cache_file)
        
        return {
            'cache_dir': str(self.cache_dir),
            'total_files': len(cache_files),
            'valid_files': len(valid_cache),
            'expired_files': len(expired_cache),
            'cache_days': self.cache_days,
            'memory_loaded': len(self.stock_data)
        }
    
    def clear_cache(self, expired_only=True):
        """캐시 파일 정리"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        deleted_count = 0
        
        for cache_file in cache_files:
            should_delete = not expired_only or not self._is_cache_valid(cache_file)
            if should_delete:
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"캐시 파일 삭제 실패 {cache_file}: {e}")
        
        if expired_only:
            print(f"만료된 캐시 {deleted_count}개 파일을 삭제했습니다.")
        else:
            print(f"모든 캐시 {deleted_count}개 파일을 삭제했습니다.")
            self.stock_data.clear()  # 메모리도 초기화
        
        return deleted_count
    
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
            if dividend_yield > 3.0:  # 3% 이상
                score += 15
            elif dividend_yield > 2.0:  # 2% 이상
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
            if dividend_yield > 5.0:  # 5% 이상
                score += 40
            elif dividend_yield > 4.0:  # 4% 이상
                score += 30
            elif dividend_yield > 3.0:  # 3% 이상
                score += 20
            elif dividend_yield > 2.0:  # 2% 이상
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
    
    def get_company_description(self, ticker):
        """Gemini AI를 사용한 회사 설명 생성"""
        if not self.gemini_available:
            return "Gemini API가 설정되지 않아 회사 설명을 생성할 수 없습니다."
        
        try:
            prompt = f"""
{ticker} 종목에 대해서 간단하고 명확한 회사 설명을 3-4줄로 작성해주세요.

다음 내용을 포함해주세요:
1. 회사의 주요 사업 분야
2. 어떤 제품이나 서비스를 제공하는지
3. 업계에서의 위치나 특징

한국어로 작성하고, 투자자가 이해하기 쉽게 간결하고 명확하게 설명해주세요.
예시 형태: "Apple Inc.(AAPL)은 아이폰, 맥, 아이패드 등의 혁신적인 전자제품을 설계, 제조, 판매하는 글로벌 기술 기업입니다. iOS와 macOS 운영체제, App Store 등의 소프트웨어 플랫폼도 운영하며, 전 세계적으로 강력한 브랜드 충성도를 보유하고 있습니다."

{ticker} 회사 설명:
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # 응답이 너무 길면 줄여서 반환
            lines = response_text.split('\n')
            filtered_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('##')]
            
            if len(filtered_lines) > 4:
                filtered_lines = filtered_lines[:4]
            
            return ' '.join(filtered_lines)
            
        except Exception as e:
            print(f"❌ Gemini API 회사 설명 생성 실패: {e}")
            return f"{ticker} 종목에 대한 상세 정보를 불러오는 중 오류가 발생했습니다."

    def analyze_natural_language_strategy(self, user_input):
        """Gemini AI를 사용한 투자 전략 분석 (LLM 전용)"""
        if not self.gemini_available:
            return {
                "strategy_name": "API 없음",
                "criteria": {},
                "weights": {"value_focus": 25, "growth_focus": 25, "dividend_focus": 25, "quality_focus": 25},
                "description": "Gemini API가 설정되지 않았습니다. .env 파일에 GEMINI_API_KEY를 설정해주세요."
            }
        
        try:
            prompt = f"""
당신은 전문 투자 분석가입니다. 다음 사용자의 투자 전략을 정밀하게 분석하여 정확한 수치로 변환해주세요.

사용자 입력: "{user_input}"

다음 JSON 형태로만 응답하세요 (코드블록, 설명, 주석 없이 순수 JSON만):
{{
    "strategy_name": "분석된 전략명",
    "criteria": {{
        "per_max": null or 숫자,
        "per_min": null or 숫자,
        "pbr_max": null or 숫자,
        "pbr_min": null or 숫자,
        "roe_min": null or 0.0-1.0 사이 소수 (예: 0.15는 15%),
        "roa_min": null or 0.0-1.0 사이 소수,
        "dividend_min": null or 0.0-1.0 사이 소수 (예: 0.045는 4.5%),
        "debt_ratio_max": null or 0.0-1.0 사이 소수,
        "market_cap_min": null or 숫자 (십억달러 단위),
        "price_to_52week_high_min": null or 0.0-1.0 사이 소수
    }},
    "weights": {{
        "value_focus": 0-100 정수,
        "growth_focus": 0-100 정수,
        "dividend_focus": 0-100 정수,
        "quality_focus": 0-100 정수
    }},
    "description": "추출된 전략 요약"
}}

*** 중요한 수치 변환 규칙 ***
- 배당수익률: "4.5%" → dividend_min: 0.045
- 배당수익률: "3%" → dividend_min: 0.03
- 배당수익률: "6%" → dividend_min: 0.06
- ROE: "20%" → roe_min: 0.2
- ROE: "15%" → roe_min: 0.15
- ROA: "8%" → roa_min: 0.08
- 부채비율: "60%" → debt_ratio_max: 0.6

*** 정확한 예시 ***
1. "배당수익률 3% 이상인 안정 대형주"
   → {{"dividend_min": 0.03, "market_cap_min": 50, "debt_ratio_max": 0.6}}

2. "PER 12 이하, 배당 2.5% 이상"
   → {{"per_max": 12, "dividend_min": 0.025}}

3. "ROE 15% 이상, 배당수익률 3% 이상인 우량주"
   → {{"roe_min": 0.15, "dividend_min": 0.03, "debt_ratio_max": 0.5}}

*** 현실적인 기준 가이드 ***
- 배당수익률: 미국 대형주는 보통 2-4% (REITs 제외)
- 시가총액: 중형주 50억$, 대형주 100억$, 초대형주 500억$ 이상
- "시가총액이 큰" = 100억$ 이상, "매우 큰" = 500억$ 이상으로 해석
- ROE: 우수한 기업은 15% 이상, 매우 우수한 기업은 20% 이상
- PER: 적정한 PER은 업종에 따라 다르지만 보통 10-25배
- 안정적인 배당주는 보통 배당수익률 2.5-4%, 시총 50억$ 이상

퍼센트(%)를 소수로 정확히 변환하는 것이 가장 중요합니다!
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # 코드 블록 제거
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            # JSON 파싱
            strategy_config = json.loads(response_text)
            
            # 검증 및 보정
            if 'criteria' not in strategy_config:
                strategy_config['criteria'] = {}
            if 'weights' not in strategy_config:
                strategy_config['weights'] = {"value_focus": 25, "growth_focus": 25, "dividend_focus": 25, "quality_focus": 25}
            
            # weights 합계가 100이 되도록 조정
            total_weight = sum(strategy_config['weights'].values())
            if total_weight > 0:
                for key in strategy_config['weights']:
                    strategy_config['weights'][key] = int(strategy_config['weights'][key] * 100 / total_weight)
            
            print(f"✅ Gemini 분석 성공: {strategy_config.get('strategy_name', '커스텀 전략')}")
            return strategy_config
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"응답 텍스트: {response_text[:200]}...")
            return None
            
        except Exception as e:
            print(f"❌ Gemini API 분석 실패: {e}")
            return None
    

    def _meets_required_criteria(self, ratios, strategy_config):
        """필수 조건을 만족하는지 체크"""
        criteria = strategy_config.get('criteria', {})
        
        # PER 최대값 체크
        if 'per_max' in criteria and criteria['per_max'] is not None:
            per = ratios.get('PER', 'N/A')
            if per == 'N/A' or per is None or per <= 0 or per > criteria['per_max']:
                return False
        
        # PER 최소값 체크
        if 'per_min' in criteria and criteria['per_min'] is not None:
            per = ratios.get('PER', 'N/A')
            if per == 'N/A' or per is None or per <= 0 or per < criteria['per_min']:
                return False
        
        # PBR 최대값 체크
        if 'pbr_max' in criteria and criteria['pbr_max'] is not None:
            pbr = ratios.get('PBR', 'N/A')
            if pbr == 'N/A' or pbr is None or pbr <= 0 or pbr > criteria['pbr_max']:
                return False
        
        # PBR 최소값 체크
        if 'pbr_min' in criteria and criteria['pbr_min'] is not None:
            pbr = ratios.get('PBR', 'N/A')
            if pbr == 'N/A' or pbr is None or pbr <= 0 or pbr < criteria['pbr_min']:
                return False
        
        # ROE 최소값 체크
        if 'roe_min' in criteria and criteria['roe_min'] is not None:
            roe = ratios.get('ROE', 'N/A')
            if roe == 'N/A' or roe is None or roe < criteria['roe_min']:
                return False
        
        # ROA 최소값 체크
        if 'roa_min' in criteria and criteria['roa_min'] is not None:
            roa = ratios.get('ROA', 'N/A')
            if roa == 'N/A' or roa is None or roa < criteria['roa_min']:
                return False
        
        # 배당수익률 최소값 체크 (퍼센트 단위)
        if 'dividend_min' in criteria and criteria['dividend_min'] is not None:
            dividend = ratios.get('배당수익률', 'N/A')
            dividend_min_percent = criteria['dividend_min'] * 100  # 소수를 퍼센트로 변환
            if dividend == 'N/A' or dividend is None or dividend < dividend_min_percent:
                return False
        
        # 부채비율 최대값 체크
        if 'debt_ratio_max' in criteria and criteria['debt_ratio_max'] is not None:
            debt_ratio = ratios.get('부채비율', 'N/A')
            if debt_ratio == 'N/A' or debt_ratio is None:
                return False, "부채비율 데이터 없음"
            # criteria의 debt_ratio_max는 소수 형태(0.6)이므로 100을 곱해서 퍼센트로 변환
            debt_ratio_max_percent = criteria['debt_ratio_max'] * 100
            if debt_ratio > debt_ratio_max_percent:
                return False, f"부채비율 높음 ({debt_ratio:.1f}% > {debt_ratio_max_percent:.1f}%)"
        
        # 시가총액 최소값 체크 (십억 달러 단위)
        if 'market_cap_min' in criteria and criteria['market_cap_min'] is not None:
            market_cap = ratios.get('시가총액', 'N/A')
            if market_cap == 'N/A' or market_cap is None:
                return False, "시가총액 데이터 없음"
            market_cap_b = market_cap / 1e9  # 십억 단위로 변환
            if market_cap_b < criteria['market_cap_min']:
                return False, f"시가총액 작음 (${market_cap_b:.1f}B < ${criteria['market_cap_min']:.1f}B)"
        
        # 52주 최고가 대비 현재가 최소값 체크
        if 'price_to_52week_high_min' in criteria and criteria['price_to_52week_high_min'] is not None:
            price_ratio = ratios.get('52주_고점대비', 'N/A')
            if price_ratio == 'N/A' or price_ratio is None:
                return False, "52주 가격비율 데이터 없음"
            if price_ratio / 100 < criteria['price_to_52week_high_min']:
                return False, f"52주 가격비율 낮음 ({price_ratio:.1f}% < {criteria['price_to_52week_high_min']*100:.1f}%)"
        
        return True, "모든 조건 만족"  # 모든 조건을 만족함
    
    def _meets_required_criteria_with_reason(self, ratios, strategy_config):
        """필수 조건을 만족하는지 체크하고 실패 이유도 반환"""
        criteria = strategy_config.get('criteria', {})
        
        # PER 최대값 체크
        if 'per_max' in criteria and criteria['per_max'] is not None:
            per = ratios.get('PER', 'N/A')
            if per == 'N/A' or per is None or per <= 0:
                return False, "PER 데이터 없음"
            if per > criteria['per_max']:
                return False, f"PER 높음 ({per:.1f} > {criteria['per_max']})"
        
        # PER 최소값 체크
        if 'per_min' in criteria and criteria['per_min'] is not None:
            per = ratios.get('PER', 'N/A')
            if per == 'N/A' or per is None or per <= 0:
                return False, "PER 데이터 없음"
            if per < criteria['per_min']:
                return False, f"PER 낮음 ({per:.1f} < {criteria['per_min']})"
        
        # PBR 최대값 체크
        if 'pbr_max' in criteria and criteria['pbr_max'] is not None:
            pbr = ratios.get('PBR', 'N/A')
            if pbr == 'N/A' or pbr is None or pbr <= 0:
                return False, "PBR 데이터 없음"
            if pbr > criteria['pbr_max']:
                return False, f"PBR 높음 ({pbr:.1f} > {criteria['pbr_max']})"
        
        # PBR 최소값 체크
        if 'pbr_min' in criteria and criteria['pbr_min'] is not None:
            pbr = ratios.get('PBR', 'N/A')
            if pbr == 'N/A' or pbr is None or pbr <= 0:
                return False, "PBR 데이터 없음"
            if pbr < criteria['pbr_min']:
                return False, f"PBR 낮음 ({pbr:.1f} < {criteria['pbr_min']})"
        
        # ROE 최소값 체크
        if 'roe_min' in criteria and criteria['roe_min'] is not None:
            roe = ratios.get('ROE', 'N/A')
            if roe == 'N/A' or roe is None:
                return False, "ROE 데이터 없음"
            if roe < criteria['roe_min']:
                return False, f"ROE 낮음 ({roe*100:.1f}% < {criteria['roe_min']*100:.1f}%)"
        
        # ROA 최소값 체크
        if 'roa_min' in criteria and criteria['roa_min'] is not None:
            roa = ratios.get('ROA', 'N/A')
            if roa == 'N/A' or roa is None:
                return False, "ROA 데이터 없음"
            if roa < criteria['roa_min']:
                return False, f"ROA 낮음 ({roa*100:.1f}% < {criteria['roa_min']*100:.1f}%)"
        
        # 배당수익률 최소값 체크 (퍼센트 단위)
        if 'dividend_min' in criteria and criteria['dividend_min'] is not None:
            dividend = ratios.get('배당수익률', 'N/A')
            dividend_min_percent = criteria['dividend_min'] * 100  # 소수를 퍼센트로 변환
            if dividend == 'N/A' or dividend is None:
                return False, "배당수익률 데이터 없음"
            if dividend < dividend_min_percent:
                return False, f"배당수익률 낮음 ({dividend:.2f}% < {dividend_min_percent:.2f}%)"
        
        # 부채비율 최대값 체크
        if 'debt_ratio_max' in criteria and criteria['debt_ratio_max'] is not None:
            debt_ratio = ratios.get('부채비율', 'N/A')
            if debt_ratio == 'N/A' or debt_ratio is None:
                return False, "부채비율 데이터 없음"
            # criteria의 debt_ratio_max는 소수 형태(0.6)이므로 100을 곱해서 퍼센트로 변환
            debt_ratio_max_percent = criteria['debt_ratio_max'] * 100
            if debt_ratio > debt_ratio_max_percent:
                return False, f"부채비율 높음 ({debt_ratio:.1f}% > {debt_ratio_max_percent:.1f}%)"
        
        # 시가총액 최소값 체크 (십억 달러 단위)
        if 'market_cap_min' in criteria and criteria['market_cap_min'] is not None:
            market_cap = ratios.get('시가총액', 'N/A')
            if market_cap == 'N/A' or market_cap is None:
                return False, "시가총액 데이터 없음"
            market_cap_b = market_cap / 1e9  # 십억 단위로 변환
            if market_cap_b < criteria['market_cap_min']:
                return False, f"시가총액 작음 (${market_cap_b:.1f}B < ${criteria['market_cap_min']:.1f}B)"
        
        # 52주 최고가 대비 현재가 최소값 체크
        if 'price_to_52week_high_min' in criteria and criteria['price_to_52week_high_min'] is not None:
            price_ratio = ratios.get('52주_고점대비', 'N/A')
            if price_ratio == 'N/A' or price_ratio is None:
                return False, "52주 가격비율 데이터 없음"
            if price_ratio / 100 < criteria['price_to_52week_high_min']:
                return False, f"52주 가격비율 낮음 ({price_ratio:.1f}% < {criteria['price_to_52week_high_min']*100:.1f}%)"
        
        return True, "모든 조건 만족"  # 모든 조건을 만족함
    
    def _calculate_custom_strategy_score(self, ratios, strategy_config):
        """커스텀 전략에 따른 점수 계산"""
        score = 50  # 기본 점수
        criteria = strategy_config.get('criteria', {})
        weights = strategy_config.get('weights', {})
        
        # 각 기준별 점수 계산
        
        # PER 기준
        per = ratios.get('PER', 'N/A')
        if per != 'N/A' and per is not None and per > 0:
            if 'per_max' in criteria and criteria['per_max']:
                if per <= criteria['per_max']:
                    score += 20 * (weights.get('value_focus', 25) / 100)
                elif per > criteria['per_max'] * 1.5:
                    score -= 15
            
            if 'per_min' in criteria and criteria['per_min']:
                if per >= criteria['per_min']:
                    score += 15 * (weights.get('value_focus', 25) / 100)
        
        # PBR 기준
        pbr = ratios.get('PBR', 'N/A')
        if pbr != 'N/A' and pbr is not None and pbr > 0:
            if 'pbr_max' in criteria and criteria['pbr_max']:
                if pbr <= criteria['pbr_max']:
                    score += 15 * (weights.get('value_focus', 25) / 100)
                elif pbr > criteria['pbr_max'] * 1.5:
                    score -= 10
        
        # ROE 기준
        roe = ratios.get('ROE', 'N/A')
        if roe != 'N/A' and roe is not None:
            if 'roe_min' in criteria and criteria['roe_min']:
                if roe >= criteria['roe_min']:
                    score += 25 * (weights.get('quality_focus', 25) / 100)
                elif roe < criteria['roe_min'] * 0.7:
                    score -= 20
        
        # ROA 기준
        roa = ratios.get('ROA', 'N/A')
        if roa != 'N/A' and roa is not None:
            if 'roa_min' in criteria and criteria['roa_min']:
                if roa >= criteria['roa_min']:
                    score += 15 * (weights.get('quality_focus', 25) / 100)
        
        # 배당 기준
        dividend = ratios.get('배당수익률', 'N/A')
        if dividend != 'N/A' and dividend is not None:
            if 'dividend_min' in criteria and criteria['dividend_min']:
                # criteria의 dividend_min은 소수점 형태(0.03)이므로 100을 곱해서 퍼센트로 변환
                dividend_min_percent = criteria['dividend_min'] * 100
                if dividend >= dividend_min_percent:
                    score += 30 * (weights.get('dividend_focus', 25) / 100)
                elif dividend < dividend_min_percent * 0.5:
                    score -= 15
        
        # 부채비율 기준
        debt_ratio = ratios.get('부채비율', 'N/A')
        if debt_ratio != 'N/A' and debt_ratio is not None:
            if 'debt_ratio_max' in criteria and criteria['debt_ratio_max']:
                # criteria의 debt_ratio_max는 소수 형태(0.6)이므로 100을 곱해서 퍼센트로 변환
                debt_ratio_max_percent = criteria['debt_ratio_max'] * 100
                if debt_ratio <= debt_ratio_max_percent:
                    score += 15 * (weights.get('quality_focus', 25) / 100)
                elif debt_ratio > debt_ratio_max_percent * 1.5:
                    score -= 20
        
        # 시가총액 기준 (십억 달러 단위)
        market_cap = ratios.get('시가총액', 'N/A')
        if market_cap != 'N/A' and market_cap is not None:
            market_cap_b = market_cap / 1e9  # 십억 단위로 변환
            if 'market_cap_min' in criteria and criteria['market_cap_min']:
                if market_cap_b >= criteria['market_cap_min']:
                    score += 10 * (weights.get('quality_focus', 25) / 100)
        
        # 52주 최고가 대비 현재가 기준
        price_ratio = ratios.get('52주_고점대비', 'N/A')
        if price_ratio != 'N/A' and price_ratio is not None:
            if 'price_to_52week_high_min' in criteria and criteria['price_to_52week_high_min']:
                if price_ratio / 100 >= criteria['price_to_52week_high_min']:
                    score += 15 * (weights.get('growth_focus', 25) / 100)
        
        return max(0, min(100, score))

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