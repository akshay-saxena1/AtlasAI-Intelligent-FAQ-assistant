"""
NLP Preprocessing Pipeline using SpaCy.

Implements vectorized tokenization, strict lowercasing, punctuation
stripping, stopword excision, and context-aware lemmatization using
the en_core_web_sm model.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import spacy
from typing import Optional
from functools import lru_cache

from backend.config import get_settings


@lru_cache(maxsize=1)
def load_spacy_model() -> spacy.language.Language:
    """Load and cache the SpaCy language model singleton.

    Disables NER and parser components for faster tokenization-only
    processing. Auto-downloads the model if not found locally.

    Returns:
        spacy.language.Language: The loaded SpaCy NLP model.

    Time Complexity: O(M) where M is the model size (one-time load)
    Space Complexity: O(M) for the model in memory
    """
    settings = get_settings()
    model_name: str = settings.spacy_model
    try:
        nlp: spacy.language.Language = spacy.load(
            model_name, disable=["ner", "parser"]
        )
        print(f"[NLP] SpaCy model '{model_name}' loaded successfully.")
        return nlp
    except OSError:
        print(f"[NLP] Model '{model_name}' not found. Downloading...")
        spacy.cli.download(model_name)
        nlp = spacy.load(model_name, disable=["ner", "parser"])
        print(f"[NLP] SpaCy model '{model_name}' downloaded and loaded.")
        return nlp


def preprocess_text(text: str) -> str:
    """Execute the full NLP preprocessing pipeline on input text.

    Pipeline stages (executed sequentially):
        1. Vectorized Tokenization via SpaCy doc processing
        2. Strict Lowercasing (token.lower_)
        3. Punctuation Stripping (not token.is_punct)
        4. Stopword Excision (not token.is_stop)
        5. Context-Aware Lemmatization (token.lemma_)

    Args:
        text: Raw input text string to preprocess.

    Returns:
        str: Cleaned, lemmatized text with stopwords and punctuation removed.

    Time Complexity: O(N) where N is the number of tokens in the text
    Space Complexity: O(N) for the processed token list

    Example:
        >>> preprocess_text("What are the shipping policies?")
        "shipping policy"
        >>> preprocess_text("How do I reset my password?")
        "reset password"
    """
    if not text or not text.strip():
        return ""

    nlp: spacy.language.Language = load_spacy_model()
    doc: spacy.tokens.Doc = nlp(text.lower().strip())

    processed_tokens: list[str] = [
        token.lemma_
        for token in doc
        if (
            not token.is_stop
            and not token.is_punct
            and not token.is_space
            and len(token.lemma_) > 1
        )
    ]

    return " ".join(processed_tokens)


def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    """Extract the most salient keywords from text using POS tagging.

    Prioritizes nouns, proper nouns, and adjectives as they carry
    the highest semantic weight for FAQ matching.

    Args:
        text: Input text to extract keywords from.
        top_n: Maximum number of keywords to return.

    Returns:
        list[str]: Top-N keywords ordered by occurrence, deduplicated.

    Time Complexity: O(N) where N is the number of tokens
    Space Complexity: O(K) where K is top_n
    """
    if not text or not text.strip():
        return []

    nlp: spacy.language.Language = load_spacy_model()
    doc: spacy.tokens.Doc = nlp(text.lower().strip())

    priority_pos: set[str] = {"NOUN", "PROPN", "ADJ"}
    keywords: list[str] = []

    for token in doc:
        if (
            token.pos_ in priority_pos
            and not token.is_stop
            and not token.is_punct
            and len(token.lemma_) > 1
            and token.lemma_ not in keywords
        ):
            keywords.append(token.lemma_)

    return keywords[:top_n]


def batch_preprocess(texts: list[str]) -> list[str]:
    """Batch preprocess multiple texts using SpaCy's pipe for efficiency.

    Leverages SpaCy's internal batching (nlp.pipe) for vectorized
    processing across multiple documents simultaneously, avoiding
    per-document model overhead.

    Args:
        texts: List of raw text strings to preprocess.

    Returns:
        list[str]: List of preprocessed text strings.

    Time Complexity: O(N * L) where N is number of texts, L is avg token count
    Space Complexity: O(N * L) for all processed outputs
    """
    if not texts:
        return []

    nlp: spacy.language.Language = load_spacy_model()
    lowered: list[str] = [t.lower().strip() for t in texts]

    results: list[str] = []
    for doc in nlp.pipe(lowered, batch_size=64):
        tokens: list[str] = [
            token.lemma_
            for token in doc
            if (
                not token.is_stop
                and not token.is_punct
                and not token.is_space
                and len(token.lemma_) > 1
            )
        ]
        results.append(" ".join(tokens))

    return results
