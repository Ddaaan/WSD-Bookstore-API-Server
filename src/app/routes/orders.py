from datetime import datetime
from decimal import Decimal

from flask import Blueprint, request, jsonify, g 
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Order, OrderItem, User, Book, Cart
from ..auth_utils import jwt_required

bp = Blueprint("orders", __name__)

ALLOWED_STATUSES = {"PENDING", "PAID", "CANCELLED", "SHIPPED", "COMPLETED"}


def decimal_to_str(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


@bp.route("", methods=["POST"])
@jwt_required()   # 로그인한 사용자만 주문 생성 가능
def create_order():
    data = request.get_json() or {}

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id 는 필수입니다."}), 400

    if int(user_id) != g.current_user.id and g.current_user.role != "ADMIN":
        return jsonify({"message": "본인 주문만 생성할 수 있습니다."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    items = data.get("items", [])
    if not items:
        return jsonify({"message": "주문할 items 배열은 비어 있을 수 없습니다."}), 400

    order_items: list[OrderItem] = []
    total_amount = Decimal("0")

    # 재고 체크 및 주문 항목 생성
    for item in items:
        book_id = item.get("book_id")
        quantity = item.get("quantity", 1)

        if not book_id:
            return jsonify({"message": "각 항목의 book_id 는 필수입니다."}), 400

        try:
            quantity = int(quantity)
        except ValueError:
            return jsonify({"message": "quantity 는 정수여야 합니다."}), 400

        if quantity < 1:
            return jsonify({"message": "quantity 는 최소 1 이상이어야 합니다."}), 400

        book = Book.query.get(book_id)
        if not book:
            return jsonify({"message": f"도서를 찾을 수 없습니다. book_id={book_id}"}), 404

        if book.stock_cnt is not None and book.stock_cnt < quantity:
            return jsonify({
                "message": "재고가 부족하여 주문할 수 없습니다.",
                "details": f"book_id={book_id}, 재고={book.stock_cnt}, 요청수량={quantity}"
            }), 409

        oi = OrderItem(
            book_id=book_id,
            quantity=quantity,
            unit_price=book.price,
        )
        order_items.append(oi)
        total_amount += (book.price * quantity)

    order = Order(
        user_id=user_id,
        status="PENDING",
        total_amount=total_amount,
    )
    db.session.add(order)
    db.session.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.session.add(oi)

        book = Book.query.get(oi.book_id)
        if book and book.stock_cnt is not None:
            book.stock_cnt -= oi.quantity

    db.session.commit()

    return jsonify({
        "order_id": order.id,
        "total_amount": decimal_to_str(order.total_amount),
        "status": order.status,
        "created_at": order.created_at.isoformat()
    }), 201


@bp.route("", methods=["GET"])
def list_orders():
    """
    주문 목록 조회
    쿼리 파라미터:
      - user_id: 해당 사용자의 주문만 조회
      - status: 특정 상태만 필터링 (PENDING, PAID, CANCELLED, SHIPPED, COMPLETED)
    """
    query = Order.query.filter(Order.deleted_at.is_(None))

    user_id = request.args.get("user_id")
    status = request.args.get("status")

    if user_id:
        query = query.filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "user_id": o.user_id,
            "status": o.status,
            "total_amount": decimal_to_str(o.total_amount),
            "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            "created_at": o.created_at.isoformat(),
        })

    return jsonify(result), 200


@bp.route("/<int:order_id>", methods=["GET"])
def get_order_detail(order_id):
    """
    주문 상세 조회 (주문 + 주문항목)
    """
    order = Order.query.get(order_id)
    if not order or order.deleted_at is not None:
        return jsonify({"message": "주문을 찾을 수 없습니다."}), 404

    items = []
    for item in order.items.order_by(OrderItem.id.asc()).all():
        items.append({
            "id": item.id,
            "book_id": item.book_id,
            "quantity": item.quantity,
            "unit_price": decimal_to_str(item.unit_price),
            "created_at": item.created_at.isoformat(),
        })

    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": decimal_to_str(order.total_amount),
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
        "items": items,
    }), 200


@bp.route("/<int:order_id>/status", methods=["PATCH"])
@jwt_required(role="ADMIN")
def update_order_status(order_id):
    """
    주문 상태 변경
    요청 바디 예시:
    { "status": "PAID" }
    """
    order = Order.query.get(order_id)
    if not order or order.deleted_at is not None:
        return jsonify({"message": "주문을 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status:
        return jsonify({"message": "status 필드는 필수입니다."}), 400

    if new_status not in ALLOWED_STATUSES:
        return jsonify({
            "message": "허용되지 않는 주문 상태입니다.",
            "details": f"허용 상태: {sorted(ALLOWED_STATUSES)}"
        }), 400

    if order.status == "CANCELLED":
        return jsonify({"message": "취소된 주문은 상태를 변경할 수 없습니다."}), 409

    if new_status == "PAID" and order.paid_at is None:
        order.paid_at = datetime.utcnow()

    order.status = new_status
    db.session.commit()

    return jsonify({
        "id": order.id,
        "from_status": order.status,
        "status": order.status,
        "updated_at": order.updated_at.isoformat(),
    }), 200
