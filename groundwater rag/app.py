import pandas as pd
from pymongo import MongoClient
from google import genai
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np
import difflib

def fuzzy_match_district(query, df):
    """Return best matching district name from query"""
    districts = df['district'].astype(str).str.lower().unique()
    query_lower = query.lower()
    match = difflib.get_close_matches(query_lower, districts, n=1, cutoff=0.6)
    return match[0] if match else None


def convert_numpy(obj):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, (np.int64, np.int32, np.float64, np.float32)):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    else:
        return obj


# ======================================================
# 💾 RAG Components
# ======================================================
class GroundwaterRAG:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.document_chunks = []
        self.chunk_embeddings = None
        
        # Print available columns for debugging
        print(f"📋 Available columns: {list(df.columns)}")
        print(f"📊 Data shape: {df.shape}")
        print(f"👀 First row sample:\n{df.head(1).to_dict('records')}")
        
        self._create_document_chunks()
        
    def _create_document_chunks(self):
        """Enhanced chunking with cluster-aware strategies"""
        print("🔨 Creating document chunks for RAG...")
        
        # Detect column names
        col_mapping = {}
        for search_term in ['district', 'year', 'rainfall', 'groundwater', 'recharge', 
                            'usage', 'allocation', 'cluster']:
            for col in self.df.columns:
                if search_term.lower() in col.lower():
                    col_mapping[search_term] = col
                    break
        
        print(f"🗺️ Column mapping: {col_mapping}")
        
        district_col = col_mapping.get('district')
        year_col = col_mapping.get('year')
        cluster_col = col_mapping.get('cluster')
        rainfall_col = col_mapping.get('rainfall')
        
        if not district_col or not year_col:
            print("⚠️ Could not find District or Year columns!")
            # Fallback to simple chunks
            for idx, row in self.df.iterrows():
                chunk_text = " ".join([f"{k}: {v}" for k, v in row.items() if pd.notna(v)])
                self.document_chunks.append({
                    'text': chunk_text,
                    'metadata': {'index': idx, 'type': 'full_row'}
                })
        else:
            # Strategy 1: District-Year summaries (enhanced with cluster)
            for district in self.df[district_col].dropna().unique():
                district_data = self.df[self.df[district_col] == district]
                for year in district_data[year_col].dropna().unique():
                    year_data = district_data[district_data[year_col] == year]
                    
                    # Get cluster info if available
                    cluster_info = ""
                    if cluster_col and not year_data[cluster_col].isna().all():
                        cluster = year_data[cluster_col].values[0]
                        cluster_info = f"Cluster: {cluster}. "
                    
                    chunk_text = f"District: {district}, Year: {year}. {cluster_info}"
                    
                    for col in year_data.columns:
                        if col not in [district_col, year_col, cluster_col] and pd.api.types.is_numeric_dtype(year_data[col]):
                            try:
                                value = year_data[col].values[0]
                                if pd.notna(value):
                                    chunk_text += f"{col}: {value}. "
                            except:
                                pass
                    
                    self.document_chunks.append({
                        'text': chunk_text,
                        'metadata': {
                            'district': district, 
                            'year': year, 
                            'cluster': year_data[cluster_col].values[0] if cluster_col else None,
                            'type': 'district_year_summary'
                        }
                    })
            
            # Strategy 2: Cluster-Year aggregations (NEW)
            if cluster_col and rainfall_col:
                for year in self.df[year_col].dropna().unique():
                    year_data = self.df[self.df[year_col] == year]
                    
                    # Group by cluster and aggregate
                    cluster_stats = year_data.groupby(cluster_col).agg({
                        rainfall_col: ['mean', 'max', 'min', 'sum'],
                        district_col: 'count'
                    }).round(2)
                    
                    for cluster in cluster_stats.index:
                        stats = cluster_stats.loc[cluster]
                        chunk_text = (
                            f"Year {year}, Cluster {cluster} statistics: "
                            f"Average rainfall: {stats[(rainfall_col, 'mean')]}mm, "
                            f"Highest rainfall: {stats[(rainfall_col, 'max')]}mm, "
                            f"Lowest rainfall: {stats[(rainfall_col, 'min')]}mm, "
                            f"Total rainfall: {stats[(rainfall_col, 'sum')]}mm, "
                            f"Number of districts: {stats[(district_col, 'count')]}. "
                        )
                        
                        # Add top districts in this cluster
                        cluster_districts = year_data[year_data[cluster_col] == cluster].nlargest(3, rainfall_col)
                        if not cluster_districts.empty:
                            top_districts = ", ".join([
                                f"{row[district_col]} ({row[rainfall_col]}mm)" 
                                for _, row in cluster_districts.iterrows()
                            ])
                            chunk_text += f"Top districts: {top_districts}. "
                        
                        self.document_chunks.append({
                            'text': chunk_text,
                            'metadata': {'cluster': cluster, 'year': year, 'type': 'cluster_year_summary'}
                        })
            
            # Strategy 3: Cluster rankings by year (NEW)
            if cluster_col and rainfall_col:
                for year in self.df[year_col].dropna().unique():
                    year_data = self.df[self.df[year_col] == year]
                    cluster_totals = year_data.groupby(cluster_col)[rainfall_col].sum().sort_values(ascending=False)
                    
                    ranking_text = f"Year {year} - Clusters ranked by total rainfall: "
                    for i, (cluster, total) in enumerate(cluster_totals.items(), 1):
                        ranking_text += f"{i}. Cluster {cluster} ({total:.2f}mm), "
                    
                    self.document_chunks.append({
                        'text': ranking_text,
                        'metadata': {'year': year, 'type': 'cluster_rainfall_ranking'}
                    })
            
            # Strategy 4: Rainfall rankings (enhanced)
            if rainfall_col:
                for year in self.df[year_col].dropna().unique():
                    year_data = self.df[self.df[year_col] == year].copy()
                    year_data_sorted = year_data.sort_values(rainfall_col, ascending=False)
                    
                    top_5 = year_data_sorted.head(5)
                    ranking_text = f"Year {year} - Top 5 districts by rainfall: "
                    for _, row in top_5.iterrows():
                        cluster_info = f" (Cluster {row[cluster_col]})" if cluster_col else ""
                        ranking_text += f"{row[district_col]} ({row[rainfall_col]}mm){cluster_info}, "
                    
                    self.document_chunks.append({
                        'text': ranking_text,
                        'metadata': {'year': year, 'type': 'rainfall_ranking'}
                    })
            
            # Strategy 5: Year-level aggregations (NEW - for "which year had highest X")
            for year in self.df[year_col].dropna().unique():
                year_data = self.df[self.df[year_col] == year]
                year_text = f"Year {year} - Overall statistics across all districts: "
                
                for col in year_data.columns:
                    if col not in [district_col, year_col, cluster_col] and pd.api.types.is_numeric_dtype(year_data[col]):
                        try:
                            total_val = year_data[col].sum()
                            avg_val = year_data[col].mean()
                            max_val = year_data[col].max()
                            year_text += f"{col} Total: {total_val:.2f}, Avg: {avg_val:.2f}, Max: {max_val:.2f}. "
                        except:
                            pass
                
                self.document_chunks.append({
                    'text': year_text,
                    'metadata': {'year': year, 'type': 'year_aggregation'}
                })
            
            # Strategy 6: District statistics
            for district in self.df[district_col].dropna().unique():
                district_data = self.df[self.df[district_col] == district]
                stats_text = f"District {district} - Overall statistics: "
                
                for col in district_data.columns:
                    if col not in [district_col, year_col] and pd.api.types.is_numeric_dtype(district_data[col]):
                        try:
                            avg_val = district_data[col].mean()
                            max_val = district_data[col].max()
                            min_val = district_data[col].min()
                            stats_text += f"{col} - Avg: {avg_val:.2f}, Max: {max_val:.2f}, Min: {min_val:.2f}. "
                        except:
                            pass
                
                self.document_chunks.append({
                    'text': stats_text,
                    'metadata': {'district': district, 'type': 'district_statistics'}
                })
        
        print(f"✅ Created {len(self.document_chunks)} document chunks")
        
        # Create embeddings
        if len(self.document_chunks) > 0:
            chunk_texts = [chunk['text'] for chunk in self.document_chunks]
            self.chunk_embeddings = self.embedding_model.encode(chunk_texts)
            print("✅ Generated embeddings for all chunks")
        else:
            print("⚠️ No chunks created!")

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5):
        """Enhanced retrieval with query-aware boosting"""
        if self.chunk_embeddings is None or len(self.document_chunks) == 0:
            return []
        
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.chunk_embeddings)[0]
        
        # Query analysis for boosting
        query_lower = query.lower()
        contains_cluster = 'cluster' in query_lower
        contains_year = any(str(y) in query_lower for y in range(2015, 2030))
        
        # Apply boosting based on query intent
        boosted_similarities = similarities.copy()
        for idx, chunk in enumerate(self.document_chunks):
            metadata = chunk.get('metadata', {})
            chunk_type = metadata.get('type', '')
            
            # Boost cluster-related chunks for cluster queries
            if contains_cluster and 'cluster' in chunk_type:
                boosted_similarities[idx] *= 1.3
            
            # Boost district-year chunks when specific district and year mentioned
            if chunk_type == 'district_year_summary':
                chunk_district = metadata.get('district', '').lower()
                chunk_year = str(metadata.get('year', ''))
                if chunk_district in query_lower and chunk_year in query_lower:
                    boosted_similarities[idx] *= 1.5
            
            # Boost year aggregation chunks for "which year" queries
            if any(phrase in query_lower for phrase in ['which year', 'what year', 'எந்த ஆண்டு']):
                if chunk_type == 'year_aggregation':
                    boosted_similarities[idx] *= 1.4
            
            # Boost ranking chunks for comparative queries
            if any(word in query_lower for word in ['highest', 'lowest', 'top', 'compare', 'rank', 'best', 'worst']):
                if 'ranking' in chunk_type or chunk_type == 'year_aggregation':
                    boosted_similarities[idx] *= 1.2
        
        top_indices = np.argsort(boosted_similarities)[-top_k:][::-1]
        
        relevant_chunks = []
        for idx in top_indices:
            relevant_chunks.append({
                'text': self.document_chunks[idx]['text'],
                'metadata': self.document_chunks[idx]['metadata'],
                'similarity': float(similarities[idx]),
                'boosted_score': float(boosted_similarities[idx])
            })
        
        return relevant_chunks


