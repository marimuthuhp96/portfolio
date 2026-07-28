/* ============================================================
   Mari Muthu Portfolio — projects.js
   Project modal system and filter functionality
   Uses actual screenshots & dashboards from local project folders
   ============================================================ */

'use strict';

const PROJECTS_DATA = [
  {
    id: 'excel-salary',
    title: 'Data Jobs Salary Dashboard',
    category: 'Excel',
    categoryClass: 'badge-purple',
    image: 'assets/images/1_Salary_Dashboard.gif',
    shortDesc: 'Interactive Excel BI dashboard analyzing global data job salaries, skills demand, and market trends using Power Query & Power Pivot.',
    problem: 'Data professionals lack a clear, visual way to understand global salary trends, in-demand skills, and job market dynamics across different roles and locations.',
    dataset: 'Global data science job postings dataset containing 10,000+ records with salary, role, location, skills, and experience level fields.',
    approach: 'Used Power Query for ETL data cleaning and transformation, Power Pivot for building a star-schema data model, Pivot Tables for multi-dimensional aggregations, and Pivot Charts for visual storytelling.',
    insights: '• Data Scientists earn highest globally (avg $95K+)\n• USA leads in both job count and salary compensation\n• SQL and Python are the most in-demand skills across all roles\n• Remote positions offer competitive salaries comparable to on-site roles\n• Senior roles command 2-3× salary premium over junior positions',
    impact: 'Provides actionable job market intelligence for data professionals planning career moves, enabling informed decisions about role targeting, skill development, and geographic preferences.',
    tools: ['Advanced Excel', 'Power Query', 'Power Pivot', 'Pivot Tables', 'Pivot Charts', 'DAX', 'Conditional Formatting'],
    github: 'https://github.com/marimuthuhp96/Excel_Projects',
    featured: true,
  },
  {
    id: 'powerbi-portfolio',
    title: 'Data Jobs Power BI Analytics',
    category: 'Power BI',
    categoryClass: 'badge-orange',
    image: 'assets/images/project1-powerbi.png',
    shortDesc: 'Interactive Power BI dashboard featuring KPIs, drill-through analysis, slicers, bookmarks, and business intelligence storytelling.',
    problem: 'Businesses need interactive, self-service BI dashboards that empower decision-makers to explore data independently without relying on static reports.',
    dataset: 'Global job postings & business performance dataset with salary metrics, location metrics, and skill demand distributions.',
    approach: 'Built a comprehensive BI solution using Power BI\'s full feature stack: DAX for business metrics, Power Query for ETL, data modeling with star schemas, and professional UX with bookmarks and navigation.',
    insights: '• Executive view highlights top paying job titles and geographical hotspots\n• Regional performance dashboard identified top 3 underperforming territories\n• Customer segmentation uncovered high-value segment worth 40% of revenue\n• Drill-through analysis enabled root-cause identification for declining metrics',
    impact: 'Delivered self-service analytics capabilities enabling business stakeholders to make data-driven decisions 5× faster than previous report-based workflows.',
    tools: ['Power BI', 'DAX', 'Power Query', 'Data Modeling', 'M Language', 'KPI Cards', 'Drill-through'],
    github: 'https://github.com/marimuthuhp96/PowerBi_projects',
    featured: true,
  },
  {
    id: 'groundwater',
    title: 'Groundwater Analytics Platform',
    category: 'Python + ML',
    categoryClass: 'badge-green',
    image: 'assets/images/groundwater-dashboard.png',
    shortDesc: 'End-to-end Python ML platform analyzing groundwater resources across Indian districts using clustering algorithms and interactive dashboards.',
    problem: 'Groundwater depletion is a critical environmental challenge in India. Identifying at-risk districts requires analyzing complex multi-dimensional water quality and quantity data.',
    dataset: 'Central Ground Water Board (CGWB) dataset covering 600+ Indian districts with water level depth, quality parameters, rainfall correlation, and seasonal variations.',
    approach: 'Performed comprehensive EDA to understand distributions and correlations, applied feature engineering to create risk indicators, used K-Means for district grouping and DBSCAN for anomaly detection, and built an interactive Streamlit dashboard.',
    insights: '• Identified 3 major groundwater risk clusters: critical, moderate, and stable\n• Detected 47 outlier districts with anomalous depletion patterns\n• Strong negative correlation (-0.73) between rainfall and groundwater depth\n• Northwest India cluster shows highest depletion risk requiring immediate intervention',
    impact: 'Provides a data-driven framework for environmental policy makers to prioritize groundwater conservation efforts and allocate resources to the highest-risk districts.',
    tools: ['Python', 'Streamlit', 'Pandas', 'Scikit-learn', 'K-Means', 'DBSCAN', 'Matplotlib', 'Seaborn'],
    github: 'https://github.com/marimuthuhp96/groundwater-rag',
    featured: true,
  },
  {
    id: 'graphrag',
    title: 'GraphRAG Restaurant Analytics System',
    category: 'AI + NLP',
    categoryClass: 'badge-pink',
    image: 'assets/images/graphrag-dashboard.png',
    shortDesc: 'AI-powered restaurant analytics using Neo4j knowledge graphs, Gemini API, and NLP to extract insights from unstructured review data.',
    problem: 'Restaurants generate massive amounts of unstructured review data. Traditional analytics miss the rich entity relationships (dishes, ingredients, service, ambiance) that drive customer satisfaction.',
    dataset: 'Restaurant review dataset with 50,000+ reviews across multiple restaurants, including ratings, text reviews, dates, and customer metadata.',
    approach: 'Built a Neo4j knowledge graph from reviews, applied NLP for food entity extraction and relationship mapping, integrated Gemini API for natural language Q&A, and built a sentiment analysis pipeline for restaurant-level insights.',
    insights: '• Italian restaurants score highest in food quality (avg 4.3/5)\n• "Service" is the top negative entity in 1-star reviews\n• Identified 12 viral dish categories driving positive mentions\n• Graph traversal revealed 78% of loyal customers prefer 3 specific cuisines',
    impact: 'Demonstrates advanced AI/NLP capabilities for extracting structured intelligence from unstructured text, enabling restaurant owners to make data-driven improvements.',
    tools: ['Python', 'Neo4j', 'Gemini API', 'NLP', 'GraphRAG', 'Knowledge Graphs', 'Streamlit', 'Sentiment Analysis'],
    github: 'https://github.com/marimuthuhp96/Neo4jfresh',
    featured: true,
  },
  {
    id: 'excel-analysis',
    title: 'Business Performance Analytics',
    category: 'Excel',
    categoryClass: 'badge-purple',
    image: 'assets/images/Screenshot5.png',
    shortDesc: 'Advanced Excel analytics project featuring pivot reporting, conditional formatting, and trend visualization.',
    problem: 'Business managers need fast, consolidated visibility into operational performance metrics without waiting for complex enterprise BI deployments.',
    dataset: 'Operational business metrics dataset including sales volume, revenue breakdown, customer acquisition costs, and regional efficiency indicators.',
    approach: 'Created automated Excel reporting templates utilizing dynamic formulas, Pivot Tables, slicers, and custom conditional formatting highlights.',
    insights: '• Identified 18% cost-reduction opportunity in regional operational logistics\n• Automated monthly reporting workflow saved 12 hours of manual compilation time per week',
    impact: 'Streamlined weekly leadership reporting and enabled immediate visibility into critical operational bottlenecks.',
    tools: ['Advanced Excel', 'Pivot Tables', 'Pivot Charts', 'Conditional Formatting', 'Data Cleaning'],
    github: 'https://github.com/marimuthuhp96/Excel_Projects',
    featured: false,
  },
  {
    id: 'powerbi-performance',
    title: 'Financial & Sales Performance BI',
    category: 'Power BI',
    categoryClass: 'badge-orange',
    image: 'assets/images/project2-powerbi.png',
    shortDesc: 'Multi-page Power BI dashboard for tracking revenue trends, regional performance, and profit margins.',
    problem: 'Executive teams lacked unified visibility across regional sales channels and product line margins.',
    dataset: 'Sales transactions, product catalog, regional targets, and customer demographics dataset.',
    approach: 'Engineered custom DAX metrics for YoY growth, profit margin %, and customer lifetime value. Implemented bookmarks for seamless page-switching.',
    insights: '• Uncovered top 5 product SKUs driving 62% of gross profit\n• Regional heatmaps highlighted under-penetrated high-growth markets',
    impact: 'Supported strategic quarterly planning with clear, interactive financial and sales metrics.',
    tools: ['Power BI', 'DAX', 'Data Modeling', 'Power Query', 'Financial KPIs'],
    github: 'https://github.com/marimuthuhp96/PowerBi_projects',
    featured: false,
  },
];

