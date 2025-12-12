from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Wishlist, User, Book

bp = Blueprint("wishlists", __name__)


@bp.route("", methods=["POST"])
def add_to_wishlist():
    data = request.get_json() or {}

    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        return jsonify({"message": "user_id, book_id 는 필수입니다."}), 400

    if not User.query.get(user_id):
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404
    if not Book.query.get(book_id):
        return jsonify({"message": "도서를 찾을 수 없습니다."}), 404

    # 이미 찜한 항목인지 확인(soft delete 안 된 것만)
    existing = Wishlist.query.filter(
        Wishlist.user_id == user_id,
        Wishlist.book_id == book_id,
        Wishlist.deleted_at.is_(None),
    ).first()
    if existing:
        return jsonify({"message": "이미 위시리스트에 존재하는 도서입니다."}), 409

    wishlist = Wishlist(user_id=user_id, book_id=book_id)
    db.session.add(wishlist)
    db.session.commit()

    return jsonify({
        "id": wishlist.id,
        "user_id": wishlist.user_id,
        "book_id": wishlist.book_id,
        "created_at": wishlist.created_at.isoformat()
    }), 201


@bp.route("", methods=["GET"])
def list_all_wishlists():
    """간단 전체 조회 (관리자용 느낌, 나중에 ADMIN 권한으로 제한 가능)"""
    wishlists = Wishlist.query.filter(Wishlist.deleted_at.is_(None)).all()
    result = [
        {
            "id": w.id,
            "user_id": w.user_id,
            "book_id": w.book_id,
            "created_at": w.created_at.isoformat(),
        }
        for w in wishlists
    ]
    return jsonify(result), 200


@bp.route("/me", methods=["GET"])
def list_my_wishlist():
    """user_id 기준 사용자 위시리스트 조회 (나중에 JWT로 교체)"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "user_id 쿼리 파라미터는 필수입니다."}), 400

    wishlists = Wishlist.query.filter(
        Wishlist.user_id == user_id,
        Wishlist.deleted_at.is_(None)
    ).all()

    result = [
        {
            "id": w.id,
            "user_id": w.user_id,
            "book_id": w.book_id,
            "created_at": w.created_at.isoformat(),
        }
        for w in wishlists
    ]
    return jsonify(result), 200


@bp.route("/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist_item(wishlist_id):
    wishlist = Wishlist.query.get(wishlist_id)
    if not wishlist or wishlist.deleted_at is not None:
        return jsonify({"message": "위시리스트 항목을 찾을 수 없습니다."}), 404

    wishlist.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "위시리스트 항목이 삭제되었습니다."}), 200
