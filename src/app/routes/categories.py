from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Category

bp = Blueprint("categories", __name__)


@bp.route("", methods=["POST"])
def create_category():
    data = request.get_json() or {}
    name = data.get("name")
    slug = data.get("slug")

    if not name or not slug:
        return jsonify({"message": "name, slug 는 필수입니다."}), 400

    # 간단 중복 체크
    if Category.query.filter((Category.name == name) | (Category.slug == slug)).first():
        return jsonify({"message": "이미 존재하는 카테고리 이름 또는 슬러그입니다."}), 409

    category = Category(name=name, slug=slug)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
    }), 201


@bp.route("", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    result = [
        {"id": c.id, "name": c.name, "slug": c.slug}
        for c in categories
    ]
    return jsonify(result), 200


@bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "카테고리를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
    }), 200


@bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "카테고리를 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    category.name = data.get("name", category.name)
    category.slug = data.get("slug", category.slug)
    db.session.commit()

    return jsonify({"message": "카테고리 정보가 수정되었습니다."}), 200


@bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "카테고리를 찾을 수 없습니다."}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "카테고리가 삭제되었습니다."}), 200
