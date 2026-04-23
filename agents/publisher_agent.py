import os
import json
import requests
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class PublisherAgent:
    def __init__(self):
        self.blogger_scopes = ['https://www.googleapis.com/auth/blogger']
        self.data_dir = Path("data")
        self.creds_path = Path("token.json")

    def _get_blogger_service(self):
        """Blogger API 인증 및 서비스 객체 반환"""
        creds = None
        if self.creds_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.creds_path), self.blogger_scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('client_secrets.json'):
                    print("⚠️ client_secrets.json 파일이 없습니다. Blogger 발행을 건너뜁니다.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', self.blogger_scopes)
                creds = flow.run_local_server(port=0)
            
            with open(self.creds_path, 'w') as token:
                token.write(creds.to_json())

        return build('blogger', 'v3', credentials=creds)

    def publish_to_blogger(self, blog_id, title, content):
        """Blogger에 포스팅 업로드"""
        try:
            service = self._get_blogger_service()
            if not service: return None
            
            body = {
                "kind": "blogger#post",
                "title": title,
                "content": content
            }
            posts = service.posts()
            result = posts.insert(blogId=blog_id, body=body).execute()
            print(f"✅ Blogger 포스팅 완료: {result.get('url')}")
            return result
        except Exception as e:
            print(f"❌ Blogger 발행 실패: {e}")
            return None

    def publish_to_instagram(self, user_id, access_token, caption, image_urls):
        """Instagram Graph API를 사용하여 카드뉴스(Carousel) 업로드"""
        if not access_token or access_token == "your_meta_token_here":
            print("⚠️ Instagram 액세스 토큰이 설정되지 않았습니다.")
            return None

        # 1. 각 이미지를 컨테이너로 업로드
        media_ids = []
        for url in image_urls:
            container_url = f"https://graph.facebook.com/v19.0/{user_id}/media"
            payload = {
                'image_url': url,
                'is_carousel_item': True,
                'access_token': access_token
            }
            response = requests.post(container_url, data=payload)
            res_data = response.json()
            if 'id' in res_data:
                media_ids.append(res_data['id'])
            else:
                print(f"❌ 이미지 컨테이너 생성 실패: {res_data}")
                return None

        # 2. 캐러셀 컨테이너 생성
        carousel_url = f"https://graph.facebook.com/v19.0/{user_id}/media"
        carousel_payload = {
            'caption': caption,
            'media_type': 'CAROUSEL',
            'children': ','.join(media_ids),
            'access_token': access_token
        }
        carousel_res = requests.post(carousel_url, data=carousel_payload).json()
        
        if 'id' in carousel_res:
            creation_id = carousel_res['id']
            # 3. 최종 발행
            publish_url = f"https://graph.facebook.com/v19.0/{user_id}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            final_res = requests.post(publish_url, data=publish_payload).json()
            if 'id' in final_res:
                print("✅ Instagram 카드뉴스 발행 성공!")
                return final_res
        
        print(f"❌ Instagram 발행 실패: {carousel_res}")
        return None

if __name__ == "__main__":
    pass
