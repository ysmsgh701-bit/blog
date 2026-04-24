import schedule
import time
import subprocess
import os
from datetime import datetime

def run_blog_pipeline():
    """메인 파이프라인 실행"""
    print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 포스팅 시작...")
    try:
        # main.py 실행 (매개변수 없이 실행하면 AI가 주제를 알아서 선정)
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ 자동 포스팅 성공!")
        else:
            print(f"❌ 자동 포스팅 실패: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 스케줄러 실행 중 오류 발생: {e}")

# --- 스케줄 설정 ---
# 1. 6시간마다 실행
schedule.every(6).hours.do(run_blog_pipeline)

# 2. 특정 시간에 실행 (예: 매일 오전 9시)
# schedule.every().day.at("09:00").do(run_blog_pipeline)

print("🚀 4060 블로그 자동화 스케줄러 가동 중...")
print("이 창을 켜두시면 6시간마다 자동으로 포스팅이 생성됩니다.")

# 테스트를 위해 즉시 한 번 실행하고 싶다면 아래 주석을 해제하세요
# run_blog_pipeline()

while True:
    schedule.run_pending()
    time.sleep(60) # 1분마다 스케줄 확인
