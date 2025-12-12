from datetime import datetime
from decimal import Decimal

from flask import Blueprint, request, jsonify, g
from ..extensions import db
from ..models import Order, OrderItem, User, Book
from ..auth_utils import jwt_required
from ..error_handlers import ApiError
from ..error_codes import ErrorCodes
from ..pagination import apply_pagination_and_sort

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
    """
    주문 생성
    요청 예시:
    {
      "user_id": 1,
      "items": [
        { "book_id": 1, "quantity": 2 },
        { "book_id": 3, "quantity": 1 }
      ]
    }
    """
    data = request.get_json() or {}

    user_id = data.get("user_id")
    if not user_id:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="user_id 는 필수입니다.",
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.INVALID_QUERY_PARAM,
            message="user_id 는 정수여야 합니다.",
        )

    # 본인 또는 ADMIN만 해당 user_id로 주문 생성 가능
    if user_id_int != g.current_user.id and g.current_user.role != "ADMIN":
        raise ApiError(
            status_code=403,
            code=ErrorCodes.FORBIDDEN,
            message="본인 주문만 생성할 수 있습니다.",
        )

    user = User.query.get(user_id_int)
    if not user:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다.",
        )

    items = data.get("items", [])
    if not items:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="주문할 items 배열은 비어 있을 수 없습니다.",
        )

    order_items: list[OrderItem] = []
    total_amount = Decimal("0")

    # 재고 체크 및 주문 항목 생성
    for item in items:
        book_id = item.get("book_id")
        quantity = item.get("quantity", 1)

        if not book_id:
            raise ApiError(
                status_code=400,
                code=ErrorCodes.VALIDATION_FAILED,
                message="각 항목의 book_id 는 필수입니다.",
            )

        try:
            quantity = int(quantity)
        except ValueError:
            raise ApiError(
                status_code=400,
                code=ErrorCodes.VALIDATION_FAILED,
                message="quantity 는 정수여야 합니다.",
            )

        if quantity < 1:
            raise ApiError(
                status_code=400,
                code=ErrorCodes.VALIDATION_FAILED,
                message="quantity 는 최소 1 이상이어야 합니다.",
            )

        book = Book.query.get(book_id)
        if not book:
            raise ApiError(
                status_code=404,
                code=ErrorCodes.RESOURCE_NOT_FOUND,
                message=f"도서를 찾을 수 없습니다.",
                details={"book_id": book_id},
            )

        if book.stock_cnt is not None and book.stock_cnt < quantity:
            raise ApiError(
                status_code=409,
                code=ErrorCodes.STATE_CONFLICT,
                message="재고가 부족하여 주문할 수 없습니다.",
                details={
                    "book_id": book_id,
                    "stock_cnt": book.stock_cnt,
                    "requested": quantity,
                },
            )

        oi = OrderItem(
            book_id=book_id,
            quantity=quantity,
            unit_price=book.price,
        )
        order_items.append(oi)
        total_amount += (book.price * quantity)

    # 주문 생성
    order = Order(
        user_id=user_id_int,
        status="PENDING",
        total_amount=total_amount,
    )
    db.session.add(order)
    db.session.flush()  # order.id 확보

    # 주문 항목 저장 + 재고 차감
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
@jwt_required()   # 자신의 주문만 기본 조회 (관리자는 전체 조회 가능하게 확장 가능)
def list_orders():
    """
    주문 목록 조회
    쿼리 파라미터:
      - user_id (관리자일 때 다른 사람 주문 조회 가능)
      - status
      - page, size
      - sort=created_at,DESC
    """
    from ..pagination import apply_pagination_and_sort

    query = Order.query.filter(Order.deleted_at.is_(None))

    # 기본: 본인 주문만
    user_id_param = request.args.get("user_id")
    if user_id_param:
        # ADMIN이면 다른 사용자 주문도 조회 가능
        if g.current_user.role == "ADMIN":
            query = query.filter(Order.user_id == user_id_param)
        else:
            query = query.filter(Order.user_id == g.current_user.id)
    else:
        query = query.filter(Order.user_id == g.current_user.id)

    status = request.args.get("status")
    if status:
        query = query.filter(Order.status == status)

    orders, meta = apply_pagination_and_sort(
        query=query,
        model=Order,
        default_sort_field="created_at",
        default_sort_dir="DESC",
    )

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

    response = {
        "content": result,
        **meta,
    }
    return jsonify(response), 200


@bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_detail(order_id):
    """
    주문 상세 조회 (주문 + 주문항목)
    - 일반 유저: 자신의 주문만 조회 가능
    - ADMIN: 아무 주문이나 조회 가능
    """
    order = Order.query.get(order_id)
    if not order or order.deleted_at is not None:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="주문을 찾을 수 없습니다.",
        )

    if g.current_user.role != "ADMIN" and order.user_id != g.current_user.id:
        raise ApiError(
            status_code=403,
            code=ErrorCodes.FORBIDDEN,
            message="본인의 주문만 조회할 수 있습니다.",
        )

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
    주문 상태 변경 (ADMIN 전용)
    요청 바디 예시:
    { "status": "PAID" }
    """
    order = Order.query.get(order_id)
    if not order or order.deleted_at is not None:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="주문을 찾을 수 없습니다.",
        )

    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="status 필드는 필수입니다.",
        )

    if new_status not in ALLOWED_STATUSES:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.UNPROCESSABLE_ENTITY,
            message="허용되지 않는 주문 상태입니다.",
            details={"allowed": sorted(ALLOWED_STATUSES)},
        )

    if order.status == "CANCELLED":
        raise ApiError(
            status_code=409,
            code=ErrorCodes.STATE_CONFLICT,
            message="취소된 주문은 상태를 변경할 수 없습니다.",
        )

    if new_status == "PAID" and order.paid_at is None:
        order.paid_at = datetime.utcnow()

    order.status = new_status
    db.session.commit()

    return jsonify({
        "id": order.id,
        "status": order.status,
        "updated_at": order.updated_at.isoformat(),
    }), 200