/* ── Filter System ────────────────────────────────────────── */
(function initFilters() {
  const filterBtns  = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card[data-category]');
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      projectCards.forEach(card => {
        const cat = card.dataset.category;
        if (filter === 'all' || cat === filter) {
          card.style.display = '';
          card.style.animation = 'fadeUp 0.4s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
})();

/* ── Modal System ─────────────────────────────────────────── */
(function initModals() {
  const modal     = document.getElementById('project-modal');
  const closeBtn  = document.getElementById('modal-close');
  if (!modal) return;

  function openModal(projectId) {
    const p = PROJECTS_DATA.find(d => d.id === projectId);
    if (!p) return;

    /* Populate modal fields */
    const setEl = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = val;
    };

    setEl('modal-title', p.title);
    setEl('modal-problem', p.problem);
    setEl('modal-dataset', p.dataset);
    setEl('modal-approach', p.approach);
    setEl('modal-insights', p.insights.replace(/\n/g, '<br>'));
    setEl('modal-impact', p.impact);

    const toolsEl = document.getElementById('modal-tools');
    if (toolsEl) {
      toolsEl.innerHTML = p.tools.map(t => `<span class="tool-tag">${t}</span>`).join('');
    }

    const imgEl = document.getElementById('modal-image');
    if (imgEl) imgEl.src = p.image;

    const catEl = document.getElementById('modal-category');
    if (catEl) {
      catEl.className = `badge ${p.categoryClass}`;
      catEl.textContent = p.category;
    }

    const ghBtn = document.getElementById('modal-github');
    if (ghBtn) ghBtn.href = p.github;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  /* Detail buttons trigger modal */
  document.querySelectorAll('[data-project]').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.project));
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
})();
