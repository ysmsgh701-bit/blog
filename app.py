import re
import subprocess
from pathlib import Path
from flask import Flask, send_from_directory, Response, request, stream_with_context, abort

BASE_DIR = Path(__file__).parent.resolve()

# 정적 파일로 노출해도 안전한 경로만 허용
ALLOWED_STATIC_DIRS = {'data', 'assets'}
BLOCKED_PATHS = {'.env', 'token.json', 'client_secrets.json', 'credentials.json', '.git'}

app = Flask(__name__, static_folder=None)

@app.route('/')
def serve_index():
    return send_from_directory(str(BASE_DIR), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # 민감 파일 및 상위 경로 이동 차단
    normalized = Path(path).parts
    if not normalized:
        abort(404)
    if any(part in BLOCKED_PATHS or part.startswith('.') for part in normalized):
        abort(403)
    if normalized[0] not in ALLOWED_STATIC_DIRS:
        abort(403)

    full_path = BASE_DIR / path
    if not full_path.resolve().is_relative_to(BASE_DIR):
        abort(403)
    if not full_path.exists():
        abort(404)

    return send_from_directory(str(BASE_DIR), path)

@app.route('/api/generate', methods=['POST'])
def generate_post():
    data = request.json or {}
    keyword = data.get('keyword', '').strip()

    # 키워드 입력 검증 (명령어 인젝션 방지)
    if keyword and not re.match(r'^[\w\s가-힣a-zA-Z0-9\-_.,!?%]+$', keyword):
        return {'error': '유효하지 않은 키워드입니다.'}, 400
    if len(keyword) > 100:
        return {'error': '키워드가 너무 깁니다.'}, 400

    def generate():
        cmd = ['python', str(BASE_DIR / 'main.py')]
        if keyword:
            cmd.append(keyword)  # 리스트로 전달하므로 shell injection 없음

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            cwd=str(BASE_DIR)
        )

        for line in process.stdout:
            cleaned_line = line.replace('\n', '').replace('\r', '')
            yield f"data: {cleaned_line}\n\n"

        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            yield "data: [COMPLETE]\n\n"
        else:
            yield "data: [ERROR]\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("[START] Local Admin Dashboard Server Started.")
    print(">> Open your browser and go to http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