# ======================================================
# 🔑 Initialize Components
# ======================================================
def initialize_rag_system():
    """Initialize MongoDB connection and RAG system"""
    try:
        client_mongo = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        # Test connection
        client_mongo.server_info()
        
        db = client_mongo["groundwaterDB"]
        collection = db["rainfallData"]

        data = list(collection.find({}, {"_id": 0}))
        
        if not data:
            print("⚠️ Warning: No data found in MongoDB!")
            # Create sample data for testing
            df = pd.DataFrame({
                'District': ['Chennai', 'Coimbatore', 'Madurai'],
                'Year': [2024, 2024, 2024],
                'Rainfall': [1200, 800, 950]
            })
            print("📝 Using sample data for testing")
        else:
            df = pd.DataFrame(data)
            print(f"✅ Loaded {len(df)} rows from MongoDB!")

        rag_system = GroundwaterRAG(df)
        return rag_system, df
        
    except Exception as e:
        print(f"⚠️ MongoDB connection error: {e}")
        print("📝 Using sample data instead")
        df = pd.DataFrame({
            'District': ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Trichy'],
            'Year': [2024, 2024, 2024, 2024, 2024],
            'Rainfall': [1200, 800, 950, 700, 1100]
        })
        rag_system = GroundwaterRAG(df)
        return rag_system, df


