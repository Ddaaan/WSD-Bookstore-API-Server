from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User

bp = Blueprint("users", __name__)

# 사용자 생성
@bp.route("", methods=["POST"])
def create_user():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")  # 입력은 password
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"message": "email, password, name 은 필수입니다."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "이미 사용 중인 이메일입니다."}), 409

    user = User(
        email=email,
        name=name,
        password_hash=password,  # DB 컬럼은 password_hash
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }), 201

# 사용자 목록 조회
@bp.route("", methods=["GET"])
def list_users():
    users = User.query.all()
    result = [
        {"id": u.id, "email": u.email, "name": u.name, "role": u.role}
        for u in users
    ]
    return jsonify(result), 200


# 특정 사용자 조회
@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }), 200


# 사용자 수정
@bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    user.name = data.get("name", user.name)
    db.session.commit()

    return jsonify({"message": "수정되었습니다."}), 200


# 사용자 삭제
@bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "삭제되었습니다."}), 200
