import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from agents.curator_agent import CuratorAgent
from agents.writer_agent import WriterAgent
from agents.publisher_agent import PublisherAgent
from agents.distributor_agent import DistributorAgent
from agents.image_agent import ImageAgent
from utils.html_builder import HTMLBuilder

# .env 파일 로드
load_dotenv()

# 윈도우 인코딩 설정
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 데이터 경로 설정
DATA_DIR = Path("data")
POSTS_DB = DATA_DIR / "posts_db.json"
POSTS_DIR = DATA_DIR / "posts"
SNS_DIR = DATA_DIR / "sns"
IMAGES_DIR = DATA_DIR / "images"

# 폴더 생성
for d in [POSTS_DIR, SNS_DIR, IMAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def update_db(post_data):
    """게시글 데이터를 JSON DB에 저장"""
    posts = []
    if POSTS_DB.exists():
        with open(POSTS_DB, "r", encoding="utf-8") as f:
            posts = json.load(f)
    
    # 중복 ID 체크 및 추가
    if not any(p['id'] == post_data['id'] for p in posts):
        posts.append(post_data)
    
    with open(POSTS_DB, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def run_automation_pipeline(custom_keyword=None):
    print("\n🚀 [START] 4060 Smart Blog Pipeline 가동 ---")
    
    # 1. 주제 기획 (Curator)
    curator = CuratorAgent()
    if custom_keyword:
        target_topic = {"topic": custom_keyword, "keywords": [custom_keyword], "category": "사용자 지정"}
    else:
        print("[1/5] 트렌드 분석 및 주제 선정 중...")
        trends = curator.analyze_trends("2025 복지 혜택, 노인 일자리, 절세 전략, 건강보험")
        topics = json.loads(trends)
        target_topic = topics[0] if topics else {"topic": "추천 주제 없음", "keywords": []}
    
    print(f">> 선정 주제: {target_topic['topic']}")

    # 2. 원고 작성 (Writer)
    print("[2/5] AI 원고 생성 중...")
    writer = WriterAgent()
    raw_content = writer.generate_post({"keyword": target_topic['topic']})
    
    # 3. HTML 디자인 (Utils)
    final_post_html = HTMLBuilder.build_premium_post(raw_content)
    print("[3/5] 프리미엄 HTML 변환 완료")

    # 4. 데이터 저장 및 DB 업데이트
    post_id = int(datetime.now().timestamp())
    post_entry = {
        "id": post_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": target_topic['topic'],
        "keywords": target_topic.get('keywords', []),
        "category": target_topic.get('category', '일반'),
        "status": "draft"
    }
    update_db(post_entry)
    
    # HTML 파일 저장
    html_path = POSTS_DIR / f"post_{post_id}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_post_html)
    
    # 대시보드 호환을 위해 루트 data 폴더에도 복사본 유지 (필요시)
    with open(DATA_DIR / f"post_{post_id}.html", "w", encoding="utf-8") as f:
        f.write(final_post_html)

    print(f"[4/5] 로컬 데이터베이스 및 HTML 저장 완료 (ID: {post_id})")

    # 5. SNS 변환 및 이미지 생성 (Distributor & ImageAgent)
    print("\n[5/5] SNS 홍보 콘텐츠 및 이미지 생성 중...")
    distributor = DistributorAgent()
    sns_content_raw = distributor.transform_for_sns(target_topic['topic'], raw_content)
    
    try:
        sns_content = json.loads(sns_content_raw)
        # SNS 데이터 저장
        sns_path = SNS_DIR / f"sns_{post_id}.json"
        with open(sns_path, "w", encoding="utf-8") as f:
            json.dump(sns_content, f, ensure_ascii=False, indent=4)
        
        # 루트 data 폴더 복사본
        with open(DATA_DIR / f"sns_{post_id}.json", "w", encoding="utf-8") as f:
            json.dump(sns_content, f, ensure_ascii=False, indent=4)

        # 이미지 생성
        image_agent = ImageAgent()
        image_files = image_agent.generate_images(post_id, sns_content.get('carousel', []))
        if image_files:
            print(f"✅ {len(image_files)}개의 카드뉴스 이미지 생성 완료")
            
    except Exception as e:
        print(f"⚠️ SNS/이미지 생성 중 오류 발생: {e}")
    
    print(f"\n✨ [FINISH] 모든 작업 완료! 대시보드(index.html)에서 확인하세요. ---")

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_automation_pipeline(custom_keyword=topic)
