#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주식 분석기 빠른 데모
"""

from stock_analyzer import StockAnalyzer

def quick_demo():
    """빠른 데모"""
    print("🚀 미국 주식 분석기 빠른 데모")
    print("=" * 50)
    
    analyzer = StockAnalyzer()
    
    # 테슬라 분석
    print("\n📊 TESLA (TSLA) 분석")
    analyzer.print_analysis("TSLA")
    
    # 네이버 ADR 분석 (한국 기업의 미국 상장 주식)
    print("\n📊 MSFT 분석")
    analyzer.print_analysis("MSFT")
    
    # 테크 대장주 비교
    print("\n📊 테크 대장주 비교 (AAPL vs MSFT vs AMZN)")
    results = analyzer.compare_stocks(["AAPL", "MSFT", "AMZN"])
    
    print("=" * 60)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['ticker']}: {result['recommendation']} (점수: {result['score']}/100)")
        print(f"   💡 {result['reason']}")
        if i < len(results):
            print()

if __name__ == "__main__":
    quick_demo() 