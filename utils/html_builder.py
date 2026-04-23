class HTMLBuilder:
    @staticmethod
    def build_premium_post(raw_content):
        """
        작성된 원고에 4060 타겟 맞춤형 디자인 스타일(CSS)과 광고 버튼 삽입
        """
        css_style = """
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; line-height: 1.8; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .ad-button { 
                display: block; width: 80%; margin: 20px auto; padding: 15px;
                background-color: #e74c3c; color: white; text-align: center;
                text-decoration: none; font-weight: bold; border-radius: 5px;
                font-size: 1.2em;
            }
        </style>
        """
        ad_button_html = '<a href="#" class="ad-button">지금 바로 확인하기 (클릭)</a>'
        
        final_html = css_style + raw_content.replace("[AD_BUTTON]", ad_button_html)
        return final_html
