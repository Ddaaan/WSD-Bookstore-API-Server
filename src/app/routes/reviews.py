from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Review, Book, User

bp = Blueprint("reviews", __name__)


@bp.route("", methods=["POST"])
def create_review():
    data = request.get_json() or {}

    book_id = data.get("book_id")
    user_id = data.get("user_id")
    rating = data.get("rating")

    if not book_id or not user_id or rating is None:
        return jsonify({"message": "book_id, user_id, rating 은 필수입니다."}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({"message": "rating 은 1~5 사이의 정수여야 합니다."}), 400

    if not Book.query.get(book_id):
        return jsonify({"message": "도서를 찾을 수 없습니다."}), 404
    if not User.query.get(user_id):
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    review = Review(
        book_id=book_id,
        user_id=user_id,
        rating=rating,
        title=data.get("title"),
        content=data.get("content"),
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        "id": review.id,
        "book_id": review.book_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "title": review.title,
        "content": review.content,
        "created_at": review.created_at.isoformat()
    }), 201


@bp.route("", methods=["GET"])
def list_reviews():
    query = Review.query.filter(Review.deleted_at.is_(None))

    book_id = request.args.get("book_id")
    user_id = request.args.get("user_id")

    if book_id:
        query = query.filter(Review.book_id == book_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)

    reviews = query.order_by(Review.created_at.desc()).all()

    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "book_id": r.book_id,
            "user_id": r.user_id,
            "rating": r.rating,
            "title": r.title,
            "content": r.content,
            "created_at": r.created_at.isoformat()
        })

    return jsonify(result), 200


@bp.route("/<int:review_id>", methods=["GET"])
def get_review(review_id):
    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": review.id,
        "book_id": review.book_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "title": review.title,
        "content": review.content,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat()
    }), 200


@bp.route("/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    data = request.get_json() or {}

    if "rating" in data:
        rating = int(data["rating"])
        if not (1 <= rating <= 5):
            return jsonify({"message": "rating 은 1~5 사이의 정수여야 합니다."}), 400
        review.rating = rating

    review.title = data.get("title", review.title)
    review.content = data.get("content", review.content)

    db.session.commit()
    return jsonify({"message": "리뷰가 수정되었습니다."}), 200


@bp.route("/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    review.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "리뷰가 삭제되었습니다."}), 200
