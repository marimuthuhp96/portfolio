/* ============================================================
   Mari Muthu Portfolio — chatbot.js
   "Ask My Portfolio" — Rule-based intelligent chatbot
   Answers questions using portfolio content only.
   ============================================================ */

'use strict';

const PORTFOLIO_KB = {
  /* ── Identity ──────────────────────────────────────────── */
  identity: {
    keywords: ['who are you','who is marimuthu','tell me about yourself','introduce yourself','about you','your name'],
    response: `👋 I'm **Mari Muthu**, a passionate Data Analyst based in **Coimbatore, Tamil Nadu, India**.

I specialize in transforming raw data into actionable business insights using **SQL, Python, Power BI, Advanced Excel, and Machine Learning**. I'm currently pursuing my **MSc in Data Analytics at Bharathiar University** (completing May 2026) and actively seeking opportunities as a Data Analyst or Business Intelligence Analyst.

My mission: solve real-world business problems through data-driven decision making.`,
  },

  /* ── Skills ─────────────────────────────────────────────── */
  skills: {
    keywords: ['skills','tools','technologies','what do you know','tech stack','expertise','proficiency','capabilities'],
    response: `🛠️ Here's my technical skills overview:

**Data & Analytics:**
• Advanced Excel (92%) — Pivot Tables, Power Query, DAX, Conditional Formatting
• SQL (90%) — CTEs, Window Functions, Joins, Subqueries, Views
• Python (82%) — Pandas, Scikit-learn, Matplotlib, Seaborn, NumPy

**Business Intelligence:**
• Power BI (88%) — DAX, Data Modeling, Drill-through, Bookmarks, KPIs
• Power Query (85%) — ETL workflows, data transformation
• Power Pivot & DAX (78%)

**Machine Learning & AI:**
• Scikit-learn, K-Means, DBSCAN, Feature Engineering
• GraphRAG, Neo4j, NLP, Knowledge Graphs

**Other Tools:** Git, GitHub, VS Code, Jupyter Notebooks

I'm also strong in Statistics, Data Cleaning, and Data Visualization.`,
  },

  /* ── SQL ─────────────────────────────────────────────────── */
  sql: {
    keywords: ['sql','database','query','joins','cte','window function','aggregate','subquery'],
    response: `🗃️ **SQL is one of my strongest skills (90% proficiency).**

I build complex, optimized queries for real-world business analytics:

• **Joins** — INNER, LEFT, RIGHT, FULL OUTER, CROSS joins
• **CTEs** — Readable, modular query structures for complex logic
• **Window Functions** — ROW_NUMBER(), RANK(), LEAD/LAG, running totals
• **Aggregate Functions** — SUM, AVG, COUNT, GROUP BY with HAVING
• **Subqueries** — Correlated and non-correlated
• **Views** — Reusable virtual tables for business reporting

📁 **SQL Analytics Portfolio** — my dedicated SQL project covers 8+ business query scenarios, schema design, and performance-optimized reporting queries.`,
  },

  /* ── Python ─────────────────────────────────────────────── */
  python: {
    keywords: ['python','pandas','numpy','matplotlib','seaborn','scikit','jupyter','programming'],
    response: `🐍 **Python proficiency: 82%**

I use Python extensively for end-to-end data analytics workflows:

• **Data Manipulation** — Pandas for cleaning, merging, reshaping data
• **Visualization** — Matplotlib, Seaborn for EDA charts
• **Machine Learning** — Scikit-learn for clustering, classification, regression
• **NLP & AI** — Text processing, entity extraction, GraphRAG pipelines
• **Web Scraping** — BeautifulSoup, Requests
• **Notebooks** — Jupyter for exploratory analysis

Featured Python projects:
1. 🌊 **Groundwater Analytics** — K-Means & DBSCAN clustering
2. 🍽️ **GraphRAG Restaurant** — Neo4j + Gemini AI knowledge graph`,
  },

  /* ── Power BI ─────────────────────────────────────────────── */
  powerbi: {
    keywords: ['power bi','powerbi','dax','dashboard','report','bi','business intelligence','data model'],
    response: `📊 **Power BI proficiency: 88%**

Power BI is my primary business intelligence tool. I build professional, interactive dashboards featuring:

• **DAX Measures** — Custom KPIs, YoY growth, running totals, time intelligence
• **Data Modeling** — Star/snowflake schemas, relationship management
• **Drill-through** — Enabling detailed analysis from summary views
• **Bookmarks & Navigation** — Professional UX for business users
• **Slicers & Filters** — Dynamic, cross-filtering interactivity
• **Power Query** — ETL transformations, custom M functions

📁 **Power BI Dashboard Portfolio** — 5+ interactive dashboards covering sales analytics, KPI tracking, regional performance, and business reporting.`,
  },

  /* ── Excel ─────────────────────────────────────────────── */
  excel: {
    keywords: ['excel','pivot table','power query','vlookup','xlookup','spreadsheet','advanced excel'],
    response: `📗 **Advanced Excel proficiency: 92% (my highest-rated skill)**

I use Excel as a powerful analytics and BI tool:

• **Power Query** — Data extraction, transformation, loading (ETL)
• **Power Pivot** — Data modeling with millions of rows
• **Pivot Tables & Charts** — Interactive summary analysis
• **DAX in Excel** — Advanced calculated columns and measures
• **Conditional Formatting** — Data-driven visual highlighting
• **XLOOKUP, INDEX-MATCH** — Advanced lookups

📁 **Data Jobs Salary Dashboard** — An end-to-end Excel project analyzing global data job salaries, in-demand skills, and location trends using Power Query + Power Pivot.`,
  },

  /* ── Machine Learning ─────────────────────────────────── */
  ml: {
    keywords: ['machine learning','ml','clustering','classification','model','ai','artificial intelligence','kmeans','dbscan','scikit'],
    response: `🤖 **Machine Learning proficiency: 72%**

I apply ML techniques to solve real analytical problems:

**Unsupervised Learning:**
• K-Means Clustering — Group segmentation, pattern discovery
• DBSCAN — Density-based anomaly detection

**Supervised Learning:**
• Classification models for predictive analytics
• Feature engineering and selection
• Model evaluation (accuracy, F1, confusion matrix)

**Applied ML Projects:**
1. 🌊 **Groundwater Analytics** — Applied K-Means & DBSCAN on groundwater data from Indian districts to identify resource patterns and anomalies
2. 🍽️ **GraphRAG Restaurant** — NLP-based entity extraction and sentiment analysis

I'm continuously expanding my ML knowledge, working toward proficiency in neural networks and advanced model deployment.`,
  },

  /* ── Groundwater Project ─────────────────────────────── */
  groundwater: {
    keywords: ['groundwater','water','clustering','dbscan','kmeans','environmental','india'],
    response: `🌊 **Groundwater Analytics Platform**

One of my flagship Python + ML projects:

**Problem:** Analyze groundwater resources across Indian districts to identify patterns, anomalies, and risk zones.

**Approach:**
• Performed comprehensive **EDA** on groundwater quality and depth data
• Applied **Feature Engineering** to create meaningful analytical features
• Used **K-Means Clustering** to group districts by water availability patterns
• Applied **DBSCAN** to detect anomalous districts with critical groundwater issues
• Built an **interactive analytics dashboard** for visual exploration

**Tools:** Python, Pandas, Scikit-learn, Matplotlib, Seaborn

**Key Insights:**
• Identified 3 major groundwater risk clusters across Indian districts
• Detected outlier zones requiring immediate attention
• Created actionable visualizations for policy decision-making

**Impact:** Actionable environmental intelligence for groundwater resource management.`,
  },

  /* ── GraphRAG Project ────────────────────────────────── */
  graphrag: {
    keywords: ['graphrag','graph','neo4j','restaurant','nlp','gemini','knowledge graph','rag','recommendation'],
    response: `🍽️ **GraphRAG Restaurant Analytics System**

An AI-powered project at the cutting edge of NLP and knowledge graphs:

**Problem:** Extract intelligent insights from unstructured restaurant review data and enable natural language querying.

**Approach:**
• Built a **Knowledge Graph** in Neo4j from restaurant reviews
• Nodes: Restaurants, Dishes, Customers, Sentiments, Locations
• Relationships: REVIEWED, MENTIONS, RECOMMENDS, VISITED
• Applied **NLP** for food entity extraction (dishes, ingredients, service quality)
• Integrated **Gemini API** for intelligent natural language Q&A
• Performed **Sentiment Analysis** (positive/negative/neutral)
• Built a **recommendation engine** based on graph traversal

**Tools:** Python, Neo4j, Gemini API, NLP, GraphRAG framework

**Key Features:**
• Ask "Which restaurants have the best pasta?" → Knowledge graph answers
• Sentiment score per restaurant and dish category
• Entity-level insights: most mentioned foods, service ratings

**Impact:** Demonstrates advanced AI/ML capabilities beyond traditional analytics.`,
  },

  /* ── Salary Dashboard ────────────────────────────────── */
  salary: {
    keywords: ['salary','jobs','data jobs','excel dashboard','pay','compensation','job market'],
    response: `💼 **Data Jobs Salary Dashboard (Excel Project)**

A comprehensive global job market analysis using Excel as a full BI platform:

**Problem:** Understand salary trends, in-demand skills, and location preferences in the global data jobs market.

**Dataset:** Global data science job postings with salary, role, location, and skills data.

**Approach:**
• **Power Query** — Cleaned, merged, and transformed raw job data
• **Power Pivot** — Built a relational data model for cross-analysis
• **Pivot Tables** — Summarized salaries by role, country, experience level
• **Pivot Charts** — Bar charts, maps, scatter plots for trend visualization
• **Conditional Formatting** — Highlighted high-paying markets
• **Slicers** — Interactive filtering by country, role, and experience

**Key Insights:**
• Data Scientists earn highest globally (avg $95K+)
• USA leads in both job count and salary
• SQL and Python are the most in-demand skills
• Remote roles offer competitive salaries vs on-site

**Impact:** Actionable job market intelligence for data professionals.`,
  },

  /* ── Education ───────────────────────────────────────── */
  education: {
    keywords: ['education','degree','university','college','msc','bachelor','academic','study','bharathiar'],
    response: `🎓 **Educational Background**

**Master of Science — Data Analytics**
📍 Bharathiar University, Coimbatore
📅 Completing: May 2026
Coursework: Statistics, Machine Learning, Business Intelligence, Data Visualization, Big Data Analytics, Research Methods

**Bachelor of Science — Mathematics**
📍 Bharathiar University, Coimbatore
Strong foundation in: Linear Algebra, Statistics, Probability Theory, Calculus

My mathematical background gives me a strong foundation for statistical analysis and ML model understanding.`,
  },

  /* ── Experience ──────────────────────────────────────── */
  experience: {
    keywords: ['experience','work','job','career','lenskart','trance','company','employment','professional'],
    response: `💼 **Professional Experience**

**Executive — Lenskart Solutions Pvt. Ltd.**
• Worked with operational processes and customer service workflows
• Developed analytical thinking through business problem-solving
• Gained experience in data-driven operational decisions

**Executive — Trance Home India Pvt. Ltd.**
• Managed operational responsibilities with attention to detail
• Handled reporting and process management
• Developed strong organizational and analytical skills

Currently transitioning full-time into Data Analytics, combining business domain knowledge with technical expertise.`,
  },

  /* ── Projects overview ───────────────────────────────── */
  projects: {
    keywords: ['projects','portfolio','work','built','created','developed','project'],
    response: `📁 **Portfolio Projects Overview**

I have built 5 featured analytics projects:

1. 📊 **Data Jobs Salary Dashboard** (Excel)
   → Global salary trend analysis using Power Query, Power Pivot, Pivot Tables

2. 📈 **Power BI Dashboard Portfolio** (Power BI)
   → 5+ interactive business dashboards with DAX, drill-through, bookmarks

3. 🌊 **Groundwater Analytics Platform** (Python + ML)
   → EDA, K-Means & DBSCAN clustering, analytics dashboard

4. 🍽️ **GraphRAG Restaurant Analytics** (Python + AI)
   → Knowledge graph, NLP, Gemini API, sentiment analysis

5. 🗃️ **SQL Analytics Portfolio** (SQL)
   → Business queries, CTEs, window functions, reporting

Ask me about any specific project for detailed information!`,
  },

  /* ── Contact ─────────────────────────────────────────── */
  contact: {
    keywords: ['contact','email','hire','recruit','linkedin','github','reach','connect'],
    response: `📬 **Connect with Mari Muthu**

🐙 **GitHub:** [github.com/marimuthuhp96](https://github.com/marimuthuhp96)
💼 **LinkedIn:** [linkedin.com/in/mari-muthu-837002219](https://linkedin.com/in/mari-muthu-837002219)
📍 **Location:** Coimbatore, Tamil Nadu, India

✅ **Currently open to:**
• Full-Time Data Analyst roles
• Business Intelligence Analyst positions
• SQL Developer roles
• Junior Data Scientist opportunities

I'm actively seeking opportunities where I can apply my SQL, Python, Power BI, and ML skills to solve real business problems. Let's connect! 🚀`,
  },

  /* ── Default ─────────────────────────────────────────── */
  default: {
    response: `🤔 Great question! I can answer questions about:

• 👤 **About Marimuthu** — background, education, goals
• 🛠️ **Skills & Tools** — SQL, Python, Power BI, Excel, ML
• 📁 **Projects** — all 5 portfolio projects in detail
• 💼 **Experience** — professional background
• 🎓 **Education** — MSc Data Analytics at Bharathiar University
• 📬 **Contact** — how to reach out or hire

Try asking: *"What Power BI projects have you built?"* or *"Tell me about your SQL skills."*`,
  },
};

