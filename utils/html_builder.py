class HTMLBuilder:
    @staticmethod
    def build_premium_post(title, raw_content):
        """
        작성된 원고에 4060 타겟 맞춤형 디자인 스타일(CSS)과 광고 버튼 삽입
        """
        css_style = """
        <style>
            .post-container { font-family: 'Malgun Gothic', sans-serif; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1.post-title { color: #2c3e50; border-bottom: 3px solid #6366f1; padding-bottom: 15px; font-size: 2rem; }
            .post-body { white-space: pre-wrap; font-size: 1.1rem; }
            .ad-button { 
                display: block; width: 80%; margin: 30px auto; padding: 15px;
                background-color: #6366f1; color: white !important; text-align: center;
                text-decoration: none; font-weight: bold; border-radius: 10px;
                font-size: 1.3rem; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            }
            .ad-button:hover { background-color: #4f46e5; transform: scale(1.02); transition: all 0.2s; }
        </style>
        """
        ad_button_html = '<a href="#" class="ad-button">👉 지금 바로 혜택 확인하기 (클릭)</a>'
        
        body_content = raw_content.replace("[AD_BUTTON]", ad_button_html)
        final_html = f"""
        {css_style}
        <div class="post-container">
            <h1 class="post-title">{title}</h1>
            <div class="post-body">
                {body_content}
            </div>
        </div>
        """
        return final_html