# Initialize global variables
rag_system, df = initialize_rag_system()

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDRbWHmj1iCupKQyGDnFB2d09Hy1dqGAqg")
client = genai.Client(api_key=api_key)

conversation_history = []
has_greeted = False


# ======================================================
# 🈳 Helper Functions
# ======================================================
def detect_greeting(text):
    greetings_en = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    greetings_ta = ["வணக்கம்", "ஹாய்", "ஹலோ", "நல்வரவு"]
    text_lower = text.lower()
    return any(g in text_lower for g in greetings_en) or any(g in text for g in greetings_ta)


def detect_tamil(text):
    return any('\u0B80' <= ch <= '\u0BFF' for ch in text)


# ======================================================
# 🤖 RAG Query Processing
# ======================================================
def process_rag_query(question: str):
    """Process query using RAG approach"""
    relevant_chunks = rag_system.retrieve_relevant_chunks(question, top_k=5)

    if not relevant_chunks:
        return {
            "answer": "Sorry, I couldn't find relevant information in the database.",
            "retrieved_chunks": [],
            "context_used": ""
        }

    print("\n📚 Retrieved chunks:")
    for i, chunk in enumerate(relevant_chunks):
        print(f"  {i+1}. [Similarity: {chunk['similarity']:.3f}] {chunk['text'][:100]}...")

    context = "\n\n".join([f"Document {i+1}: {chunk['text']}" for i, chunk in enumerate(relevant_chunks)])

    is_tamil = detect_tamil(question)
    language = "Tamil" if is_tamil else "English"

    prompt = f"""
You are a groundwater data analyst assistant.

Retrieved Context:
{context}

User Question: "{question}"

Instructions:
1. Answer based ONLY on the retrieved context above.
2. If the context doesn't contain the answer, say so clearly.
3. Provide specific numbers, districts, and years from the context.
4. Answer in {language}.
5. Be conversational and helpful.

Answer:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )
        answer = response.candidates[0].content.parts[0].text.strip()

        return {
            "answer": answer,
            "retrieved_chunks": relevant_chunks,
            "context_used": context
        }

    except Exception as e:
        err_msg = "மன்னிக்கவும் 💧" if is_tamil else f"Error: {str(e)} 💧"
        return {"answer": err_msg, "retrieved_chunks": [], "context_used": ""}


# ======================================================
# 💧 Main Chatbot Function
# ======================================================
def rag_groundwater_chatbot(question):
    global has_greeted
    q_lower = question.lower().strip()
    is_tamil = detect_tamil(question)

    # ---------------------------
    # 🟢 Greeting logic
    # ---------------------------
    if detect_greeting(question) and not any(
        kw in q_lower for kw in [
            "rain", "district", "allocation", "groundwater", "cluster", "data", "year",
            "மழை", "நீர்", "மாவட்டம்"
        ]
    ):
        if not has_greeted:
            has_greeted = True
            if is_tamil:
                return {"answer": "வணக்கம்! நான் ஆக்வா — உங்கள் நிலத்தடி நீர் RAG உதவியாளர். 😊", "retrieved_chunks": []}
            else:
                return {"answer": "Hello! I'm Aqua — your RAG-powered groundwater assistant. 😊", "retrieved_chunks": []}
        else:
            if is_tamil:
                return {"answer": "மீண்டும் வணக்கம்! உங்களுக்கு என்ன உதவி தேவை?", "retrieved_chunks": []}
            else:
                return {"answer": "Hi again! How can I assist you?", "retrieved_chunks": []}

    # ---------------------------
    # 🔍 Identify data-related query
    # ---------------------------
    data_keywords = [
        "rainfall", "rain", "precipitation", "usage", "recharge", "cluster",
        "district", "state", "efficiency", "average", "highest", "lowest",
        "compare", "trend", "groundwater", "allocation", "data", "level",
        "மாவட்டம்", "மழை", "நீர்", "அளவு", "show", "tell", "what", "which"
    ]
    is_data_question = any(word in q_lower for word in data_keywords)

    # ---------------------------
    # 💧 If it's a data-related query
    # ---------------------------
    if is_data_question:
        # Load your CSV for fuzzy matching
        df = pd.read_csv("groundwater_final.csv")

        # Apply fuzzy matching
        district_match = fuzzy_match_district(question, df)
        if district_match:
            print(f"[INFO] Fuzzy matched district → {district_match}")
            # Append matched district name to the query for more accuracy
            question += f" (district: {district_match})"

        result = process_rag_query(question)
        result = convert_numpy(result)  # ensure JSON safe
        return result

    # ---------------------------
    # 💬 Otherwise, normal conversation (non-data)
    # ---------------------------
    language_instruction = "Reply in Tamil." if is_tamil else "Reply in English."
    conversation_prompt = f"""