/* ── Chatbot Engine ───────────────────────────────────────── */
(function initChatbot() {
  const messagesEl  = document.getElementById('chat-messages');
  const inputEl     = document.getElementById('chat-input');
  const sendBtn     = document.getElementById('chat-send');
  const suggestions = document.querySelectorAll('.chat-suggestion');
  if (!messagesEl || !inputEl || !sendBtn) return;

  /* Find best matching KB entry */
  function findResponse(userMsg) {
    const msg = userMsg.toLowerCase().trim();
    let bestKey   = null;
    let bestScore = 0;

    for (const [key, entry] of Object.entries(PORTFOLIO_KB)) {
      if (key === 'default') continue;
      for (const kw of entry.keywords) {
        if (msg.includes(kw)) {
          const score = kw.length;
          if (score > bestScore) {
            bestScore = score;
            bestKey   = key;
          }
        }
      }
    }

    return bestKey ? PORTFOLIO_KB[bestKey].response : PORTFOLIO_KB.default.response;
  }

  /* Render markdown-lite: **bold** */
  function renderMd(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener" style="color:#60A5FA;text-decoration:underline;">$1</a>')
      .replace(/\n/g, '<br>');
  }

  function appendMsg(text, type) {
    const wrap   = document.createElement('div');
    wrap.className = `chat-msg ${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'chat-msg-avatar';
    avatar.textContent = type === 'bot' ? 'M' : 'Y';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = renderMd(text);

    if (type === 'bot') {
      wrap.appendChild(avatar);
      wrap.appendChild(bubble);
    } else {
      wrap.appendChild(bubble);
      wrap.appendChild(avatar);
    }

    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg bot';
    wrap.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'chat-msg-avatar';
    avatar.textContent = 'M';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    wrap.appendChild(avatar);
    wrap.appendChild(indicator);
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function hideTyping() {
    const ind = document.getElementById('typing-indicator');
    if (ind) ind.remove();
  }

  function sendMessage(text) {
    const msg = (text || inputEl.value).trim();
    if (!msg) return;

    appendMsg(msg, 'user');
    inputEl.value = '';
    showTyping();

    /* Simulate thinking delay */
    setTimeout(() => {
      hideTyping();
      const reply = findResponse(msg);
      appendMsg(reply, 'bot');
    }, 800 + Math.random() * 600);
  }

  sendBtn.addEventListener('click', () => sendMessage());

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  /* Suggestion chips */
  suggestions.forEach(chip => {
    chip.addEventListener('click', () => sendMessage(chip.textContent));
  });

  /* Initial greeting */
  setTimeout(() => {
    appendMsg(`👋 Hi! I'm **Marimuthu's Portfolio AI**. Ask me anything about his skills, projects, experience, or how to get in touch!\n\nTry: *"What Power BI projects have you built?"*`, 'bot');
  }, 500);
})();
