"""
Pydantic models for strict request/response validation.

Defines all data transfer objects (DTOs) used across the API,
ensuring type safety and automatic validation at the boundary layer.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

from pydantic import BaseModel, Field
from typing import Optional


# ============================================================
# Chat Models
# ============================================================


class ChatRequest(BaseModel):
    """Incoming chat query from the user.

    Attributes:
        query: The natural language question (1–1000 chars).
        session_id: Unique session identifier for conversation tracking.

    Time Complexity: O(1) for validation
    Space Complexity: O(N) where N is query length
    """

    query: str = Field(..., min_length=1, max_length=1000, description="User's question")
    session_id: str = Field(..., min_length=1, description="Session identifier")


class SuggestionItem(BaseModel):
    """A single runner-up FAQ suggestion.

    Attributes:
        faq_id: Database ID of the suggested FAQ.
        question: The FAQ question text.
        category: Category name the FAQ belongs to.
        confidence: Hybrid fusion confidence score.
        semantic_score: Sentence Transformer similarity score.
        lexical_score: TF-IDF cosine similarity score.

    Time Complexity: O(1) for validation
    Space Complexity: O(1)
    """

    faq_id: int
    question: str
    category: str
    confidence: float
    semantic_score: float
    lexical_score: float


class ChatResponse(BaseModel):
    """Structured response from the chatbot engine.

    Contains the best match (or fallback) along with diagnostic scores
    and runner-up suggestions for the telemetry panel.

    Attributes:
        match_found: Whether a confident match was found.
        answer: The FAQ answer or fallback message.
        faq_id: Matched FAQ ID, or None on fallback.
        question: The matched (or echoed) question.
        category: Category of the matched FAQ.
        confidence: Final hybrid fusion score.
        semantic_score: Semantic similarity component.
        lexical_score: TF-IDF cosine component.
        suggestions: Top runner-up FAQ suggestions.
        chat_id: Database ID of the stored chat record.

    Time Complexity: O(1) for validation
    Space Complexity: O(S) where S is suggestions count
    """

    match_found: bool
    answer: str
    faq_id: Optional[int] = None
    question: str
    category: str
    confidence: float
    semantic_score: float
    lexical_score: float
    suggestions: list[SuggestionItem] = []
    chat_id: int = 0


# ============================================================
# FAQ CRUD Models
# ============================================================


class FAQCreate(BaseModel):
    """Request body for creating a new FAQ entry.

    Attributes:
        category_id: FK to the categories table.
        question: The FAQ question (min 5 chars).
        answer: The FAQ answer (min 10 chars).

    Time Complexity: O(1) for validation
    Space Complexity: O(N) where N is text length
    """

    category_id: int = Field(..., gt=0)
    question: str = Field(..., min_length=5, description="FAQ question text")
    answer: str = Field(..., min_length=10, description="FAQ answer text")


class FAQUpdate(BaseModel):
    """Request body for updating an existing FAQ entry.

    All fields are optional; only provided fields are updated.

    Attributes:
        category_id: Optional new category FK.
        question: Optional new question text.
        answer: Optional new answer text.

    Time Complexity: O(1) for validation
    Space Complexity: O(N) where N is text length
    """

    category_id: Optional[int] = Field(None, gt=0)
    question: Optional[str] = Field(None, min_length=5)
    answer: Optional[str] = Field(None, min_length=10)


class FAQResponse(BaseModel):
    """Complete FAQ record returned from the API.

    Attributes:
        id: FAQ primary key.
        category_id: FK to categories.
        category_name: Denormalized category name for display.
        question: FAQ question text.
        answer: FAQ answer text.
        view_count: Number of times this FAQ was matched.
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of last update.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    id: int
    category_id: int
    category_name: str
    question: str
    answer: str
    view_count: int
    created_at: str
    updated_at: str


# ============================================================
# Feedback Models
# ============================================================


class FeedbackRequest(BaseModel):
    """User feedback submission on a chat response.

    Attributes:
        chat_id: FK to the chat_history record.
        is_helpful: Boolean helpfulness indicator.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    chat_id: int = Field(..., gt=0)
    is_helpful: bool


# ============================================================
# Bookmark Models
# ============================================================


class BookmarkRequest(BaseModel):
    """Request to bookmark a FAQ for later reference.

    Attributes:
        session_id: User's session identifier.
        faq_id: FK to the FAQ to bookmark.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    session_id: str = Field(..., min_length=1)
    faq_id: int = Field(..., gt=0)


class BookmarkResponse(BaseModel):
    """A saved bookmark record.

    Attributes:
        id: Bookmark primary key.
        session_id: Associated session.
        faq_id: Bookmarked FAQ ID.
        question: FAQ question text.
        category: FAQ category name.
        created_at: ISO timestamp.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    id: int
    session_id: str
    faq_id: int
    question: str
    category: str
    created_at: str


# ============================================================
# Category Models
# ============================================================


class CategoryResponse(BaseModel):
    """Category with aggregated FAQ count.

    Attributes:
        id: Category primary key.
        name: Category display name.
        icon: Emoji icon for the category.
        faq_count: Number of FAQs in this category.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    id: int
    name: str
    icon: str
    faq_count: int


# ============================================================
# Analytics Models
# ============================================================


class DashboardStats(BaseModel):
    """Aggregated dashboard statistics.

    Attributes:
        total_queries: Total chat queries processed.
        successful_matches: Queries with confidence >= threshold.
        success_rate: Percentage of successful matches.
        total_faqs: Total FAQ entries in the database.
        total_feedback: Total feedback submissions.
        positive_feedback: Count of positive (helpful) feedback.
        avg_confidence: Average confidence score across all queries.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    total_queries: int
    successful_matches: int
    success_rate: float
    total_faqs: int
    total_feedback: int
    positive_feedback: int
    avg_confidence: float


class QueryOverTime(BaseModel):
    """Time-series data point for queries over time.

    Attributes:
        date: ISO date string (YYYY-MM-DD).
        count: Number of queries on that date.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    date: str
    count: int


class CategoryStats(BaseModel):
    """Category-level query statistics for analytics.

    Attributes:
        category: Category name.
        count: Number of queries matched to this category.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    category: str
    count: int


class TypeaheadSuggestion(BaseModel):
    """Typeahead autocomplete suggestion.

    Attributes:
        faq_id: Database ID of the matching FAQ.
        question: Full FAQ question text.
        category: Category name.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    faq_id: int
    question: str
    category: str
