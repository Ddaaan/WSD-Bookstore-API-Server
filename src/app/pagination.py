from math import ceil
from flask import request
from sqlalchemy.orm import Query


def apply_pagination_and_sort(
    query: Query,
    model,
    default_sort_field: str = "created_at",
    default_sort_dir: str = "DESC",
    max_size: int = 100,
):
    # page, size
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        size = int(request.args.get("size", 20))
    except ValueError:
        size = 20

    if page < 1:
        page = 1
    if size < 1:
        size = 1
    if size > max_size:
        size = max_size

    # sort=field,DESC|ASC
    sort_param = request.args.get("sort", f"{default_sort_field},{default_sort_dir}")
    sort_field, sort_dir = default_sort_field, default_sort_dir

    if "," in sort_param:
        sf, sd = sort_param.split(",", 1)
        sf = sf.strip()
        sd = sd.strip().upper()
        if hasattr(model, sf):
            sort_field = sf
        if sd in ("ASC", "DESC"):
            sort_dir = sd

    sort_column = getattr(model, sort_field, None)
    if sort_column is not None:
        if sort_dir == "DESC":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    total_elements = query.count()
    total_pages = ceil(total_elements / size) if total_elements > 0 else 1

    items = query.offset((page - 1) * size).limit(size).all()

    meta = {
        "page": page,
        "size": size,
        "totalElements": total_elements,
        "totalPages": total_pages,
        "sort": f"{sort_field},{sort_dir}",
    }

    return items, meta
