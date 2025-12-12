from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Cart, User, Book

bp = Blueprint("cart", __name__)


@bp.route("", methods=["POST"])
def add_to_cart():
    data = request.get_json() or {}

    user_id = data.get("user_id")
    book_id = data.get("book_id")
    quantity = data.get("quantity", 1)

    if not user_id or not book_id:
        return jsonify({"message": "user_id, book_id 는 필수입니다."}), 400

    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "quantity 는 정수여야 합니다."}), 400

    if quantity < 1:
        return jsonify({"message": "quantity 는 최소 1 이상이어야 합니다."}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "도서를 찾을 수 없습니다."}), 404

    existing = Cart.query.filter(
        Cart.user_id == user_id,
        Cart.book_id == book_id,
        Cart.deleted_at.is_(None)
    ).first()

    if existing:
        existing.quantity += quantity
        existing.unit_price = book.price  # 최신 가격으로 동기화
        db.session.commit()
        return jsonify({"message": "장바구니 수량이 증가했습니다."}), 200

    cart_item = Cart(
        user_id=user_id,
        book_id=book_id,
        quantity=quantity,
        unit_price=book.price,
    )
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({
        "id": cart_item.id,
        "user_id": cart_item.user_id,
        "book_id": cart_item.book_id,
        "quantity": cart_item.quantity,
        "unit_price": str(cart_item.unit_price),
        "created_at": cart_item.created_at.isoformat()
    }), 201


@bp.route("", methods=["GET"])
def list_cart():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "user_id 쿼리 파라미터는 필수입니다."}), 400

    items = Cart.query.filter(
        Cart.user_id == user_id,
        Cart.deleted_at.is_(None)
    ).order_by(Cart.created_at.desc()).all()

    result = []
    for item in items:
        result.append({
            "id": item.id,
            "user_id": item.user_id,
            "book_id": item.book_id,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "created_at": item.created_at.isoformat(),
        })

    return jsonify(result), 200


@bp.route("/<int:item_id>", methods=["PUT"])
def update_cart_item(item_id):
    cart_item = Cart.query.get(item_id)
    if not cart_item or cart_item.deleted_at is not None:
        return jsonify({"message": "장바구니 항목을 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    quantity = data.get("quantity")

    if quantity is None:
        return jsonify({"message": "quantity 는 필수입니다."}), 400

    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "quantity 는 정수여야 합니다."}), 400

    if quantity < 1:
        return jsonify({"message": "quantity 는 최소 1 이상이어야 합니다."}), 400

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({"message": "장바구니 수량이 수정되었습니다."}), 200


@bp.route("/<int:item_id>", methods=["DELETE"])
def delete_cart_item(item_id):
    cart_item = Cart.query.get(item_id)
    if not cart_item or cart_item.deleted_at is not None:
        return jsonify({"message": "장바구니 항목을 찾을 수 없습니다."}), 404

    cart_item.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "장바구니 항목이 삭제되었습니다."}), 200
