"""
cleanup_and_reingest.py — Database cleanup and fresh data ingestion.

Architecture:
    DatabaseManager  — High-level Neo4j operations (delete, count nodes).
    RestaurantIngester (imported) — Handles the CSV → Neo4j ingestion.

Usage:
    python cleanup_and_reingest.py

Warning:
    Running this script DELETES all Review nodes and their relationships
    before re-ingesting from the CSV. Use only when data integrity is
    in doubt (e.g., after detecting duplicate nodes).
"""

from neo4j import GraphDatabase
from reingest import RestaurantIngester


class DatabaseManager:
    """
    Manages high-level Neo4j database operations.

    Responsibilities:
        - Batch-deleting nodes and relationships
        - Reporting current node counts across all labels
    """

    def __init__(
        self,
        uri: str      = "bolt://localhost:7687",
        user: str     = "neo4j",
        password: str = "12345678",
    ) -> None:
        """
        Connect to Neo4j.

        Args:
            uri:      Neo4j Bolt URI.
            user:     Neo4j username.
            password: Neo4j password.
        """
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    # ── Cleanup Operations ───────────────────────────────────────────────────

    def delete_all_reviews(self, batch_size: int = 1000) -> int:
        """
        Delete all Review nodes and their relationships in batches.

        Batching avoids out-of-memory errors on large datasets.

        Args:
            batch_size: Number of nodes to DETACH DELETE per transaction.

        Returns:
            Total number of Review nodes deleted.
        """
        print("🧹 Deleting all Review nodes and their relationships...")
        total_deleted = 0

        with self._driver.session() as session:
            while True:
                result = session.run("""
                    MATCH (r:Review)
                    WITH r LIMIT $batch
                    DETACH DELETE r
                    RETURN count(r) AS c
                """, batch=batch_size).single()

                deleted_in_batch = result["c"] if result else 0
                total_deleted   += deleted_in_batch

                if deleted_in_batch > 0:
                    print(f"   Deleted {total_deleted:,} Review nodes so far...")

                if deleted_in_batch == 0:
                    break

        print(f"✅ Cleanup complete — {total_deleted:,} Review nodes removed.\n")
        return total_deleted

    def delete_orphan_food_nodes(self) -> int:
        """
        Remove Food nodes that have no remaining Review relationships.

        Returns:
            Number of orphan Food nodes deleted.
        """
        with self._driver.session() as session:
            result = session.run("""
                MATCH (f:Food)
                WHERE NOT (f)<-[:MENTIONS]-()
                  AND NOT (f)<-[:SERVES]-()
                WITH f LIMIT 5000
                DETACH DELETE f
                RETURN count(f) AS c
            """).single()
            count = result["c"] if result else 0
            print(f"🗑️  Removed {count:,} orphan Food nodes.")
            return count

    # ── Reporting ────────────────────────────────────────────────────────────

    def get_node_counts(self) -> dict[str, int]:
        """
        Return the current node count for each major label.

        Returns:
            Dict mapping label name → count.
        """
        labels = ["Review", "Restaurant", "Food", "Sentiment"]
        counts: dict[str, int] = {}

        with self._driver.session() as session:
            for label in labels:
                counts[label] = session.run(
                    f"MATCH (n:{label}) RETURN count(n) AS c"
                ).single()["c"]

        print("\n📊 Current Neo4j Node Counts:")
        for label, count in counts.items():
            print(f"   {label:<15}: {count:,}")
        return counts

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def close(self) -> None:
        """Release the Neo4j driver connection."""
        self._driver.close()


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    URI  = "bolt://localhost:7687"
    USER = "neo4j"
    PASS = "12345678"

    print("=" * 55)
    print("  RestaurantDB — Cleanup & Re-Ingest Pipeline")
    print("=" * 55 + "\n")

    # ── Step 1: Show counts before cleanup ────────────────────
    db = DatabaseManager(URI, USER, PASS)
    print("Before cleanup:")
    db.get_node_counts()
    print()

    # ── Step 2: Delete all Review nodes ───────────────────────
    db.delete_all_reviews()

    # ── Step 3: Remove orphan Food nodes ──────────────────────
    db.delete_orphan_food_nodes()
    db.close()

    # ── Step 4: Fresh ingest ──────────────────────────────────
    print("\n📥 Starting fresh data ingestion...\n")
    ingester = RestaurantIngester()
    ingester.load_csv().run().verify()
    ingester.close()

    print("\n✅ All done. Database is clean and up-to-date.")
