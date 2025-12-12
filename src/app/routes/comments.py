from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Comment, Review, User

bp = Blueprint("comments", __name__)


@bp.route("/reviews/<int:review_id>/comments", methods=["POST"])
def create_comment(review_id):
    data = request.get_json() or {}

    user_id = data.get("user_id")
    content = data.get("content")
    parent_id = data.get("parent_id")

    if not user_id or not content:
        return jsonify({"message": "user_id, content 는 필수입니다."}), 400

    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    if not User.query.get(user_id):
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    parent = None
    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent or parent.deleted_at is not None:
            return jsonify({"message": "부모 댓글을 찾을 수 없습니다."}), 404

    comment = Comment(
        review_id=review_id,
        user_id=user_id,
        content=content,
        parent=parent,
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "id": comment.id,
        "review_id": comment.review_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at.isoformat()
    }), 201


@bp.route("/reviews/<int:review_id>/comments", methods=["GET"])
def list_comments(review_id):
    review = Review.query.get(review_id)
    if not review or review.deleted_at is not None:
        return jsonify({"message": "리뷰를 찾을 수 없습니다."}), 404

    comments = Comment.query.filter(
        Comment.review_id == review_id,
        Comment.deleted_at.is_(None)
    ).order_by(Comment.created_at.asc()).all()

    result = []
    for c in comments:
        result.append({
            "id": c.id,
            "review_id": c.review_id,
            "user_id": c.user_id,
            "content": c.content,
            "parent_id": c.parent_id,
            "created_at": c.created_at.isoformat()
        })

    return jsonify(result), 200


@bp.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment or comment.deleted_at is not None:
        return jsonify({"message": "댓글을 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    content = data.get("content")
    if not content:
        return jsonify({"message": "content 는 필수입니다."}), 400

    comment.content = content
    db.session.commit()

    return jsonify({"message": "댓글이 수정되었습니다."}), 200


@bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment or comment.deleted_at is not None:
        return jsonify({"message": "댓글을 찾을 수 없습니다."}), 404

    comment.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "댓글이 삭제되었습니다."}), 200
