from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Review, User, ReviewLike

bp = Blueprint("review_likes", __name__)


@bp.route("/<int:review_id>/like", methods=["POST"])
def like_review(review_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id 는 필수입니다."}), 400

    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    if not User.query.get(user_id):
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    existing = ReviewLike.query.filter_by(user_id=user_id, review_id=review_id).first()
    if existing:
        return jsonify({"message": "이미 좋아요를 누른 리뷰입니다."}), 409

    like = ReviewLike(user_id=user_id, review_id=review_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"message": "리뷰에 좋아요를 추가했습니다."}), 201


@bp.route("/<int:review_id>/like", methods=["DELETE"])
def unlike_review(review_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id 는 필수입니다."}), 400

    like = ReviewLike.query.filter_by(user_id=user_id, review_id=review_id).first()
    if not like:
        return jsonify({"message": "좋아요 기록을 찾을 수 없습니다."}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"message": "리뷰 좋아요를 취소했습니다."}), 200
