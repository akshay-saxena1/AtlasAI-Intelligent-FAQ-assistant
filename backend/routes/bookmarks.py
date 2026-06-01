"""
Bookmark and Feedback API routes.

Provides CRUD operations for saved bookmarks and user feedback
submission on chat responses.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.models import (
    BookmarkRequest,
    BookmarkResponse,
    FeedbackRequest,
)
from backend.database import execute_query

router: APIRouter = APIRouter(prefix="/api", tags=["Bookmarks & Feedback"])


# ============================================================
# Bookmark Routes
# ============================================================


@router.get("/bookmarks/{session_id}", response_model=list[BookmarkResponse])
async def list_bookmarks(session_id: str) -> list[BookmarkResponse]:
    """List all bookmarks for a given session.

    Returns bookmarks with denormalized FAQ question and category
    for display in the sidebar.

    Args:
        session_id: The user's session identifier.

    Returns:
        list[BookmarkResponse]: Bookmarked FAQs for the session.

    Time Complexity: O(B) where B is the bookmark count for this session
    Space Complexity: O(B)
    """
    bookmarks: list[dict] = execute_query(
        """
        SELECT sb.id, sb.session_id, sb.faq_id,
               f.question, c.name AS category, sb.created_at
        FROM saved_bookmarks sb
        JOIN faqs f ON sb.faq_id = f.id
        JOIN categories c ON f.category_id = c.id
        WHERE sb.session_id = ?
        ORDER BY sb.created_at DESC
        """,
        (session_id,),
    )
    return [BookmarkResponse(**b) for b in bookmarks]


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(bookmark: BookmarkRequest) -> BookmarkResponse:
    """Bookmark a FAQ for later reference.

    Enforces uniqueness per (session_id, faq_id) pair via
    the UNIQUE constraint in the schema.

    Args:
        bookmark: BookmarkRequest with session_id and faq_id.

    Returns:
        BookmarkResponse: The created bookmark record.

    Raises:
        HTTPException: 400 if FAQ doesn't exist or already bookmarked.

    Time Complexity: O(1) (indexed insert)
    Space Complexity: O(1)
    """
    # Validate FAQ exists
    faq: dict | None = execute_query(
        "SELECT id FROM faqs WHERE id = ?",
        (bookmark.faq_id,),
        fetch_one=True,
    )
    if not faq:
        raise HTTPException(status_code=400, detail="FAQ not found")

    # Check for duplicate
    existing: dict | None = execute_query(
        """
        SELECT id FROM saved_bookmarks
        WHERE session_id = ? AND faq_id = ?
        """,
        (bookmark.session_id, bookmark.faq_id),
        fetch_one=True,
    )
    if existing:
        raise HTTPException(status_code=400, detail="FAQ already bookmarked")

    bookmark_id: int = execute_query(
        "INSERT INTO saved_bookmarks (session_id, faq_id) VALUES (?, ?)",
        (bookmark.session_id, bookmark.faq_id),
    )

    # Fetch the complete bookmark record
    result: dict = execute_query(
        """
        SELECT sb.id, sb.session_id, sb.faq_id,
               f.question, c.name AS category, sb.created_at
        FROM saved_bookmarks sb
        JOIN faqs f ON sb.faq_id = f.id
        JOIN categories c ON f.category_id = c.id
        WHERE sb.id = ?
        """,
        (bookmark_id,),
        fetch_one=True,
    )
    return BookmarkResponse(**result)


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(bookmark_id: int) -> None:
    """Remove a saved bookmark.

    Args:
        bookmark_id: The bookmark primary key to delete.

    Raises:
        HTTPException: 404 if bookmark not found.

    Time Complexity: O(1) (indexed delete)
    Space Complexity: O(1)
    """
    existing: dict | None = execute_query(
        "SELECT id FROM saved_bookmarks WHERE id = ?",
        (bookmark_id,),
        fetch_one=True,
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    execute_query(
        "DELETE FROM saved_bookmarks WHERE id = ?",
        (bookmark_id,),
    )


# ============================================================
# Feedback Routes
# ============================================================


@router.post("/feedback", status_code=201)
async def submit_feedback(feedback: FeedbackRequest) -> dict[str, Any]:
    """Submit helpfulness feedback on a chat response.

    Records a boolean is_helpful flag against a specific chat
    interaction for analytics tracking.

    Args:
        feedback: FeedbackRequest with chat_id and is_helpful.

    Returns:
        dict: Confirmation with the feedback ID.

    Raises:
        HTTPException: 400 if chat_id doesn't exist.

    Time Complexity: O(1) (indexed insert)
    Space Complexity: O(1)
    """
    # Validate chat exists
    chat: dict | None = execute_query(
        "SELECT id FROM chat_history WHERE id = ?",
        (feedback.chat_id,),
        fetch_one=True,
    )
    if not chat:
        raise HTTPException(status_code=400, detail="Chat record not found")

    feedback_id: int = execute_query(
        "INSERT INTO user_feedback (chat_id, is_helpful) VALUES (?, ?)",
        (feedback.chat_id, feedback.is_helpful),
    )

    return {"id": feedback_id, "message": "Feedback recorded successfully"}
