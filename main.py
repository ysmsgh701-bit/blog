import sys
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from agents.curator_agent import CuratorAgent
from agents.writer_agent import WriterAgent
from agents.publisher_agent import PublisherAgent
from agents.distributor_agent import DistributorAgent
from agents.image_agent import ImageAgent
from agents.monetization_agent import MonetizationAgent
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

def validate_config():
    """필수 환경변수 및 파일 존재 여부 사전 검사"""
    errors = []
    warnings = []

    if not os.getenv("GEMINI_API_KEY"):
        errors.append("GEMINI_API_KEY 미설정 (필수)")
    if not os.getenv("BLOGGER_BLOG_ID"):
        warnings.append("BLOGGER_BLOG_ID 미설정 → Blogger 발행 건너뜀")
    if not os.getenv("OPENAI_API_KEY"):
        warnings.append("OPENAI_API_KEY 미설정 → 이미지 생성 Mock 모드로 실행됨")
    if os.getenv("COUPANG_ID", "AF1234567") == "AF1234567":
        warnings.append("COUPANG_ID가 기본값 → .env에 실제 파트너스 ID 설정 권장")

    for w in warnings:
        print(f"⚠️  [CONFIG] {w}", flush=True)
    for e in errors:
        print(f"❌  [CONFIG] {e}", flush=True)

    if errors:
        print("설정 오류로 인해 파이프라인을 시작할 수 없습니다.", flush=True)
        return False
    return True


def run_automation_pipeline(custom_keyword=None):
    print(f"\n🚀 [START] 4060 Smart Blog Pipeline 가동 ---", flush=True)
    
    # 1. 주제 기획 (Curator)
    print("\n[1/7] 주제 분석 및 기획 중...", flush=True)
    curator = CuratorAgent()
    if custom_keyword:
        catchy_title = curator.refine_title(custom_keyword)
        print(f"🎯 제목 다듬기: {custom_keyword} -> {catchy_title}", flush=True)
        target_topic = {"topic": catchy_title, "keywords": [custom_keyword], "category": "사용자 지정"}
    else:
        print("[1/7] 트렌드 분석 및 주제 선정 중...", flush=True)
        trends = curator.analyze_trends("2025 복지 혜택, 노인 일자리, 절세 전략, 건강보험")
        topics = json.loads(trends)
        target_topic = topics[0] if topics else {"topic": "추천 주제 없음", "keywords": []}
    
    print(f">> 선정 주제: {target_topic['topic']}", flush=True)

    # 2. 원고 작성 (Writer)
    print("\n[2/7] 원고 작성 중...", flush=True)
    time.sleep(10) # 쿼터 방지를 위한 대기
    writer = WriterAgent()
    raw_content = writer.generate_post(target_topic['topic'], target_topic.get('keywords', []))
    
    if not raw_content or len(raw_content) < 100:
        print("❌ [ERROR] 원고 작성 실패 (내용이 너무 짧거나 비어있습니다. API 할당량을 확인하세요.)", flush=True)
        return
    else:
        print(f"✅ 원고 작성 완료 ({len(raw_content)}자)", flush=True)

    # 3. HTML 변환 (HTMLBuilder)
    print("\n[3/7] 프리미엄 HTML 변환 중...", flush=True)
    final_post_html = HTMLBuilder.build_premium_post(target_topic['topic'], raw_content)

    # 4. 수익화 코드 삽입 (MonetizationAgent)
    print("\n[4/7] 수익화 링크(쿠팡 파트너스) 삽입 중...", flush=True)
    time.sleep(5)
    monetizer = MonetizationAgent()
    final_post_html = monetizer.insert_coupang_links(final_post_html, target_topic['topic'])

    # 5. 데이터 저장 및 DB 업데이트 (기존 4단계를 5단계로 변경)
    time.sleep(2)
    post_id = int(time.time())
    post_entry = {
        "id": post_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": target_topic['topic'],
        "keywords": target_topic.get('keywords', []),
        "category": target_topic.get('category', '일반'),
        "status": "draft"
    }
    
    # HTML 파일 저장
    with open(POSTS_DIR / f"post_{post_id}.html", "w", encoding="utf-8") as f:
        f.write(final_post_html)
    
    print(f"✅ 로컬 데이터 저장 완료 (ID: {post_id})", flush=True)

    # 6. 블로그 실제 발행 (Publisher)
    print("\n[6/7] 구글 블로그(Blogger) 자동 발행 시도 중...", flush=True)
    blog_id = os.getenv("BLOGGER_BLOG_ID")
    if blog_id:
        publisher = PublisherAgent()
        pub_result = publisher.publish_to_blogger(blog_id, target_topic['topic'], final_post_html)
        if pub_result:
            print(f"🚀 [SUCCESS] 구글 블로그 발행 완료! (URL: {pub_result.get('url')})", flush=True)
            post_entry["status"] = "published"
            post_entry["url"] = pub_result.get("url")
        else:
            print("❌ [FAIL] 구글 블로그 발행 실패 (로그를 확인하세요.)", flush=True)
    else:
        print("⚠️ [SKIP] BLOGGER_BLOG_ID 미설정으로 발행 건너뜀", flush=True)

    update_db(post_entry)

    # 7. SNS 변환 및 이미지 생성
    print("\n[7/7] SNS 콘텐츠 및 이미지 생성 중...", flush=True)
    distributor = DistributorAgent()
    sns_content_raw = distributor.transform_for_sns(target_topic['topic'], raw_content)
    
    try:
        if sns_content_raw and sns_content_raw != "{}":
            sns_content = json.loads(sns_content_raw, strict=False)
            sns_filename = f"sns_{post_id}.json"
            with open(SNS_DIR / sns_filename, "w", encoding="utf-8") as f:
                json.dump(sns_content, f, ensure_ascii=False, indent=4)
            print("✅ SNS 데이터 생성 완료", flush=True)
            
            image_agent = ImageAgent()
            image_files = image_agent.generate_images(post_id, sns_content.get('carousel', []))
            if image_files:
                print(f"✅ 카드뉴스 이미지 {len(image_files)}개 생성 완료", flush=True)
        else:
            print("❌ [FAIL] SNS 콘텐츠 생성 실패 (API 할당량 부족)", flush=True)
    except Exception as e:
        print(f"❌ [ERROR] SNS 처리 중 오류: {e}", flush=True)
    
    print(f"\n✨ [FINISH] 모든 작업 완료! 대시보드(index.html)에서 확인하세요. ---", flush=True)

if __name__ == "__main__":
    if not validate_config():
        sys.exit(1)
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_automation_pipeline(custom_keyword=topic)
