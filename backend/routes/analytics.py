"""
Analytics API routes for the Admin Dashboard.

Provides aggregated statistics, time-series query data, category
distributions, and search success metrics for the Recharts-powered
dashboard visualization.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

from typing import Any

from fastapi import APIRouter, Query

from backend.models import DashboardStats, QueryOverTime, CategoryStats
from backend.database import execute_query
from backend.config import get_settings

router: APIRouter = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    """Retrieve aggregated dashboard statistics.

    Computes totals, success rates, and averages across all
    chat interactions and feedback submissions.

    Returns:
        DashboardStats: Aggregated metrics for the dashboard.

    Time Complexity: O(H + F) where H=chat_history rows, F=feedback rows
    Space Complexity: O(1) for scalar aggregates
    """
    settings = get_settings()

    # Total queries
    total_row: dict = execute_query(
        "SELECT COUNT(*) AS total FROM chat_history",
        fetch_one=True,
    )
    total_queries: int = total_row["total"] if total_row else 0

    # Successful matches (confidence >= threshold)
    success_row: dict = execute_query(
        "SELECT COUNT(*) AS total FROM chat_history WHERE confidence_score >= ?",
        (settings.confidence_threshold,),
        fetch_one=True,
    )
    successful_matches: int = success_row["total"] if success_row else 0

    # Success rate
    success_rate: float = (
        (successful_matches / total_queries * 100) if total_queries > 0 else 0.0
    )

    # Total FAQs
    faq_row: dict = execute_query(
        "SELECT COUNT(*) AS total FROM faqs",
        fetch_one=True,
    )
    total_faqs: int = faq_row["total"] if faq_row else 0

    # Feedback stats
    feedback_row: dict = execute_query(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN is_helpful = 1 THEN 1 ELSE 0 END) AS positive
        FROM user_feedback
        """,
        fetch_one=True,
    )
    total_feedback: int = feedback_row["total"] if feedback_row else 0
    positive_feedback: int = feedback_row["positive"] if feedback_row and feedback_row["positive"] else 0

    # Average confidence
    avg_row: dict = execute_query(
        "SELECT AVG(confidence_score) AS avg_conf FROM chat_history",
        fetch_one=True,
    )
    avg_confidence: float = round(avg_row["avg_conf"], 4) if avg_row and avg_row["avg_conf"] else 0.0

    return DashboardStats(
        total_queries=total_queries,
        successful_matches=successful_matches,
        success_rate=round(success_rate, 2),
        total_faqs=total_faqs,
        total_feedback=total_feedback,
        positive_feedback=positive_feedback,
        avg_confidence=avg_confidence,
    )


@router.get("/queries-over-time", response_model=list[QueryOverTime])
async def get_queries_over_time(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
) -> list[QueryOverTime]:
    """Retrieve time-series data for queries per day.

    Groups chat history by date for the spline chart visualization.

    Args:
        days: Number of days to look back (1–365, default 30).

    Returns:
        list[QueryOverTime]: Daily query counts ordered chronologically.

    Time Complexity: O(H) where H is the chat_history rows in range
    Space Complexity: O(D) where D is the number of distinct days
    """
    rows: list[dict] = execute_query(
        """
        SELECT DATE(created_at) AS date, COUNT(*) AS count
        FROM chat_history
        WHERE created_at >= DATE('now', ?)
        GROUP BY DATE(created_at)
        ORDER BY date ASC
        """,
        (f"-{days} days",),
    )
    return [QueryOverTime(**r) for r in rows]


@router.get("/categories", response_model=list[CategoryStats])
async def get_category_stats() -> list[CategoryStats]:
    """Retrieve query distribution across categories.

    Aggregates matched FAQ categories from chat history for the
    horizontal bar chart visualization.

    Returns:
        list[CategoryStats]: Category query counts, descending.

    Time Complexity: O(H) where H is chat_history rows with matches
    Space Complexity: O(C) where C is the number of categories
    """
    rows: list[dict] = execute_query(
        """
        SELECT c.name AS category, COUNT(ch.id) AS count
        FROM chat_history ch
        JOIN faqs f ON ch.matched_faq_id = f.id
        JOIN categories c ON f.category_id = c.id
        WHERE ch.matched_faq_id IS NOT NULL
        GROUP BY c.name
        ORDER BY count DESC
        """
    )
    return [CategoryStats(**r) for r in rows]


@router.get("/recent-queries")
async def get_recent_queries(
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Retrieve the most recent chat queries for the admin feed.

    Args:
        limit: Maximum number of recent queries (1–100).

    Returns:
        list[dict]: Recent query records with scoring metadata.

    Time Complexity: O(limit) with index on created_at
    Space Complexity: O(limit)
    """
    rows: list[dict] = execute_query(
        """
        SELECT ch.id, ch.session_id, ch.user_query, ch.bot_response,
               ch.confidence_score, ch.semantic_score, ch.lexical_score,
               ch.created_at,
               CASE WHEN ch.matched_faq_id IS NOT NULL THEN 1 ELSE 0 END AS was_matched
        FROM chat_history ch
        ORDER BY ch.created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    return rows
