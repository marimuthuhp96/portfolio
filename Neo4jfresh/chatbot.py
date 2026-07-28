"""
chatbot.py — GraphRAG-powered restaurant recommendation chatbot.

Architecture:
    GraphRAGChatbot — Encapsulates Neo4j graph retrieval, vector search,
                      Gemini LLM inference, and conversation memory.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer


class GraphRAGChatbot:
    """
    GraphRAG chatbot that combines:
    - Graph-based retrieval (best/worst/food keyword routing)
    - Vector similarity search over review embeddings
    - Gemini LLM for natural language generation
    - Conversation memory (last 6 turns)
    """

    # Food keywords used for intent routing
    FOOD_KEYWORDS: list[str] = [
        "biryani", "pizza", "paneer", "burger", "noodles",
        "coffee", "cake", "snacks", "breakfast", "dinner",
        "veg", "non veg", "dessert", "shawarma", "parotta",
    ]

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "12345678",
    ) -> None:
        """
        Initialise the chatbot.

        Loads GOOGLE_API_KEY from .env, connects to Neo4j,
        and loads the sentence-transformer embedding model.

        Args:
            uri:      Neo4j Bolt URI.
            username: Neo4j username.
            password: Neo4j password.
        """
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        self._llm     = genai.GenerativeModel("gemini-flash-latest")
        self._driver  = GraphDatabase.driver(uri, auth=(username, password))
        self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self._memory: list[str] = []

    # ── Embedding ────────────────────────────────────────────────────────────

    def get_embedding(self, text: str) -> list[float]:
        """Encode *text* into a 384-dimensional vector."""
        return self._encoder.encode(text).tolist()

    # ── Graph Retrieval ──────────────────────────────────────────────────────

    def get_best_restaurants(self) -> list[str]:
        """Return the top-5 restaurants ranked by positive sentiment count."""
        with self._driver.session() as session:
            result = session.run("""
                MATCH (r:Restaurant)<-[:FOR]-(rev)
                OPTIONAL MATCH (rev)-[:HAS_SENTIMENT]->(s:Sentiment)
                WITH r,
                     count(CASE WHEN s.type='Positive' THEN 1 END) AS positive,
                     count(rev) AS total
                RETURN r.name AS name
                ORDER BY positive DESC, total DESC
                LIMIT 5
            """)
            return [record["name"] for record in result]

    def get_worst_restaurants(self) -> list[str]:
        """Return the top-5 restaurants ranked by negative sentiment count."""
        with self._driver.session() as session:
            result = session.run("""
                MATCH (r:Restaurant)<-[:FOR]-(rev)
                OPTIONAL MATCH (rev)-[:HAS_SENTIMENT]->(s:Sentiment)
                WITH r,
                     count(CASE WHEN s.type='Negative' THEN 1 END) AS negative
                RETURN r.name AS name, negative
                ORDER BY negative DESC
                LIMIT 5
            """)
            return [r["name"] for r in result if r["negative"] > 0]

    def get_food_restaurants(self, food: str) -> list[str]:
        """Return restaurants that serve a specific *food* item."""
        with self._driver.session() as session:
            result = session.run("""
                MATCH (r:Restaurant)-[:SERVES]->(f:Food)
                WHERE toLower(f.name) CONTAINS toLower($food)
                RETURN DISTINCT r.name AS name
                LIMIT 5
            """, food=food)
            return [r["name"] for r in result]

    def retrieve_from_graph(self, question: str) -> list[tuple[str, str, float]]:
        """
        Perform vector similarity search over review embeddings.

        Returns:
            List of (restaurant_name, review_text, score) tuples.
        """
        embedding = self.get_embedding(question)
        with self._driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('review_index', 5, $emb)
                YIELD node, score
                MATCH (node)-[:FOR]->(r:Restaurant)
                RETURN r.name AS restaurant,
                       node.text AS review,
                       score
                ORDER BY score DESC
            """, emb=embedding)
            return [(r["restaurant"], r["review"], r["score"]) for r in result]

    # ── Context Building ─────────────────────────────────────────────────────

    def _build_context(self, question: str) -> str:
        """
        Route the question through keyword and vector retrieval
        to build a context string for the LLM prompt.

        Routing priority:
            1. Food keyword → get_food_restaurants()
            2. Best/recommend intent → get_best_restaurants()
            3. Worst/bad intent → get_worst_restaurants()
            4. Fallback → retrieve_from_graph() (vector search)
        """
        q = question.lower()

        # 1. Food-based routing
        for food in self.FOOD_KEYWORDS:
            if food in q:
                restaurants = self.get_food_restaurants(food)
                if restaurants:
                    return f"Restaurants known for {food}: " + ", ".join(restaurants)
                break

        # 2. Sentiment-based routing
        if any(kw in q for kw in ["best restaurant", "top restaurant", "recommend"]):
            best = self.get_best_restaurants()
            if best:
                return "Top-rated restaurants: " + ", ".join(best)

        elif any(kw in q for kw in ["worst", "bad restaurant", "negative"]):
            worst = self.get_worst_restaurants()
            if worst:
                return "Restaurants with poor feedback: " + ", ".join(worst)

        # 3. Vector search fallback
        results = self.retrieve_from_graph(question)
        if not results:
            return ""

        context, seen = "", set()
        for restaurant, review, _ in results:
            if restaurant not in seen:
                context += f"{restaurant}: {review}\n"
                seen.add(restaurant)
        return context

    # ── LLM Inference ────────────────────────────────────────────────────────

    def chat(self, question: str) -> str:
        """
        Main entry point — answer a user question.

        Builds context from Neo4j, appends conversation history,
        calls Gemini, and updates memory.

        Args:
            question: User's natural language query.

        Returns:
            LLM-generated response string.
        """
        try:
            context = self._build_context(question)
            if not context:
                return "I couldn't find any relevant restaurant data for that query."

            memory_block = "\n".join(self._memory[-6:])

            prompt = f"""You are an expert GraphRAG AI Restaurant Assistant. 
Your goal is to provide accurate, data-driven recommendations based ONLY on the verified data provided.

### CONTEXT DATA
---
**Conversation History:**
{memory_block}

**Verified Restaurant Knowledge (from Neo4j):**
{context}
---

**User Query:** {question}

### RESPONSE INSTRUCTIONS:
4. **Professional Vertical UI**: 
    - You MUST use **actual line breaks** after every field. Do not group them.
    - Use this EXACT structure for every restaurant:
      
      ---
      **[Restaurant Name]**
      - **Focus**: [1-3 words]
      - **Action**: [Short 5 words]
      - **Reason**: [Short 5 words]
      ---
      
    - Use **double new lines** (\n\n) between different restaurants.
5. **No Paragraphs**: Zero paragraphs allowed in the body. Only lists and headers.
6. **Integrity**: If no data is found, briefly state you lack verified info and suggest the closest match.
"""
            response = self._llm.generate_content(prompt)
            answer   = response.text

            # Persist to conversation memory
            self._memory.append(f"User: {question}")
            self._memory.append(f"Bot: {answer}")

            return answer

        except Exception as exc:
            return f"⚠️ AI Error: {exc}"

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def close(self) -> None:
        """Release the Neo4j driver connection."""
        self._driver.close()


# ── Standalone test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot = GraphRAGChatbot()
    print(bot.chat("What are the best restaurants?"))
    bot.close()