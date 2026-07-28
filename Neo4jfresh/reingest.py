"""
reingest.py — Production restaurant data ingestion pipeline.

Architecture:
    RestaurantIngester — Loads, cleans, and ingests the CSV dataset
                         into the Neo4j Knowledge Graph using MERGE
                         with stable MD5-based review IDs.

Usage:
    python reingest.py

Design decisions:
    - MD5 hash of (restaurant + reviewer + review[:100]) ensures
      the same review is never duplicated across multiple runs.
    - Private methods prefixed with _ are internal helpers.
    - Fluent interface: load_csv().run().verify() all return self.
"""

import hashlib
import re
from datetime import datetime

import pandas as pd
from neo4j import GraphDatabase


class RestaurantIngester:
    """
    Ingests restaurant reviews from CSV into a Neo4j Knowledge Graph.

    Node types created:
        Restaurant, Review, Sentiment, Food

    Relationships created:
        (Review)-[:FOR]->(Restaurant)
        (Review)-[:HAS_SENTIMENT]->(Sentiment)
        (Review)-[:MENTIONS]->(Food)
        (Restaurant)-[:SERVES]->(Food)
    """

    # ── Configuration ────────────────────────────────────────────────────────

    NEO4J_URI:  str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASS: str = "12345678"
    BATCH_SIZE: int = 500

    FOOD_ITEMS: list[str] = [
        "chicken biryani", "butter chicken", "chicken curry", "chicken tikka",
        "tandoori chicken", "fried chicken", "chicken 65", "chicken kebab",
        "chicken wings", "chicken burger", "chicken shawarma", "chicken fried rice",
        "chicken noodles", "chilli chicken", "dragon chicken",
        "mutton biryani", "mutton curry", "mutton haleem", "mutton kebab",
        "mutton soup", "mutton thali",
        "fried rice", "jeera rice", "veg pulao", "egg biryani", "veg biryani",
        "paneer biryani", "hakka noodles", "schezwan noodles",
        "veg noodles", "egg noodles",
        "ice cream", "gulab jamun", "brownie", "chocolate cake", "lassi",
        "crispy corn", "spring roll", "manchurian", "french fries", "potato wedges",
        "paneer butter masala", "dal makhani", "veg thali", "chole", "mix veg",
        "fish fry", "fish curry", "apollo fish", "prawn curry", "fish tikka",
        "pizza", "burger", "shawarma", "kebab", "soup", "naan", "roti", "paratha",
    ]

    FOOD_CATEGORY_MAP: dict[str, str] = {
        "chicken":    "Chicken Items",
        "mutton":     "Mutton Items",
        "biryani":    "Chicken Items",
        "fried rice": "Fried Rice",
        "noodles":    "Noodles",
        "pasta":      "Noodles",
        "dessert":    "Desserts",
        "ice cream":  "Desserts",
        "cake":       "Desserts",
        "snack":      "Chats & Snacks",
        "fries":      "Chats & Snacks",
        "corn":       "Chats & Snacks",
        "meal":       "Meals",
        "thali":      "Meals",
        "paneer":     "Meals",
        "dal":        "Meals",
    }

    # ── Initialisation ───────────────────────────────────────────────────────

    def __init__(self, csv_path: str = "Restaurant_Reviews.csv") -> None:
        """
        Initialise the ingester.

        Args:
            csv_path: Path to the restaurant reviews CSV file.
        """
        self._csv_path = csv_path
        self._driver   = GraphDatabase.driver(
            self.NEO4J_URI, auth=(self.NEO4J_USER, self.NEO4J_PASS)
        )
        self._df: pd.DataFrame | None = None

    # ── Private Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _get_sentiment(rating) -> str:
        """
        Convert a numeric rating to a sentiment label.

        Returns:
            'Positive' (≥4), 'Neutral' (3), or 'Negative' (<3).
        """
        try:
            r = float(rating)
            if r >= 4: return "Positive"
            if r == 3: return "Neutral"
            return "Negative"
        except (ValueError, TypeError):
            return "Neutral"

    def _extract_food_items(self, text: str) -> list[str]:
        """
        Extract all known food items from review text via regex.

        Args:
            text: Raw review string.

        Returns:
            Deduplicated list of matched food item names.
        """
        if not isinstance(text, str):
            return []
        lowered = text.lower()
        return list({
            food for food in self.FOOD_ITEMS
            if re.search(r'\b' + re.escape(food) + r'\b', lowered)
        })

    def _get_food_category(self, food_name: str) -> str:
        """
        Map a food item name to its business category.

        Args:
            food_name: Name of the food item.

        Returns:
            Category string or 'Other'.
        """
        lowered = food_name.lower()
        for keyword, category in self.FOOD_CATEGORY_MAP.items():
            if keyword in lowered:
                return category
        return "Other"

    @staticmethod
    def _parse_datetime(time_val) -> tuple[str, str]:
        """
        Parse a raw CSV timestamp into (ISO date, HH:MM time).

        Handles formats like '5/25/2019 15:54' and '3:54 PM'.

        Returns:
            Tuple of (date_str, time_str); 'Unknown' if unparseable.
        """
        if not isinstance(time_val, str) or not time_val.strip():
            return "Unknown", "Unknown"

        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', time_val)
        time_match = re.search(
            r'(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM)?)', time_val, re.IGNORECASE
        )

        found_date, found_time = "Unknown", "Unknown"

        if date_match:
            try:
                found_date = datetime.strptime(
                    date_match.group(1), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            except ValueError:
                pass

        if time_match:
            found_time = time_match.group(1).strip()
            if "AM" in found_time.upper() or "PM" in found_time.upper():
                try:
                    found_time = datetime.strptime(
                        found_time.upper(), "%I:%M %p"
                    ).strftime("%H:%M")
                except ValueError:
                    pass

        return found_date, found_time

    @staticmethod
    def _make_review_id(restaurant: str, reviewer: str, review_text: str) -> str:
        """
        Generate a stable, content-based MD5 review ID.

        Using restaurant + reviewer + first 100 chars of the review
        ensures the same physical review always receives the same ID,
        preventing duplicate nodes across multiple ingest runs.

        Args:
            restaurant:  Restaurant name.
            reviewer:    Reviewer display name.
            review_text: Full review text.

        Returns:
            32-character hexadecimal MD5 string.
        """
        raw = f"{restaurant}::{reviewer}::{review_text[:100]}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _build_record(self, idx: int, row: pd.Series) -> dict:
        """Build a single ingest record dict from a CSV row."""
        review_text = str(row["Review"])
        reviewer    = str(row.get("Reviewer", "Anonymous"))
        restaurant  = str(row["Restaurant"]).strip()
        date, time  = self._parse_datetime(str(row.get("Time", "")))

        return {
            "review_id":  self._make_review_id(restaurant, reviewer, review_text),
            "restaurant": restaurant,
            "reviewer":   reviewer,
            "review":     review_text[:2000],
            "rating":     float(row["Rating"]),
            "sentiment":  self._get_sentiment(row["Rating"]),
            "date":       date,
            "time":       time,
            "foods":      self._extract_food_items(review_text),
        }

    def _ingest_batch(self, session, batch: list[dict]) -> None:
        """
        Write a batch of review records to Neo4j via Cypher MERGE.

        Args:
            session: Active Neo4j session.
            batch:   List of record dicts (max BATCH_SIZE entries).
        """
        # Core: Restaurant, Review, Sentiment nodes
        session.run("""
            UNWIND $rows AS row
            MERGE (res:Restaurant {name: row.restaurant})
            MERGE (rev:Review {review_id: row.review_id})
            SET   rev.text    = row.review,
                  rev.rating  = row.rating,
                  rev.date    = row.date,
                  rev.time    = row.time
            MERGE (rev)-[:FOR]->(res)
            MERGE (s:Sentiment {type: row.sentiment})
            MERGE (rev)-[:HAS_SENTIMENT]->(s)
        """, rows=batch)

        # Food nodes (only for reviews that mention food)
        food_rows = [r for r in batch if r["foods"]]
        if food_rows:
            session.run("""
                UNWIND $rows AS row
                MATCH (rev:Review {review_id: row.review_id})
                UNWIND row.foods AS food_name
                MERGE (f:Food {name: food_name})
                ON CREATE SET f.category = row.food_cat
                MERGE (rev)-[:MENTIONS]->(f)
                MERGE (res:Restaurant {name: row.restaurant})
                MERGE (res)-[:SERVES]->(f)
            """, rows=[
                {**r, "food_cat": self._get_food_category(r["foods"][0])}
                for r in food_rows
            ])

    # ── Public Interface ─────────────────────────────────────────────────────

    def load_csv(self) -> "RestaurantIngester":
        """
        Load and clean the CSV dataset into self._df.

        Cleaning steps:
            - Drop the spurious '7514' column if present
            - Drop rows with null Review or Rating
            - Fill Reviewer/Metadata/Time nulls with defaults
            - Cast Rating to float

        Returns:
            self (fluent interface)
        """
        df = pd.read_csv(self._csv_path)
        df = df.drop(columns=["7514"], errors="ignore")
        df = df.dropna(subset=["Review", "Rating"])
        df["Reviewer"] = df["Reviewer"].fillna("Anonymous")
        df["Metadata"] = df["Metadata"].fillna("")
        df["Time"]     = df["Time"].fillna("Unknown")
        df["Rating"]   = pd.to_numeric(df["Rating"], errors="coerce")
        df = df.dropna(subset=["Rating"])

        self._df = df
        print(f"📦 Loaded {len(df):,} reviews from '{self._csv_path}'.")
        return self

    def run(self) -> "RestaurantIngester":
        """
        Execute the full ingestion pipeline.

        Auto-loads the CSV if load_csv() was not called first.

        Returns:
            self (fluent interface)
        """
        if self._df is None:
            self.load_csv()

        total = 0
        with self._driver.session() as session:
            batch: list[dict] = []
            for idx, row in self._df.iterrows():
                batch.append(self._build_record(idx, row))

                if len(batch) >= self.BATCH_SIZE:
                    self._ingest_batch(session, batch)
                    total += len(batch)
                    print(f"  ✅ Ingested {total:,} / {len(self._df):,} reviews...")
                    batch.clear()

            if batch:
                self._ingest_batch(session, batch)
                total += len(batch)
                print(f"  ✅ Ingested {total:,} / {len(self._df):,} reviews...")

        print(f"\n🎉 Ingestion complete — {total:,} records processed.")
        return self

    def verify(self) -> dict[str, int]:
        """
        Query and print current node counts for all major labels.

        Returns:
            Dict mapping label names to node counts.
        """
        labels = ["Review", "Restaurant", "Food", "Sentiment"]
        counts: dict[str, int] = {}

        with self._driver.session() as session:
            for label in labels:
                counts[label] = session.run(
                    f"MATCH (n:{label}) RETURN count(n) AS c"
                ).single()["c"]

        print("\n📊 Neo4j Node Counts:")
        for label, count in counts.items():
            print(f"   {label:<15}: {count:,}")
        return counts

    def close(self) -> None:
        """Release the Neo4j driver connection."""
        self._driver.close()


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ingester = RestaurantIngester()
    ingester.load_csv().run().verify()
    ingester.close()
