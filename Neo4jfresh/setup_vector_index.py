"""
setup_vector_index.py — Generate embeddings and create Neo4j vector index.

Architecture:
    VectorIndexManager — Encapsulates the two-step process of:
        1. Generating embeddings for all Review nodes that lack one.
        2. Creating (or verifying) the Neo4j vector index 'review_index'.

Usage:
    python setup_vector_index.py

    Safe to re-run — embedding generation skips already-embedded reviews,
    and the index is created with IF NOT EXISTS.
"""

from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class VectorIndexManager:
    """
    Manages the full lifecycle of Neo4j vector search for restaurant reviews.

    Responsibilities:
        - Fetching Review nodes without embeddings
        - Encoding review text with SentenceTransformer
        - Persisting embedding vectors to Neo4j node properties
        - Creating the cosine-similarity vector index

    Index spec:
        Name       : review_index
        Label      : Review
        Property   : embedding
        Dimensions : 384  (all-MiniLM-L6-v2 output dim)
        Similarity : cosine
    """

    INDEX_NAME: str = "review_index"
    DIMENSIONS: int = 384

    def __init__(
        self,
        uri: str        = "bolt://localhost:7687",
        user: str       = "neo4j",
        password: str   = "12345678",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        """
        Initialise the manager.

        Args:
            uri:        Neo4j Bolt URI.
            user:       Neo4j username.
            password:   Neo4j password.
            model_name: SentenceTransformer model to use for encoding.
        """
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._model  = SentenceTransformer(model_name)
        print(f"✅ Loaded embedding model: '{model_name}'")

    # ── Private Helpers ──────────────────────────────────────────────────────

    def _get_reviews_without_embeddings(self) -> list[dict]:
        """
        Fetch all Review nodes that do not yet have an embedding property.

        Returns:
            List of dicts with keys 'id' (review_id) and 'text' (review text).
        """
        with self._driver.session() as session:
            return session.run("""
                MATCH (r:Review)
                WHERE r.embedding IS NULL
                RETURN r.review_id AS id, r.text AS text
            """).data()

    def _write_embedding(self, session, review_id: str, embedding: list[float]) -> None:
        """
        Persist an embedding vector to a Review node.

        Args:
            session:   Active Neo4j session.
            review_id: The review_id property of the target node.
            embedding: 384-dimensional float list.
        """
        session.run(
            "MATCH (r:Review {review_id: $id}) SET r.embedding = $emb",
            id=review_id,
            emb=embedding,
        )

    # ── Public Interface ─────────────────────────────────────────────────────

    def generate_embeddings(self) -> "VectorIndexManager":
        """
        Encode and persist embeddings for all Review nodes missing one.

        Uses tqdm for progress reporting. Safe to re-run — reviews that
        already have an embedding are completely skipped.

        Returns:
            self (fluent interface)
        """
        reviews = self._get_reviews_without_embeddings()

        if not reviews:
            print("✅ All reviews already have embeddings — nothing to do.")
            return self

        print(f"🔢 Generating embeddings for {len(reviews):,} reviews...")

        with self._driver.session() as session:
            for review in tqdm(reviews, desc="Encoding", unit="rev", ncols=80):
                text      = review.get("text") or ""
                embedding = self._model.encode(text).tolist()
                self._write_embedding(session, review["id"], embedding)

        print(f"✅ Embeddings generated for {len(reviews):,} reviews.\n")
        return self

    def create_index(self) -> "VectorIndexManager":
        """
        Create the Neo4j vector index (idempotent).

        Uses IF NOT EXISTS so it is safe to call on an already-indexed database.
        The index enables CALL db.index.vector.queryNodes() in Cypher.

        Returns:
            self (fluent interface)
        """
        print(f"📐 Creating vector index '{self.INDEX_NAME}' ({self.DIMENSIONS}d cosine)...")

        with self._driver.session() as session:
            try:
                session.run(f"""
                    CREATE VECTOR INDEX {self.INDEX_NAME} IF NOT EXISTS
                    FOR (r:Review) ON (r.embedding)
                    OPTIONS {{
                        indexConfig: {{
                            `vector.dimensions`: {self.DIMENSIONS},
                            `vector.similarity_function`: 'cosine'
                        }}
                    }}
                """)
                print(f"✅ Vector index '{self.INDEX_NAME}' created/verified.\n")
            except Exception as exc:
                print(f"⚠️  Index creation error: {exc}")

        return self

    def get_index_status(self) -> dict:
        """
        Return metadata about the vector index if it exists.

        Returns:
            Dict with keys 'name', 'state', 'type', or empty dict if absent.
        """
        with self._driver.session() as session:
            result = session.run("""
                SHOW INDEXES
                WHERE name = $name
            """, name=self.INDEX_NAME).data()
            return result[0] if result else {}

    def run(self) -> "VectorIndexManager":
        """
        Execute the full embedding + index creation pipeline.

        Call order:
            generate_embeddings() → create_index()

        Returns:
            self (fluent interface)
        """
        self.generate_embeddings()
        self.create_index()

        status = self.get_index_status()
        if status:
            print(f"📋 Index status: {status.get('state', 'UNKNOWN')}")
        return self

    def close(self) -> None:
        """Release the Neo4j driver connection."""
        self._driver.close()


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    manager = VectorIndexManager()
    manager.run()
    manager.close()