You are a friendly AI assistant named Aqua.
User message: "{question}"
{language_instruction}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[conversation_prompt],
        )
        reply = response.candidates[0].content.parts[0].text.strip()
    except Exception:
        reply = "மன்னிக்கவும் 💧" if is_tamil else "Sorry 💧"

    return {"answer": reply, "retrieved_chunks": []}


def conversational_rag_chatbot(user_input):
    """Main entry point for conversational chatbot (returns JSON-serializable dict)."""
    global conversation_history

    # record user message
    conversation_history.append({"role": "user", "content": user_input})

    # call the existing rag logic
    raw_result = rag_groundwater_chatbot(user_input)

    # Normalize into a standard result dict with required keys
    result = {}

    if isinstance(raw_result, dict):
        result["answer"] = raw_result.get("answer", "")
        result["retrieved_chunks"] = raw_result.get("retrieved_chunks", raw_result.get("sources", []))
        if "context_used" in raw_result:
            result["context_used"] = raw_result.get("context_used", "")
    else:
        result["answer"] = str(raw_result)
        result["retrieved_chunks"] = []

    # Convert any numpy/pandas numeric types

    # give me with streamlit and give me updated full code and dont bake the code
    result = convert_numpy(result)

    # add assistant reply to history
    conversation_history.append({"role": "assistant", "content": str(result.get("answer", ""))})

    return result


