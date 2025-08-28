"""
Semantic Analysis Module for WebScraperPortable

Provides semantic analysis capabilities with graceful fallbacks when
Ollama or NumPy are not available.
"""

import hashlib
from typing import Optional, List, Dict, Any

try:
    from .dependencies import (
        ollama,
        np,
        check_semantic_available,
    )
    from .utils import app_logger
except (ImportError, ModuleNotFoundError):
    from .dependencies import (
        ollama,
        np,
        check_semantic_available,
    )
    from .utils import app_logger

DEFAULT_EMBED_MODEL = "mxbai-embed-large"


class SemanticAnalyzer:
    """
    Semantic analyzer with graceful fallbacks for missing dependencies
    """

    def __init__(
        self, ollama_host: Optional[str] = None, embed_model: Optional[str] = None
    ):
        """
        Initialize semantic analyzer

        Args:
            ollama_host: Ollama server host (optional)
            embed_model: Embedding model name (optional)
        """
        self.ollama_host = ollama_host
        self.embed_model = embed_model or DEFAULT_EMBED_MODEL
        self.client = None
        self.embedding_cache = {}
        self.embedding_cache_max_size = 1000
        self.features_available = check_semantic_available()

        if self.features_available:
            self._initialize_ollama_client()
        else:
            app_logger.info(
                "Semantic analysis disabled - continuing with basic web scraping"
            )

    def _initialize_ollama_client(self) -> bool:
        """
        Initialize Ollama client if possible

        Returns:
            True if successful, False otherwise
        """
        if not ollama:
            return False

        try:
            # Determine host
            host_to_use = self.ollama_host or "http://localhost:11434"

            # Handle scheme
            if "://" not in host_to_use:
                host_to_use = f"http://{host_to_use}"

            app_logger.info(f"Initializing Ollama client with host: {host_to_use}")
            self.client = ollama.Client(host=host_to_use)

            # Test connection and model availability
            return self._check_ollama_model()

        except Exception as e:
            app_logger.error(f"Failed to initialize Ollama client: {e}")
            self.client = None
            return False

    def _check_ollama_model(self) -> bool:
        """
        Check if the embedding model is available

        Returns:
            True if model is available, False otherwise
        """
        if not self.client:
            return False

        try:
            models = self.client.list()
            model_names = [m.model for m in models.models]

            # Check if model is available
            if any(self.embed_model in name for name in model_names):
                app_logger.info(f"Ollama model '{self.embed_model}' is available")
                return True
            else:
                app_logger.warning(f"Ollama model '{self.embed_model}' not found")
                app_logger.info(f"Available models: {model_names}")
                app_logger.info(f"Attempting to pull '{self.embed_model}'...")

                # Try to pull the model
                try:
                    for response in self.client.pull(self.embed_model, stream=True):
                        if "status" in response:
                            status = response["status"]
                            if "pulling" in status.lower():
                                print(f"Pulling {self.embed_model}: {status}", end="\r")
                            elif "success" in status.lower():
                                print(f"\n✅ Successfully pulled {self.embed_model}")
                                return True
                        if response.get("error"):
                            app_logger.error(
                                f"Error pulling model: {response['error']}"
                            )
                            return False

                    return True

                except Exception as e:
                    app_logger.error(f"Failed to pull model '{self.embed_model}': {e}")
                    return False

        except Exception as e:
            app_logger.error(f"Error checking Ollama models: {e}")
            self.client = None
            return False

    def is_available(self) -> bool:
        """Check if semantic analysis is available"""
        return self.features_available and self.client is not None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text with caching

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if not available
        """
        if not self.is_available():
            return None

        if not text or not text.strip():
            return None

        # Check cache
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]

        try:
            response = self.client.embeddings(model=self.embed_model, prompt=text)
            embedding = response.get("embedding")

            if embedding:
                # Cache the embedding
                if len(self.embedding_cache) >= self.embedding_cache_max_size:
                    # Remove oldest entry
                    oldest_key = next(iter(self.embedding_cache))
                    del self.embedding_cache[oldest_key]

                self.embedding_cache[text_hash] = embedding
                app_logger.debug(f"Generated embedding for text (length: {len(text)})")
                return embedding
            else:
                app_logger.warning("Failed to get embedding from Ollama")
                return None

        except Exception as e:
            app_logger.error(f"Error getting embedding: {e}")
            return None

    def calculate_similarity(
        self, vec1: Optional[List[float]], vec2: Optional[List[float]]
    ) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0.0 to 1.0) or 0.0 if not available
        """
        if not self.features_available or vec1 is None or vec2 is None:
            return 0.0

        if not np:
            return 0.0

        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            if v1.shape != v2.shape:
                app_logger.warning(
                    f"Vector shapes don't match: {v1.shape} vs {v2.shape}"
                )
                return 0.0

            # Avoid division by zero
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            cosine_sim = np.dot(v1, v2) / (norm1 * norm2)
            return float(cosine_sim)

        except Exception as e:
            app_logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def score_link_relevance(self, page_content: str, link_text: str) -> float:
        """
        Score relevance between page content and link text

        Args:
            page_content: Main page content
            link_text: Link anchor text

        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not self.is_available():
            # Basic fallback - check if link text appears in content
            if link_text.lower() in page_content.lower():
                return 0.7
            return 0.3

        page_embedding = self.get_embedding(page_content[:1000])  # Limit length
        link_embedding = self.get_embedding(link_text)

        return self.calculate_similarity(page_embedding, link_embedding)

    def score_topic_relevance(self, content: str, topic: str) -> float:
        """
        Score relevance between content and topic

        Args:
            content: Content to analyze
            topic: Target topic

        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not self.is_available():
            # Basic fallback - keyword matching
            topic_keywords = topic.lower().split()
            content_lower = content.lower()

            matches = sum(1 for keyword in topic_keywords if keyword in content_lower)
            return min(matches / len(topic_keywords), 1.0) if topic_keywords else 0.0

        content_embedding = self.get_embedding(content[:2000])  # Limit length
        topic_embedding = self.get_embedding(topic)

        return self.calculate_similarity(content_embedding, topic_embedding)

    def filter_by_topic(
        self,
        items: List[Dict[str, Any]],
        topic: str,
        threshold: float = 0.5,
        content_key: str = "content",
    ) -> List[Dict[str, Any]]:
        """
        Filter items by topic relevance

        Args:
            items: List of items with content
            topic: Target topic
            threshold: Minimum relevance score
            content_key: Key in items containing content

        Returns:
            Filtered list of items
        """
        if not topic:
            return items

        filtered_items = []
        for item in items:
            content = item.get(content_key, "")
            if content:
                score = self.score_topic_relevance(content, topic)
                if score >= threshold:
                    item["topic_score"] = score
                    filtered_items.append(item)

        # Sort by relevance score
        filtered_items.sort(key=lambda x: x.get("topic_score", 0), reverse=True)

        app_logger.info(
            f"Topic filtering: {len(filtered_items)}/{len(items)} items passed "
            f"threshold {threshold}"
        )

        return filtered_items

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics"""
        return {
            "cache_size": len(self.embedding_cache),
            "max_size": self.embedding_cache_max_size,
            "features_available": self.features_available,
            "client_available": self.client is not None,
        }


# For backward compatibility and convenience
def create_semantic_analyzer(**kwargs) -> SemanticAnalyzer:
    """Create a semantic analyzer instance"""
    return SemanticAnalyzer(**kwargs)


__all__ = ["SemanticAnalyzer", "create_semantic_analyzer", "DEFAULT_EMBED_MODEL"]
