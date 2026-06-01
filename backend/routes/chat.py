"""
Chat API routes for the FAQ Chatbot.

Provides the main conversational endpoint, typeahead suggestions,
and chat history retrieval. Routes queries through the hybrid
search engine and persists interactions to SQLite.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.models import (
    ChatRequest,
    ChatResponse,
    SuggestionItem,
    TypeaheadSuggestion,
)
from backend.database import execute_query
from backend.nlp.search_engine import search_engine

router: APIRouter = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user query through the hybrid NLP search engine.

    Executes the full pipeline: preprocessing → TF-IDF scoring →
    semantic embedding → algorithmic fusion → threshold gating.
    Persists the interaction to chat_history and logs analytics.

    Args:
        request: ChatRequest with query text and session_id.

    Returns:
        ChatResponse: Structured response with answer, scores, and suggestions.

    Raises:
        HTTPException: 500 if the search engine encounters an error.

    Time Complexity: O(N × D + N × V) where N=FAQs, D=embed dim, V=vocab
    Space Complexity: O(N) for score computation
    """
    try:
        # Execute hybrid search
        result: dict[str, Any] = search_engine.search(request.query)

        # Build suggestion items
        suggestions: list[SuggestionItem] = [
            SuggestionItem(**s) for s in result.get("suggestions", [])
        ]

        # Persist to chat_history
        chat_id: int = execute_query(
            """
            INSERT INTO chat_history
                (session_id, user_query, bot_response, confidence_score,
                 matched_faq_id, semantic_score, lexical_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.session_id,
                request.query,
                result["answer"],
                result["confidence"],
                result.get("faq_id"),
                result["semantic_score"],
                result["lexical_score"],
            ),
        )

        # Increment view_count on the matched FAQ
        if result.get("faq_id"):
            execute_query(
                "UPDATE faqs SET view_count = view_count + 1 WHERE id = ?",
                (result["faq_id"],),
            )

        # Log analytics event
        execute_query(
            """
            INSERT INTO system_analytics (event_type, event_data)
            VALUES (?, ?)
            """,
            (
                "query",
                json.dumps(
                    {
                        "session_id": request.session_id,
                        "query": request.query,
                        "match_found": result["match_found"],
                        "confidence": result["confidence"],
                        "category": result["category"],
                    }
                ),
            ),
        )

        return ChatResponse(
            match_found=result["match_found"],
            answer=result["answer"],
            faq_id=result.get("faq_id"),
            question=result["question"],
            category=result["category"],
            confidence=result["confidence"],
            semantic_score=result["semantic_score"],
            lexical_score=result["lexical_score"],
            suggestions=suggestions,
            chat_id=chat_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search engine error: {str(e)}",
        )


@router.get("/suggest", response_model=list[TypeaheadSuggestion])
async def suggest(
    q: str = Query(..., min_length=3, description="Partial query for typeahead"),
) -> list[TypeaheadSuggestion]:
    """Generate typeahead autocomplete suggestions.

    Triggered when the user has typed >= 3 characters in the input bar.
    Returns up to 5 matching FAQ questions for live preview.

    Args:
        q: Partial query string (minimum 3 characters).

    Returns:
        list[TypeaheadSuggestion]: Matching FAQ suggestions.

    Time Complexity: O(N × L) where N=FAQs, L=avg question length
    Space Complexity: O(K) where K=result count (max 5)
    """
    results: list[dict[str, Any]] = search_engine.get_typeahead_suggestions(q)
    return [TypeaheadSuggestion(**r) for r in results]


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
) -> list[dict[str, Any]]:
    """Retrieve chat history for a specific session.

    Returns chronologically ordered conversation records with
    all scoring metadata for telemetry display.

    Args:
        session_id: The session identifier to query.
        limit: Maximum number of records (1–200, default 50).

    Returns:
        list[dict]: Chat history records ordered by creation time.

    Time Complexity: O(H) where H is the history size for this session
    Space Complexity: O(min(H, limit))
    """
    history: list[dict] = execute_query(
        """
        SELECT ch.*, f.question AS matched_question
        FROM chat_history ch
        LEFT JOIN faqs f ON ch.matched_faq_id = f.id
        WHERE ch.session_id = ?
        ORDER BY ch.created_at ASC
        LIMIT ?
        """,
        (session_id, limit),
    )
    return history
