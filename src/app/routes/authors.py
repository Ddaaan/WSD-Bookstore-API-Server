from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Author

bp = Blueprint("authors", __name__)


@bp.route("", methods=["POST"])
def create_author():
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"message": "name 은 필수입니다."}), 400

    author = Author(
        name=name,
        bio=data.get("bio"),
    )
    db.session.add(author)
    db.session.commit()

    return jsonify({
        "id": author.id,
        "name": author.name,
        "bio": author.bio,
    }), 201


@bp.route("", methods=["GET"])
def list_authors():
    authors = Author.query.all()
    result = [
        {"id": a.id, "name": a.name, "bio": a.bio}
        for a in authors
    ]
    return jsonify(result), 200


@bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"message": "저자를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": author.id,
        "name": author.name,
        "bio": author.bio,
    }), 200


@bp.route("/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"message": "저자를 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    author.name = data.get("name", author.name)
    author.bio = data.get("bio", author.bio)
    db.session.commit()

    return jsonify({"message": "저자 정보가 수정되었습니다."}), 200


@bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"message": "저자를 찾을 수 없습니다."}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({"message": "저자 정보가 삭제되었습니다."}), 200
