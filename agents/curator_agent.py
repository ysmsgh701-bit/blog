import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CuratorAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.target_audience = "4060 세대 (대한민국 중장년층)"
        
    def analyze_trends(self, raw_search_results):
        """
        검색 결과나 트렌드 데이터를 분석하여 고단가 블로그 주제 리스트 생성
        """
        prompt = f"""
        당신은 대한민국 4060 세대를 타겟으로 하는 수익형 블로그 기획자입니다.
        아래 제공된 트렌드 데이터와 사회적 이슈를 바탕으로, 클릭률(CTR)이 높고 CPC(광고 단가)가 높을 것으로 예상되는 블로그 주제 3가지를 추천해주세요.

        [트렌드 데이터]
        {raw_search_results}

        [조건]
        1. 타겟: 4060 세대 (건강, 재테크, 복지, 일자리 관심)
        2. 결과는 JSON 형식으로만 응답하세요:
           [
             {{"topic": "주제 제목", "reason": "추천 이유", "keywords": ["키워드1", "키워드2"], "priority": "상/중/하"}}
           ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            # JSON만 추출하는 로직 (Gemini가 마크다운으로 응답할 경우 대비)
            content = response.text.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return content
        except Exception as e:
            print(f"Curator Error: {e}")
            return "[]"

if __name__ == "__main__":
    agent = CuratorAgent()
    # 데모용 샘플 서치 결과
    mock_search = "2025년 최저임금 확정, 기초연금 40만원 인상 논의, 고혈압 예방 식단 유행"
    print(agent.analyze_trends(mock_search))
