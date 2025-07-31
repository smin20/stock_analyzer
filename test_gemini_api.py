import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_api():
    """Gemini API 연결 테스트"""
    print("🔍 Gemini API 연결 테스트를 시작합니다...")
    print("=" * 50)
    
    # 1. 환경변수 로드
    print("1. 환경변수 로드 중...")
    load_dotenv()
    
    # 2. API 키 확인
    print("2. API 키 확인 중...")
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("💡 해결방법:")
        print("   1. .env 파일을 생성하세요")
        print("   2. 파일에 다음 내용을 추가하세요:")
        print("      GEMINI_API_KEY=your_actual_api_key_here")
        print("   3. Google AI Studio에서 API 키를 발급받으세요: https://aistudio.google.com/")
        return False
    
    if api_key == 'your_gemini_api_key_here':
        print("❌ API 키가 기본값입니다. 실제 API 키로 변경해주세요.")
        print("💡 Google AI Studio에서 API 키를 발급받으세요: https://aistudio.google.com/")
        return False
    
    print(f"✅ API 키 발견: {api_key[:10]}...{api_key[-4:]} (총 {len(api_key)}자)")
    
    # 3. Gemini API 초기화
    print("3. Gemini API 초기화 중...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Gemini API 초기화 성공")
    except Exception as e:
        print(f"❌ Gemini API 초기화 실패: {e}")
        return False
    
    # 4. 간단한 API 호출 테스트
    print("4. API 호출 테스트 중...")
    try:
        test_prompt = "안녕하세요. 이것은 API 연결 테스트입니다. '연결 성공'이라고 한 줄로만 답변해주세요."
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("✅ API 호출 성공")
            print(f"📝 응답: {response.text.strip()}")
            return True
        else:
            print("❌ API 응답이 비어있습니다")
            return False
            
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        print("💡 가능한 원인:")
        print("   - API 키가 유효하지 않음")
        print("   - 인터넷 연결 문제")
        print("   - API 사용량 초과")
        print("   - API 서비스 일시 중단")
        return False

def test_stock_analyzer_gemini():
    """StockAnalyzer의 Gemini 기능 테스트"""
    print("\n🔍 StockAnalyzer Gemini 기능 테스트...")
    print("=" * 50)
    
    try:
        from stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        
        if not analyzer.gemini_available:
            print("❌ StockAnalyzer에서 Gemini가 비활성화되어 있습니다")
            return False
        
        print("✅ StockAnalyzer Gemini 초기화 성공")
        
        # 자연어 분석 테스트
        print("📝 자연어 투자 전략 분석 테스트 중...")
        test_input = "배당수익률 4% 이상인 안정적인 대형주"
        
        result = analyzer.analyze_natural_language_strategy(test_input)
        
        if result and result.get('strategy_name') != 'API 없음':
            print("✅ 자연어 분석 성공")
            print(f"📊 분석 결과:")
            print(f"   전략명: {result.get('strategy_name', 'N/A')}")
            print(f"   설명: {result.get('description', 'N/A')}")
            if result.get('criteria'):
                print(f"   기준: {result['criteria']}")
            return True
        else:
            print("❌ 자연어 분석 실패")
            if result:
                print(f"   오류: {result.get('description', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ StockAnalyzer 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ StockAnalyzer 테스트 실패: {e}")
        return False

def check_env_file():
    """환경설정 파일 확인"""
    print("🔍 환경설정 파일 확인...")
    print("=" * 30)
    
    if os.path.exists('.env'):
        print("✅ .env 파일이 존재합니다")
        
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'GEMINI_API_KEY' in content:
            print("✅ .env 파일에 GEMINI_API_KEY가 설정되어 있습니다")
            
            # API 키 값 확인 (보안상 일부만)
            lines = content.split('\n')
            for line in lines:
                if line.startswith('GEMINI_API_KEY='):
                    key_value = line.split('=', 1)[1].strip()
                    if key_value and key_value != 'your_gemini_api_key_here':
                        print(f"✅ API 키 설정됨: {key_value[:10]}...{key_value[-4:]}")
                    else:
                        print("❌ API 키가 기본값이거나 비어있습니다")
                    break
        else:
            print("❌ .env 파일에 GEMINI_API_KEY가 없습니다")
    else:
        print("❌ .env 파일이 존재하지 않습니다")
        print("💡 해결방법:")
        print("   1. 프로젝트 루트에 .env 파일을 생성하세요")
        print("   2. 다음 내용을 추가하세요:")
        print("      GEMINI_API_KEY=your_actual_api_key_here")

def main():
    """메인 테스트 실행"""
    print("🚀 Gemini API 종합 테스트")
    print("=" * 60)
    
    # 환경설정 확인
    check_env_file()
    print()
    
    # 기본 API 테스트
    basic_test_result = test_gemini_api()
    print()
    
    # StockAnalyzer 테스트
    if basic_test_result:
        analyzer_test_result = test_stock_analyzer_gemini()
    else:
        print("⚠️ 기본 API 테스트 실패로 StockAnalyzer 테스트를 건너뜁니다")
        analyzer_test_result = False
    
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    
    if basic_test_result and analyzer_test_result:
        print("🎉 모든 테스트 통과! Gemini API가 정상적으로 작동합니다.")
    elif basic_test_result:
        print("⚠️ 기본 API는 작동하지만 StockAnalyzer 통합에 문제가 있습니다.")
    else:
        print("❌ Gemini API 연결에 문제가 있습니다. 위의 해결방법을 참고하세요.")

if __name__ == "__main__":
    main() 