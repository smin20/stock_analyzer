#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주식 분석기 테스트 스크립트
"""

from stock_analyzer import StockAnalyzer

def test_single_stock():
    """단일 종목 테스트"""
    print("🧪 단일 종목 분석 테스트 (AAPL)")
    print("=" * 50)
    
    analyzer = StockAnalyzer()
    analyzer.print_analysis("AAPL")

def test_multiple_stocks():
    """여러 종목 비교 테스트"""
    print("\n🧪 여러 종목 비교 테스트 (AAPL, MSFT, GOOGL)")
    print("=" * 60)
    
    analyzer = StockAnalyzer()
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    results = analyzer.compare_stocks(tickers)
    
    print(f"📊 종목 비교 결과 (점수 순)")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['ticker']}: {result['recommendation']} (점수: {result['score']}/100)")
        print(f"   💡 {result['reason']}\n")

if __name__ == "__main__":
    print("🚀 미국 주식 분석기 테스트")
    print("=" * 50)
    
    # 단일 종목 테스트
    test_single_stock()
    
    # 여러 종목 비교 테스트
    test_multiple_stocks()
    
    print("✅ 테스트 완료!") 