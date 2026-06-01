"""
Admin API routes for FAQ CRUD management.

Provides full Create, Read, Update, Delete operations on the FAQ
database with search engine re-indexing on mutations. Includes
category management and bulk operations.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.models import (
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    CategoryResponse,
)
from backend.database import execute_query
from backend.nlp.search_engine import search_engine, initialize_search_engine

router: APIRouter = APIRouter(prefix="/api/faqs", tags=["Admin"])


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories() -> list[CategoryResponse]:
    """List all FAQ categories with their FAQ counts.

    Returns categories ordered alphabetically with aggregated
    FAQ counts for dashboard display.

    Returns:
        list[CategoryResponse]: All categories with faq_count.

    Time Complexity: O(C) where C is the number of categories
    Space Complexity: O(C)
    """
    categories: list[dict] = execute_query(
        """
        SELECT c.id, c.name, c.icon,
               COUNT(f.id) AS faq_count
        FROM categories c
        LEFT JOIN faqs f ON c.id = f.category_id
        GROUP BY c.id
        ORDER BY c.name
        """
    )
    return [CategoryResponse(**c) for c in categories]


@router.get("/", response_model=list[FAQResponse])
async def list_faqs(
    category_id: int | None = Query(None, description="Filter by category ID"),
    search: str | None = Query(None, description="Search in questions"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[FAQResponse]:
    """List FAQs with optional filtering and pagination.

    Supports filtering by category and keyword search in questions.

    Args:
        category_id: Optional category filter.
        search: Optional substring search in question text.
        limit: Maximum results per page (1–500).
        offset: Pagination offset.

    Returns:
        list[FAQResponse]: Matching FAQ records.

    Time Complexity: O(N) where N is the filtered result count
    Space Complexity: O(min(N, limit))
    """
    query: str = """
        SELECT f.id, f.category_id, c.name AS category_name,
               f.question, f.answer, f.view_count,
               f.created_at, f.updated_at
        FROM faqs f
        JOIN categories c ON f.category_id = c.id
        WHERE 1=1
    """
    params: list[Any] = []

    if category_id is not None:
        query += " AND f.category_id = ?"
        params.append(category_id)

    if search:
        query += " AND f.question LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY f.id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    faqs: list[dict] = execute_query(query, tuple(params))
    return [FAQResponse(**f) for f in faqs]


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(faq_id: int) -> FAQResponse:
    """Retrieve a single FAQ by ID.

    Args:
        faq_id: The FAQ primary key.

    Returns:
        FAQResponse: The requested FAQ record.

    Raises:
        HTTPException: 404 if FAQ not found.

    Time Complexity: O(1) (indexed lookup)
    Space Complexity: O(1)
    """
    faq: dict | None = execute_query(
        """
        SELECT f.id, f.category_id, c.name AS category_name,
               f.question, f.answer, f.view_count,
               f.created_at, f.updated_at
        FROM faqs f
        JOIN categories c ON f.category_id = c.id
        WHERE f.id = ?
        """,
        (faq_id,),
        fetch_one=True,
    )

    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    return FAQResponse(**faq)


@router.post("/", response_model=FAQResponse, status_code=201)
async def create_faq(faq: FAQCreate) -> FAQResponse:
    """Create a new FAQ entry and re-index the search engine.

    Args:
        faq: FAQCreate model with category_id, question, and answer.

    Returns:
        FAQResponse: The newly created FAQ record.

    Raises:
        HTTPException: 400 if category doesn't exist.

    Time Complexity: O(N × L) for re-indexing after insert
    Space Complexity: O(1) for the insert, O(N × D) for re-index
    """
    # Validate category exists
    category: dict | None = execute_query(
        "SELECT id FROM categories WHERE id = ?",
        (faq.category_id,),
        fetch_one=True,
    )
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    faq_id: int = execute_query(
        "INSERT INTO faqs (category_id, question, answer) VALUES (?, ?, ?)",
        (faq.category_id, faq.question, faq.answer),
    )

    # Re-index search engine to include new FAQ
    initialize_search_engine()

    return await get_faq(faq_id)


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(faq_id: int, faq: FAQUpdate) -> FAQResponse:
    """Update an existing FAQ and re-index the search engine.

    Only provided fields are updated (partial update pattern).

    Args:
        faq_id: The FAQ ID to update.
        faq: FAQUpdate model with optional fields.

    Returns:
        FAQResponse: The updated FAQ record.

    Raises:
        HTTPException: 404 if FAQ not found.

    Time Complexity: O(N × L) for re-indexing after update
    Space Complexity: O(1) for the update
    """
    existing: dict | None = execute_query(
        "SELECT id FROM faqs WHERE id = ?",
        (faq_id,),
        fetch_one=True,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="FAQ not found")

    update_fields: list[str] = []
    update_values: list[Any] = []

    if faq.category_id is not None:
        update_fields.append("category_id = ?")
        update_values.append(faq.category_id)
    if faq.question is not None:
        update_fields.append("question = ?")
        update_values.append(faq.question)
    if faq.answer is not None:
        update_fields.append("answer = ?")
        update_values.append(faq.answer)

    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(faq_id)
        execute_query(
            f"UPDATE faqs SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values),
        )
        # Re-index search engine with updated content
        initialize_search_engine()

    return await get_faq(faq_id)


@router.delete("/{faq_id}", status_code=204)
async def delete_faq(faq_id: int) -> None:
    """Delete a FAQ and re-index the search engine.

    Args:
        faq_id: The FAQ ID to delete.

    Raises:
        HTTPException: 404 if FAQ not found.

    Time Complexity: O(N × L) for re-indexing after delete
    Space Complexity: O(1) for the delete
    """
    existing: dict | None = execute_query(
        "SELECT id FROM faqs WHERE id = ?",
        (faq_id,),
        fetch_one=True,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="FAQ not found")

    execute_query("DELETE FROM faqs WHERE id = ?", (faq_id,))

    # Re-index search engine without deleted FAQ
    initialize_search_engine()


@router.delete("/bulk/delete", status_code=204)
async def bulk_delete_faqs(faq_ids: list[int]) -> None:
    """Bulk delete multiple FAQs by ID.

    Args:
        faq_ids: List of FAQ IDs to delete.

    Time Complexity: O(K + N × L) where K=delete count, N×L=re-index
    Space Complexity: O(K) for the ID list
    """
    if not faq_ids:
        raise HTTPException(status_code=400, detail="No FAQ IDs provided")

    placeholders: str = ",".join("?" * len(faq_ids))
    execute_query(
        f"DELETE FROM faqs WHERE id IN ({placeholders})",
        tuple(faq_ids),
    )

    initialize_search_engine()
