import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class WriterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.available_models = self._list_available_models()

    def _list_available_models(self):
        """사용 가능한 모든 텍스트 생성 모델 리스트 확보"""
        try:
            return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except:
            return ["models/gemini-pro"]

    def generate_post(self, topic):
        prompt = f"""
        당신은 4060 세대를 타겟으로 하는 전문 블로그 작가입니다.
        주제: '{topic['keyword']}'에 대해 HTML 형식으로 전문적인 블로그 글을 작성하세요.
        본문 중간에 [AD_BUTTON]을 꼭 넣어주세요.
        """
        
        # 시도할 우선 순위 모델들 (최신 프리뷰보다는 안정적인 모델 우선)
        priority_keywords = ['1.5-flash', '1.5-pro', '1.0-pro', 'gemini-pro']
        
        # 우선 순위에 따라 시도할 모델 리스트 재구성
        try_list = []
        for kw in priority_keywords:
            for m in self.available_models:
                if kw in m and m not in try_list:
                    try_list.append(m)
        
        # 목록에 없는 나머지 모델들도 뒤에 추가
        for m in self.available_models:
            if m not in try_list:
                try_list.append(m)

        for model_name in try_list:
            try:
                print(f"--- [TRY] {model_name} 모델로 시도 중... ---")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"⚠️ {model_name} 실패: {str(e)}")
                time.sleep(1) # 잠시 대기 후 다음 모델 시도
                continue
        
        return "모든 모델에서 글쓰기에 실패했습니다. 구글 서버 상태를 확인해 주세요."

if __name__ == "__main__":
    agent = WriterAgent()
