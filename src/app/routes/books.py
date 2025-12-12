from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Book, Category
from ..pagination import apply_pagination_and_sort
from ..error_handlers import ApiError
from ..error_codes import ErrorCodes
bp = Blueprint("books", __name__)

# 도서 등록
@bp.route("", methods=["POST"])
def create_book():
    data = request.get_json() or {}

    title = data.get("title")
    price = data.get("price")
    stock = data.get("stock_cnt", 0)

    if not title or price is None:
        return jsonify({"message": "title, price 는 필수입니다."}), 400

    book = Book(
        title=title,
        description=data.get("description"),
        price=price,
        isbn13=data.get("isbn13"),
        published_at=data.get("published_at"),
        stock_cnt=stock,
        status=data.get("status", "ACTIVE"),
    )
    db.session.add(book)
    db.session.commit()

    return jsonify({
        "id": book.id,
        "title": book.title,
        "price": str(book.price),
        "stock_cnt": book.stock_cnt,
        "status": book.status
    }), 201


# 도서 목록 조회
@bp.route("", methods=["GET"])
def list_books():
    """
    도서 목록 조회
    쿼리 파라미터 예시:
      - page, size
      - sort=created_at,DESC
      - keyword=검색어 (title 또는 description에 포함)
      - status=ACTIVE
      - min_price, max_price
    """
    query = Book.query

    keyword = request.args.get("keyword")
    status = request.args.get("status")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (Book.title.ilike(like)) | (Book.description.ilike(like))
        )

    if status:
        query = query.filter(Book.status == status)

    # 가격 필터
    try:
        if min_price is not None:
            query = query.filter(Book.price >= float(min_price))
        if max_price is not None:
            query = query.filter(Book.price <= float(max_price))
    except ValueError:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.INVALID_QUERY_PARAM,
            message="min_price, max_price 는 숫자여야 합니다.",
        )

    books, meta = apply_pagination_and_sort(
        query=query,
        model=Book,
        default_sort_field="created_at",
        default_sort_dir="DESC",
    )

    content = []
    for b in books:
        content.append({
            "id": b.id,
            "title": b.title,
            "description": b.description,
            "price": str(b.price),
            "status": b.status,
            "stock_cnt": b.stock_cnt,
            "created_at": b.created_at.isoformat(),
        })

    response = {
        "content": content,
        **meta,
    }
    return jsonify(response), 200



# 특정 도서 조회
@bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "책을 찾을 수 없습니다."}), 404

    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "stock": book.stock
    }), 200


# 도서 수정
@bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "책을 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.price = data.get("price", book.price)
    book.stock = data.get("stock", book.stock)

    db.session.commit()
    return jsonify({"message": "수정되었습니다."}), 200


# 도서 삭제
@bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "책을 찾을 수 없습니다."}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "삭제되었습니다."}), 200
