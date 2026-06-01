"""
Hybrid Search Engine combining TF-IDF lexical matching and
Sentence Transformer semantic similarity.

Algorithmic Fusion Formula:
    Final Score = (0.7 × Semantic Score) + (0.3 × TF-IDF Cosine Score)

Fallback Threshold: If Final Score < 0.45, returns a conversational
fallback with the top 3 closest contextual matches.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import numpy as np
from typing import Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.config import get_settings
from backend.nlp.pipeline import preprocess_text, batch_preprocess
from backend.nlp.embeddings import (
    generate_embedding,
    generate_embeddings_batch,
    compute_semantic_similarity,
)


class HybridSearchEngine:
    """Dual-engine search combining lexical TF-IDF and semantic embeddings.

    The engine maintains pre-computed TF-IDF vectors and dense embeddings
    for all FAQs in memory. At query time, it computes both lexical and
    semantic similarity scores and fuses them with configurable weights.

    Attributes:
        settings: Application configuration singleton.
        tfidf_vectorizer: Fitted scikit-learn TF-IDF vectorizer.
        tfidf_matrix: Pre-computed sparse TF-IDF matrix (N × V).
        faq_embeddings: Dense embedding matrix (N × 384).
        faq_ids: List of FAQ database primary keys.
        faq_questions: Original FAQ question strings.
        faq_answers: Original FAQ answer strings.
        faq_categories: Category names for each FAQ.

    Time Complexity: O(1) for construction
    Space Complexity: O(N × V + N × D) when fitted
    """

    def __init__(self) -> None:
        """Initialize the hybrid search engine with empty state.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.settings = get_settings()
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[Any] = None
        self.faq_embeddings: Optional[np.ndarray] = None
        self.faq_ids: list[int] = []
        self.faq_questions: list[str] = []
        self.faq_answers: list[str] = []
        self.faq_categories: list[str] = []
        self._is_fitted: bool = False

    def fit(
        self,
        faq_ids: list[int],
        questions: list[str],
        answers: list[str],
        categories: list[str],
    ) -> None:
        """Fit the search engine on the FAQ corpus.

        Precomputes TF-IDF vectors (lexical) and dense semantic embeddings
        for all FAQ questions, storing them in memory for O(1) lookup
        during search operations.

        The TF-IDF vectorizer uses bigram features and sublinear TF scaling
        for improved lexical discrimination.

        Semantic embeddings combine question + answer text for richer
        contextual representation.

        Args:
            faq_ids: Database IDs for each FAQ.
            questions: Raw FAQ question texts.
            answers: Corresponding FAQ answer texts.
            categories: Category name for each FAQ.

        Time Complexity: O(N × L) where N=FAQ count, L=avg text length
        Space Complexity: O(N × V + N × D) where V=vocab size, D=embed dim
        """
        if not questions:
            print("[SEARCH] No FAQs to index. Engine remains unfitted.")
            return

        self.faq_ids = list(faq_ids)
        self.faq_questions = list(questions)
        self.faq_answers = list(answers)
        self.faq_categories = list(categories)

        # --- Stage 1: Lexical Engine (TF-IDF) ---
        processed_questions: list[str] = batch_preprocess(questions)

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_questions)

        # --- Stage 2: Semantic Engine (Dense Embeddings on CUDA) ---
        combined_texts: list[str] = [
            f"{q} {a}" for q, a in zip(questions, answers)
        ]
        self.faq_embeddings = generate_embeddings_batch(combined_texts)

        self._is_fitted = True
        vocab_size: int = len(self.tfidf_vectorizer.vocabulary_)
        embed_shape: tuple = self.faq_embeddings.shape
        print(f"[SEARCH] Engine fitted on {len(questions)} FAQs.")
        print(f"[SEARCH] TF-IDF vocab size: {vocab_size}")
        print(f"[SEARCH] Embedding matrix shape: {embed_shape}")

    @property
    def is_ready(self) -> bool:
        """Check if the engine has been fitted and is ready for search.

        Returns:
            bool: True if the engine is fitted with FAQ data.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return self._is_fitted

    def search(self, query: str, top_k: int = 5) -> dict[str, Any]:
        """Execute hybrid search with algorithmic score fusion.

        Performs both TF-IDF cosine similarity (lexical) and Sentence
        Transformer similarity (semantic), then fuses scores using:

            Final Score = (0.7 × Semantic) + (0.3 × TF-IDF Cosine)

        If the best final score is below 0.45, returns a graceful
        conversational fallback with the top 3 closest contextual matches.

        Args:
            query: User's natural language query string.
            top_k: Number of top results to consider for ranking.

        Returns:
            dict: Search results containing:
                - match_found (bool): Whether a confident match exists.
                - answer (str): Best FAQ answer or fallback message.
                - faq_id (int|None): Matched FAQ ID or None.
                - question (str): Matched question or echo of user query.
                - category (str): Category of the matched FAQ.
                - confidence (float): Final hybrid fusion score.
                - semantic_score (float): Semantic component score.
                - lexical_score (float): Lexical component score.
                - suggestions (list[dict]): Runner-up FAQ matches.

        Time Complexity: O(N × D + N × V) where N=FAQs, D=embed dim, V=vocab
        Space Complexity: O(N) for score arrays + O(K) for suggestions
        """
        if not self._is_fitted:
            return self._build_fallback_response(query, [])

        # --- Preprocess query for TF-IDF ---
        processed_query: str = preprocess_text(query)

        # --- Lexical Engine: TF-IDF + Cosine Similarity ---
        query_tfidf = self.tfidf_vectorizer.transform([processed_query])
        tfidf_scores: np.ndarray = cosine_similarity(
            query_tfidf, self.tfidf_matrix
        ).flatten()

        # --- Semantic Engine: Dense Embedding Similarity ---
        query_embedding: np.ndarray = generate_embedding(query)
        semantic_scores: np.ndarray = compute_semantic_similarity(
            query_embedding, self.faq_embeddings
        )

        # --- Algorithmic Fusion ---
        # Final Score = (0.7 × Semantic) + (0.3 × TF-IDF Cosine)
        final_scores: np.ndarray = (
            self.settings.semantic_weight * semantic_scores
            + self.settings.lexical_weight * tfidf_scores
        )

        # Rank by descending final score
        ranked_indices: np.ndarray = np.argsort(final_scores)[::-1][:top_k]

        best_idx: int = int(ranked_indices[0])
        best_score: float = float(final_scores[best_idx])
        best_semantic: float = float(semantic_scores[best_idx])
        best_lexical: float = float(tfidf_scores[best_idx])

        # Build runner-up suggestions (positions 2–4)
        suggestions: list[dict[str, Any]] = []
        for idx in ranked_indices[1:4]:
            idx_int: int = int(idx)
            suggestions.append(
                {
                    "faq_id": self.faq_ids[idx_int],
                    "question": self.faq_questions[idx_int],
                    "category": self.faq_categories[idx_int],
                    "confidence": round(float(final_scores[idx_int]), 4),
                    "semantic_score": round(float(semantic_scores[idx_int]), 4),
                    "lexical_score": round(float(tfidf_scores[idx_int]), 4),
                }
            )

        # --- Confidence Threshold Gate ---
        if best_score < self.settings.confidence_threshold:
            return self._build_fallback_response(query, suggestions)

        return {
            "match_found": True,
            "answer": self.faq_answers[best_idx],
            "faq_id": self.faq_ids[best_idx],
            "question": self.faq_questions[best_idx],
            "category": self.faq_categories[best_idx],
            "confidence": round(best_score, 4),
            "semantic_score": round(best_semantic, 4),
            "lexical_score": round(best_lexical, 4),
            "suggestions": suggestions,
        }

    def _build_fallback_response(
        self,
        query: str,
        suggestions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Construct a graceful fallback response for low-confidence queries.

        Generated when the hybrid confidence score falls below the
        configured threshold (default: 0.45). Provides a polite
        conversational message and the closest contextual matches.

        Args:
            query: The original user query that failed to match.
            suggestions: Top contextual matches despite low confidence.

        Returns:
            dict: Structured fallback response with suggestions array.

        Time Complexity: O(1)
        Space Complexity: O(S) where S is the suggestions list size
        """
        return {
            "match_found": False,
            "answer": (
                "I appreciate your question! While I wasn't able to find an exact "
                "match in our knowledge base, here are some related topics that "
                "might help. You can also try rephrasing your question or contact "
                "our support team for personalized assistance."
            ),
            "faq_id": None,
            "question": query,
            "category": "General",
            "confidence": 0.0,
            "semantic_score": 0.0,
            "lexical_score": 0.0,
            "suggestions": suggestions,
        }

    def get_typeahead_suggestions(
        self,
        partial_query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate typeahead suggestions for partial query input.

        Uses lightweight substring matching on FAQ questions for
        low-latency typeahead autocomplete. Triggered when the user
        has typed >= 3 characters.

        Args:
            partial_query: Partial query string (>= 3 chars).
            limit: Maximum number of suggestions to return.

        Returns:
            list[dict]: Matching FAQ questions with IDs and categories.

        Time Complexity: O(N × L) where N=FAQs, L=avg question length
        Space Complexity: O(K) where K=limit
        """
        if len(partial_query) < self.settings.typeahead_min_chars:
            return []

        query_lower: str = partial_query.lower().strip()
        matches: list[dict[str, Any]] = []

        for i, question in enumerate(self.faq_questions):
            if query_lower in question.lower():
                matches.append(
                    {
                        "faq_id": self.faq_ids[i],
                        "question": question,
                        "category": self.faq_categories[i],
                    }
                )
                if len(matches) >= limit:
                    break

        return matches


# ============================================================
# Global singleton instance
# ============================================================
search_engine: HybridSearchEngine = HybridSearchEngine()


def initialize_search_engine() -> None:
    """Initialize the global search engine from the SQLite database.

    Loads all FAQs with their categories and fits both the TF-IDF
    vectorizer and semantic embedding model. This is called once
    at application startup.

    Time Complexity: O(N × L + N × M) where N=FAQs, L=text len, M=model inference
    Space Complexity: O(N × (V + D)) where V=vocab, D=embed dim
    """
    from backend.database import execute_query

    faqs: list[dict] = execute_query(
        """
        SELECT f.id, f.question, f.answer, c.name AS category
        FROM faqs f
        JOIN categories c ON f.category_id = c.id
        ORDER BY f.id
        """
    )

    if not faqs:
        print("[SEARCH] No FAQs found in database. Engine not fitted.")
        return

    search_engine.fit(
        faq_ids=[f["id"] for f in faqs],
        questions=[f["question"] for f in faqs],
        answers=[f["answer"] for f in faqs],
        categories=[f["category"] for f in faqs],
    )