# ======================================================
# 🌊 STREAMLIT INTERFACE (APPENDED - DOES NOT MODIFY ABOVE LOGIC)
# ======================================================
import streamlit as st

st.set_page_config(page_title="💧 Aqua - Groundwater RAG Chatbot", page_icon="🌊", layout="wide")

st.title("💧 Aqua — Groundwater RAG Chatbot")
st.write("Ask anything about rainfall, clusters, or groundwater data. Supports both English and Tamil.")

# Persist chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar: Debug / Settings
with st.sidebar:
    st.header("Settings & Debug")
    show_chunks = st.checkbox("Show retrieved chunks", value=True)
    api_key_input = st.text_input("GEMINI API KEY (optional)", value="", type="password")
    if api_key_input:
        try:
            client.api_key = api_key_input
            st.success("API key updated in runtime (temporary)")
        except Exception:
            st.error("Could not set API key")

# Input box
user_input = st.chat_input("Type your question here...")

if user_input:
    with st.spinner("Thinking... 💭"):
        result = conversational_rag_chatbot(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", result.get("answer", "")))

# Display chat history
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").markdown(f"🧑‍💬 {msg}")
    else:
        st.chat_message("assistant").markdown(f"🤖 {msg}")

# Optionally show retrieved context for transparency
if st.session_state.chat_history and show_chunks:
    # show the last result's chunks if available
    last_chunks = []
    try:
        last_chunks = result.get("retrieved_chunks", [])
    except Exception:
        last_chunks = []

    if last_chunks:
        with st.expander("🔍 Retrieved Chunks (for transparency):"):
            for i, chunk in enumerate(last_chunks, 1):
                st.markdown(f"**Chunk {i}:** {chunk.get('text', '')}")
                if 'similarity' in chunk:
                    st.caption(f"Similarity: {chunk.get('similarity', 0):.3f}")

# Footer
st.markdown("---")
st.caption("Aqua — Groundwater RAG assistant. Data comes from your MongoDB or sample data fallback.")
