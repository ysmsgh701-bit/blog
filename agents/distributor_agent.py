import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class DistributorAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.available_models = self._list_available_models()

    def _list_available_models(self):
        try:
            return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            print(f"⚠️ 모델 목록 조회 실패: {e}", flush=True)
            return ["models/gemini-1.5-flash"]

    def transform_for_sns(self, blog_title, blog_content):
        """
        블로그 내용을 인스타그램 카드뉴스, 릴스 대본으로 변환
        """
        prompt = f"""
        블로그 글을 인스타그램에 맞는 형식으로 변환해주세요.

        [블로그 제목]
        {blog_title}

        [블로그 내용]
        {blog_content[:2000]} # 토큰 절약을 위해 일부만 사용

        [요청사항]
        1. 카드뉴스 (Carousel): 10장 이내의 구성 (각 장의 제목과 핵심 문구)
        2. 릴스 대본 (Reels): 60초 내외의 흥미 유발형 대본 (영상 연출 가이드 포함)
        3. 캡션 (Caption): 인스타그램에 바로 올릴 수 있는 해시태그 포함 캡션

        모든 출력은 한국어로, 친근하고 유익한 말투(~하세요, ~입니다)를 사용하세요.
        응답은 아래 JSON 형식을 지켜주세요:
        {{
          "carousel": [
            {{"slide": 1, "title": "...", "content": "..."}}
          ],
          "reels": {{"hook": "...", "body": "...", "outro": "..."}},
          "caption": "..."
        }}
        """
        
        priority_keywords = ['1.5-flash', '2.0-flash', '1.5-pro', '1.0-pro']
        try_list = []
        for kw in priority_keywords:
            for m in self.available_models:
                if kw in m and m not in try_list:
                    try_list.append(m)
        
        for m in self.available_models:
            if m not in try_list:
                try_list.append(m)

        for model_name in try_list:
            try:
                print(f"--- [TRY SNS] {model_name} 모델로 시도 중... ---")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                content = response.text.strip()
                
                # 정규표현식으로 JSON 블록 추출 시도
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                
                # 백틱 없이 JSON만 왔을 경우 시도
                json_match = re.search(r'(\{.*?\})', content, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                    
                return content
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"⚠️ {model_name} 할당량 초과 (429 Error)")
                else:
                    print(f"⚠️ Distributor Error ({model_name}): {error_msg}")
                continue
        
        return "{}"

if __name__ == "__main__":
    agent = DistributorAgent()
    print(agent.transform_for_sns("테스트 제목", "테스트 내용입니다."))
