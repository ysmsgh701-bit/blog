import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CuratorAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        self.target_audience = "4060 세대 (대한민국 중장년층)"
        
    def refine_title(self, raw_topic):
        """평범한 주제를 유튜브 스타일의 자극적인 제목으로 변환 (다중 모델 시도)"""
        prompt = f"""
        아래의 평범한 블로그 주제를 4060 세대가 클릭하지 않고는 못 배길 '유튜브 썸네일 스타일'의 자극적인 제목으로 딱 하나만 다시 작성하세요.
        
        [원래 주제]
        {raw_topic}
        
        [조건]
        1. '충격', '비결', '손해', '당장', '나라에서' 등의 강력한 키워드 활용
        2. 결과는 제목만 짧고 굵게 출력하세요. (특수문자 제외)
        """
        
        try_models = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
        for model_name in try_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                refined = response.text.strip().replace('"', '')
                if refined:
                    return refined
            except:
                continue
        
        return raw_topic

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
        2. 제목 스타일: 유튜브 썸네일처럼 클릭을 강하게 유도하는 자극적이고 흥미로운 스타일로 작성하세요. 
           (예: "모르면 평생 손해!", "나라에서 100만원 줍니다", "지금 당장 확인해야 할...", "충격적인 진실")
        3. 결과는 JSON 형식으로만 응답하세요:
           [
             {{"topic": "자극적인 제목", "reason": "추천 이유", "keywords": ["키워드1", "키워드2"], "priority": "상/중/하"}}
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
