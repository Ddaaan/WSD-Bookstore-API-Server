from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify

from ..extensions import db
from ..models import Book, Category, Author
from ..pagination import apply_pagination_and_sort
from ..error_handlers import ApiError
from ..error_codes import ErrorCodes
from ..auth_utils import jwt_required

bp = Blueprint("books", __name__)


def _parse_decimal(value, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message=f"{field_name} must be a numeric value.",
        )


def _parse_date(value, field_name: str):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message=f"{field_name} must follow YYYY-MM-DD format.",
        )


def _parse_int(value, field_name: str, min_value: int | None = None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message=f"{field_name} must be an integer.",
        )

    if min_value is not None and parsed < min_value:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message=f"{field_name} must be greater than or equal to {min_value}.",
        )

    return parsed


def _book_to_dict(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "price": str(book.price),
        "isbn13": book.isbn13,
        "published_at": book.published_at.isoformat() if book.published_at else None,
        "stock_cnt": book.stock_cnt,
        "status": book.status,
        "author": {
            "id": book.author_id,
            "name": book.author.name if book.author else None,
        },
        "category": {
            "id": book.category_id,
            "name": book.category.name if book.category else None,
        },
        "created_at": book.created_at.isoformat(),
        "updated_at": book.updated_at.isoformat(),
    }


# 도서 등록 (ADMIN 전용)
@bp.route("", methods=["POST"])
@jwt_required(role="ADMIN")
def create_book():
    data = request.get_json() or {}

    title = data.get("title")
    price_raw = data.get("price")
    stock_raw = data.get("stock_cnt", 0)
    category_id = data.get("category_id")
    author_id = data.get("author_id")

    if not title or price_raw is None or category_id is None or author_id is None:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="title, price, category_id, author_id are required.",
        )

    price = _parse_decimal(price_raw, "price")
    stock_cnt = _parse_int(stock_raw, "stock_cnt", min_value=0)

    category = Category.query.get(category_id)
    if not category:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="Category could not be found.",
            details={"category_id": category_id},
        )

    author = Author.query.get(author_id)
    if not author:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="Author could not be found.",
            details={"author_id": author_id},
        )

    published_at = _parse_date(data.get("published_at"), "published_at")

    book = Book(
        title=title,
        description=data.get("description"),
        price=price,
        isbn13=data.get("isbn13"),
        published_at=published_at,
        stock_cnt=stock_cnt,
        status=data.get("status", "ACTIVE"),
        category_id=category.id,
        author_id=author.id,
    )
    db.session.add(book)
    db.session.commit()

    return jsonify(_book_to_dict(book)), 201


# 도서 목록 조회
@bp.route("", methods=["GET"])
def list_books():
    query = Book.query

    keyword = request.args.get("keyword")
    status = request.args.get("status")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    category_filter = request.args.get("category_id")
    author_filter = request.args.get("author_id")

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (Book.title.ilike(like)) | (Book.description.ilike(like))
        )

    if status:
        query = query.filter(Book.status == status)

    try:
        if min_price is not None:
            query = query.filter(Book.price >= Decimal(str(min_price)))
        if max_price is not None:
            query = query.filter(Book.price <= Decimal(str(max_price)))
    except (InvalidOperation, TypeError):
        raise ApiError(
            status_code=400,
            code=ErrorCodes.INVALID_QUERY_PARAM,
            message="min_price and max_price must be numeric values.",
        )

    if category_filter:
        try:
            category_id = int(category_filter)
        except ValueError:
            raise ApiError(
                status_code=400,
                code=ErrorCodes.INVALID_QUERY_PARAM,
                message="category_id query parameter must be numeric.",
            )
        query = query.filter(Book.category_id == category_id)

    if author_filter:
        try:
            author_id = int(author_filter)
        except ValueError:
            raise ApiError(
                status_code=400,
                code=ErrorCodes.INVALID_QUERY_PARAM,
                message="author_id query parameter must be numeric.",
            )
        query = query.filter(Book.author_id == author_id)

    books, meta = apply_pagination_and_sort(
        query=query,
        model=Book,
        default_sort_field="created_at",
        default_sort_dir="DESC",
    )

    content = [_book_to_dict(b) for b in books]

    response = {
        "content": content,
        **meta,
    }
    return jsonify(response), 200


# 단일 도서 조회
@bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="Book could not be found.",
        )

    return jsonify(_book_to_dict(book)), 200


# 도서 수정 (ADMIN 전용)
@bp.route("/<int:book_id>", methods=["PUT"])
@jwt_required(role="ADMIN")
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="Book could not be found.",
        )

    data = request.get_json() or {}

    if "category_id" in data:
        category = Category.query.get(data["category_id"])
        if not category:
            raise ApiError(
                status_code=404,
                code=ErrorCodes.RESOURCE_NOT_FOUND,
                message="Category could not be found.",
                details={"category_id": data["category_id"]},
            )
        book.category_id = category.id

    if "author_id" in data:
        author = Author.query.get(data["author_id"])
        if not author:
            raise ApiError(
                status_code=404,
                code=ErrorCodes.RESOURCE_NOT_FOUND,
                message="Author could not be found.",
                details={"author_id": data["author_id"]},
            )
        book.author_id = author.id

    if "title" in data:
        book.title = data["title"]
    if "description" in data:
        book.description = data["description"]
    if "price" in data:
        book.price = _parse_decimal(data["price"], "price")
    if "isbn13" in data:
        book.isbn13 = data["isbn13"]
    if "published_at" in data:
        book.published_at = _parse_date(data["published_at"], "published_at")
    if "stock_cnt" in data:
        book.stock_cnt = _parse_int(data["stock_cnt"], "stock_cnt", min_value=0)
    if "status" in data:
        book.status = data["status"]

    db.session.commit()
    return jsonify(_book_to_dict(book)), 200


# 도서 삭제 (ADMIN 전용)
@bp.route("/<int:book_id>", methods=["DELETE"])
@jwt_required(role="ADMIN")
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        raise ApiError(
            status_code=404,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            message="Book could not be found.",
        )

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "Book deleted."}), 200
