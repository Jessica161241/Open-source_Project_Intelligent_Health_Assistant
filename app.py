from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

# MaxKB API 配置
MAXKB_API_URL = "http://localhost:8080/ui/chat/c9d289df55cfc1dc"
MAXKB_API_KEY = "application-367032ed5055a7239377076902af24b0"


@app.route('/')
def index():
    # 返回前端 HTML
    return send_from_directory('.', 'index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    repo = request.json.get("repo", "github/user/repo")
    prompt = f"分析仓库 {repo}，返回五个健康维度和改进建议"

    try:
        resp = requests.post(
            MAXKB_API_URL,
            json={"prompt": prompt},
            headers={
                "Authorization": f"Bearer {MAXKB_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        # 假设返回结构中有 'radar' 和 'suggestions'
        return jsonify(data)
    except Exception as e:
        print("[Error] MaxKB API 请求失败:", e)
        # 返回示例数据，保证前端可展示
        return jsonify({
            "response": "AI助手请求失败，使用示例数据",
            "radar": {"活跃度": 80, "协作度": 70, "问题管理": 60, "PR管理": 75, "流行度": 85},
            "suggestions": [
                {"priority": "高", "text": "测试覆盖率低，建议增加单元测试"},
                {"priority": "中", "text": "缺少文档，建议补充README和CONTRIBUTING"},
                {"priority": "低", "text": "项目响应时间较慢，建议设置响应SLA"}
            ]
        })


if __name__ == "__main__":
    app.run(debug=True)
