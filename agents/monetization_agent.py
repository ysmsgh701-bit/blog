import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class MonetizationAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.coupang_id = os.getenv("COUPANG_ID", "AF1234567") # 기본 ID

    def recommend_products(self, topic):
        """주제와 관련된 쿠팡 추천 상품 키워드 3가지 추출"""
        prompt = f"""
        아래 블로그 주제와 가장 잘 어울리는 쿠팡 판매 상품 키워드 3가지를 뽑아주세요.
        4060 세대가 실제로 구매할 법한 실용적인 상품이어야 합니다.
        
        주제: {topic}
        
        결과는 쉼표로 구분된 키워드만 출력하세요. (예: 건강식품, 무릎보호대, 재테크도서)
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return [k.strip() for k in response.text.split(',')]
        except:
            return ["부모님 선물", "건강식품", "자기계발도서"]

    def insert_coupang_links(self, html_content, topic):
        """본문 하단에 쿠팡 파트너스 링크 및 안내 문구 삽입"""
        keywords = self.recommend_products(topic)
        
        monetization_html = f"""
        <div style="margin-top: 50px; padding: 20px; border: 1px dashed #ccc; border-radius: 10px; background: #f9f9f9;">
            <h3 style="margin-top: 0; color: #333;">💡 4060 세대를 위한 추천 아이템</h3>
            <ul style="list-style: none; padding: 0;">
        """
        
        for kw in keywords:
            # 실제 API 연동 전까지는 검색 링크 형식으로 생성
            search_url = f"https://link.coupang.com/a/your-link-id?q={kw}" 
            monetization_html += f"""
                <li style="margin-bottom: 10px;">
                    <a href="{search_url}" target="_blank" style="color: #007bff; text-decoration: none;">
                        👉 <strong>{kw}</strong> 최저가 확인하기
                    </a>
                </li>
            """
            
        monetization_html += f"""
            </ul>
            <p style="font-size: 0.8rem; color: #888; margin-top: 15px;">
                * 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
            </p>
        </div>
        """
        
        # HTML의 </body> 태그 직전이나 컨텐츠 끝에 삽입
        if "</div>" in html_content:
            parts = html_content.rsplit("</div>", 1)
            return parts[0] + monetization_html + "</div>" + parts[1]
        return html_content + monetization_html

if __name__ == "__main__":
    agent = MonetizationAgent()
    print(agent.recommend_products("노후 자금 마련을 위한 주택연금 활용법"))
