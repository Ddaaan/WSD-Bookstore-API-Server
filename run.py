from src.app import create_app
from flask import jsonify

app = create_app("dev")

@app.route("/")
def home():
    return jsonify({"message": "Bookstore API 서버에 오신 것을 환영합니다!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
