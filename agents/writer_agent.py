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

    def generate_post(self, topic, keywords=[]):
        """블로그 원고 생성 (주제와 키워드 기반)"""
        prompt = f"""
        당신은 대한민국 4060 세대를 타겟으로 하는 전문 블로그 작가입니다.
        아래 주제와 키워드를 바탕으로, 독자들에게 실질적인 도움이 되고 가독성이 뛰어난 블로그 원고를 작성해주세요.
        
        주제: {topic}
        키워드: {', '.join(keywords)}
        
        [지침]
        1. 4060 세대의 눈높이에 맞춰 쉽고 친절하게 설명하세요.
        2. 소제목을 3개 이상 활용하여 구조를 잡으세요.
        3. 본문 중간에 [AD_BUTTON] 이라는 텍스트를 반드시 2회 삽입하세요.
        4. 분량은 1,500자 내외로 상세하게 작성하세요.
        """
        
        # 시도할 우선 순위 모델들 (2026년 기준 가용 모델)
        try_models = ['models/gemini-2.0-flash', 'models/gemini-flash-latest', 'models/gemini-pro-latest']
        for model_name in try_models:
            for attempt in range(3): # 모델당 최대 3번 시도
                try:
                    print(f"📡 {model_name} 모델로 원고 생성 시도 중... (시도 {attempt+1}/3)", flush=True)
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        wait_time = 40 # 기본 40초 대기 (쿼터 초과 대비)
                        print(f"⚠️ 쿼터 초과 (429). {wait_time}초 후 다시 시도합니다...", flush=True)
                        time.sleep(wait_time)
                        continue # 같은 모델로 다시 시도
                    else:
                        print(f"⚠️ {model_name} 실패: {e}", flush=True)
                        break # 다음 모델로 넘어감
                
        return None
                
        return None

if __name__ == "__main__":
    agent = WriterAgent()
    print("Available models:", agent.available_models)
