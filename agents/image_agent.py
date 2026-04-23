import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class ImageAgent:
    def __init__(self, model="dall-e-3"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.save_dir = Path("data/images")
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def generate_prompts(self, carousel_data):
        """슬라이드 데이터를 바탕으로 이미지 생성을 위한 상세 프롬프트 생성"""
        prompts = []
        for slide in carousel_data:
            # 4060 세대에 맞는 세련되고 신뢰감 있는 이미지 스타일 정의
            base_style = "Premium, clean, modern graphic design. High resolution. Warm lighting. "
            visual_desc = f"Concept: {slide['title']}. Content: {slide['content']}. "
            target_vibe = "Targeting age 40-60, professional, financial theme, trustworthy, minimal UI elements."
            
            prompt = f"{base_style} {visual_desc} {target_vibe}"
            prompts.append({
                "slide": slide['slide'],
                "prompt": prompt
            })
        return prompts

    def generate_images(self, post_id, carousel_data):
        """각 슬라이드별 이미지 생성 및 저장"""
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. 이미지 생성을 건너뜜 (Mock 모드).")
            return self._mock_generate(post_id, carousel_data)

        post_image_dir = self.save_dir / str(post_id)
        post_image_dir.mkdir(parents=True, exist_ok=True)
        
        prompts = self.generate_prompts(carousel_data)
        generated_files = []

        for p in prompts:
            print(f"🎨 슬라이드 {p['slide']} 이미지 생성 중...")
            try:
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "prompt": p['prompt'],
                        "n": 1,
                        "size": "1024x1024"
                    }
                )
                result = response.json()
                if "data" in result:
                    image_url = result['data'][0]['url']
                    img_data = requests.get(image_url).content
                    file_path = post_image_dir / f"slide_{p['slide']}.png"
                    with open(file_path, "wb") as f:
                        f.write(img_data)
                    generated_files.append(str(file_path))
                else:
                    print(f"❌ 생성 실패: {result.get('error', {}).get('message')}")
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

        return generated_files

    def _mock_generate(self, post_id, carousel_data):
        """API 키가 없을 때 가짜 경로 반환 (테스트용)"""
        post_image_dir = self.save_dir / str(post_id)
        post_image_dir.mkdir(parents=True, exist_ok=True)
        
        mock_files = []
        for slide in carousel_data:
            file_path = post_image_dir / f"slide_{slide['slide']}.png"
            # 실제 이미지가 없으므로 빈 파일이라도 생성하여 경로 유효성 유지
            with open(file_path, "w") as f:
                f.write("mock_image_data")
            mock_files.append(str(file_path))
        return mock_files

if __name__ == "__main__":
    test_carousel = [{"slide": 1, "title": "테스트", "content": "내용"}]
    agent = ImageAgent()
    agent.generate_images("test", test_carousel)
