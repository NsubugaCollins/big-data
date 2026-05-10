import streamlit as st
import sqlite3
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

def load_data(query, params=None):
    # Use absolute path relative to this file to avoid issues with different CWDs
    main_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patent_database.db')
    sample_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patent_database_sample.db')
    
    if os.path.exists(main_db):
        db_path = main_db
    elif os.path.exists(sample_db):
        db_path = sample_db
    else:
        st.error(f"Database not found. Please run the extraction locally to generate patent_database.db.")
        return pd.DataFrame()
        
    conn = sqlite3.connect(db_path)
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Patent Intelligence", page_icon="🧬", layout="wide")

# Custom CSS for a premium look
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
    }
    /* Typography adjustments */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    p, label {
        color: #cbd5e1 !important;
    }
    /* Premium Metric Containers */
    .metric-container {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        text-align: center;
        border: 1px solid #334155;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        border-color: #3b82f6;
    }
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 8px;
    }
    /* Tab styling overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #f8fafc !important;
        border-bottom-color: #3b82f6 !important;
    }
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    /* Custom info boxes */
    .info-card {
        background: #1e293b;
        padding: 15px;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Global Patent Intelligence")
st.markdown("### Discover innovation trends, top inventors, and leading assignees worldwide.")

st.markdown("<br>", unsafe_allow_html=True)

# Quick stats row
total_patents_df = load_data("SELECT COUNT(*) as t FROM patents")
total_inventors_df = load_data("SELECT COUNT(*) as t FROM inventors")
total_companies_df = load_data("SELECT COUNT(*) as t FROM companies")
pendency_df = load_data("""
    SELECT ROUND(AVG(
        (JULIANDAY(grant_date) - JULIANDAY(filing_date)) / 365.25
    ), 1) as avg_years
    FROM patents
    WHERE grant_date IS NOT NULL AND filing_date IS NOT NULL
        AND grant_date > filing_date
""")
countries_df = load_data("SELECT COUNT(DISTINCT country) as t FROM inventors WHERE country != 'Unknown'")
year_span_df = load_data("SELECT MIN(grant_year) as mn, MAX(grant_year) as mx FROM patents WHERE grant_year IS NOT NULL")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    val = total_patents_df.iloc[0]['t'] if not total_patents_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Total Patents</div></div>', unsafe_allow_html=True)
with col2:
    val = total_inventors_df.iloc[0]['t'] if not total_inventors_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Unique Inventors</div></div>', unsafe_allow_html=True)
with col3:
    val = total_companies_df.iloc[0]['t'] if not total_companies_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Company Assignees</div></div>', unsafe_allow_html=True)
with col4:
    val = pendency_df.iloc[0]['avg_years'] if not pendency_df.empty and pendency_df.iloc[0]['avg_years'] else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val}y</div><div class="metric-label">Avg. Grant Wait</div></div>', unsafe_allow_html=True)
with col5:
    val = countries_df.iloc[0]['t'] if not countries_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val}</div><div class="metric-label">Countries Represented</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Main layout logic
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Market Trends", "🏆 Top Innovators", "🌍 Global Distribution", "🔍 Search & Explore", "📊 Deep Analytics", "🏢 Company Intelligence"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Patent Activity Over Time")
    st.markdown("""
    <div class="info-card">
    This visualization tracks the volume of patents filed and granted each year.
    A spike in filings indicates rapid technological advancement or increased R&D investment.
    The gap between filings and grants reflects examination delays at patent offices.
    </div>
    """, unsafe_allow_html=True)

    trends_df = load_data("""
        SELECT
            COALESCE(grant_year, filing_year) as activity_year,
            COUNT(CASE WHEN grant_year IS NOT NULL THEN 1 END) as grants,
            COUNT(CASE WHEN filing_year IS NOT NULL THEN 1 END) as filings
        FROM patents
        WHERE grant_year IS NOT NULL OR filing_year IS NOT NULL
        GROUP BY activity_year
        ORDER BY activity_year
    """)

    if not trends_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trends_df['activity_year'], y=trends_df['filings'], name='Filings',
                                 line=dict(color='#3b82f6', width=4), fill='tozeroy',
                                 fillcolor='rgba(59,130,246,0.1)'))
        fig.add_trace(go.Scatter(x=trends_df['activity_year'], y=trends_df['grants'], name='Grants',
                                 line=dict(color='#10b981', width=4, dash='dot')))
        fig.update_layout(
            title_text="Annual Patent Filings vs Grants",
            title_font=dict(size=24, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(showgrid=False, title="Year"),
            yaxis=dict(showgrid=True, gridcolor="#334155", title="Number of Patents"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    # YoY Growth Rate
    st.subheader("Year-over-Year Innovation Growth Rate")
    st.markdown("""
    <div class="info-card">
    The growth rate measures how rapidly patenting activity is accelerating or decelerating year on year.
    Sustained positive growth rates signal long-term R&D momentum; negative rates may indicate market saturation
    or economic downturns affecting R&D budgets.
    </div>
    """, unsafe_allow_html=True)
    if not trends_df.empty:
        growth = trends_df[trends_df['grants'] > 0].copy()
        growth['yoy_growth'] = growth['grants'].pct_change() * 100
        growth = growth.dropna()
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in growth['yoy_growth']]
        fig_g = go.Figure(go.Bar(
            x=growth['activity_year'], y=growth['yoy_growth'],
            marker_color=colors, name='YoY Growth %'
        ))
        fig_g.add_hline(y=0, line_color='#94a3b8', line_dash='dash')
        fig_g.update_layout(
            title_text="Year-over-Year Patent Grant Growth (%)",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1",
            xaxis=dict(showgrid=False, title="Year"),
            yaxis=dict(showgrid=True, gridcolor="#334155", title="Growth Rate (%)")
        )
        st.plotly_chart(fig_g, use_container_width=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Leading Innovation Drivers")
    st.markdown("""
    <div class="info-card">
    The following charts highlight the most prolific inventors and companies based on their total patent counts. 
    This identifies the key players currently dominating the intellectual property landscape.
    </div>
    """, unsafe_allow_html=True)
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        inventors_df = load_data("""
            SELECT i.name, COUNT(r.patent_id) as total_patents
            FROM inventors i
            JOIN relationships r ON i.inventor_id = r.inventor_id
            GROUP BY i.name
            ORDER BY total_patents DESC
            LIMIT 15
        """)
        if not inventors_df.empty:
            fig2 = px.bar(inventors_df, x='total_patents', y='name', orientation='h',
                          labels={'total_patents': 'Patents', 'name': ''},
                          color='total_patents', color_continuous_scale='Blues')
            fig2.update_layout(
                title_text="Top 15 Inventors",
                title_font=dict(size=20, color="#f8fafc"),
                yaxis={'categoryorder':'total ascending'},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig2, use_container_width=True)

    with col2_2:
        companies_df = load_data("""
            SELECT c.name, COUNT(r.patent_id) as total_patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            GROUP BY c.name
            ORDER BY total_patents DESC
            LIMIT 15
        """)
        if not companies_df.empty:
            fig3 = px.bar(companies_df, x='total_patents', y='name', orientation='h',
                          labels={'total_patents': 'Patents', 'name': ''},
                          color='total_patents', color_continuous_scale='Purples')
            fig3.update_layout(
                title_text="Top 15 Assignees (Companies)",
                title_font=dict(size=20, color="#f8fafc"),
                yaxis={'categoryorder':'total ascending'},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Global Patent Origin")
    st.markdown("""
    <div class="info-card">
    This distribution shows where the world's innovations are originating. 
    A higher concentration in specific regions often correlates with robust local technology ecosystems and government incentives.
    </div>
    """, unsafe_allow_html=True)
    
    country_df = load_data("""
        SELECT i.country, COUNT(r.patent_id) as total_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.country
        ORDER BY total_patents DESC
    """)
    if not country_df.empty:
        fig4 = px.pie(country_df.head(15), values='total_patents', names='country', hole=0.5,
                      color_discrete_sequence=px.colors.sequential.Teal)
        fig4.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#0f1117', width=2)))
        fig4.update_layout(
            title_text="Top 15 Countries",
            title_font=dict(size=24, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Advanced Patent Search")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("Search by Title or Abstract", placeholder="e.g., Artificial Intelligence")
    with col_s2:
        sort_by = st.selectbox("Order By", ["Grant Date (Newest)", "Grant Date (Oldest)", "Patent ID", "Title"])
    with col_s3:
        limit = st.slider("Results Limit", 10, 500, 50)
    
    order_sql = "grant_date DESC"
    if sort_by == "Grant Date (Oldest)": order_sql = "grant_date ASC"
    elif sort_by == "Patent ID": order_sql = "patent_id ASC"
    elif sort_by == "Title": order_sql = "title ASC"
    
    if search_query:
        search_sql = f"""
            SELECT patent_id, title, grant_date, filing_date 
            FROM patents 
            WHERE title LIKE ? OR abstract LIKE ?
            ORDER BY {order_sql}
            LIMIT ?
        """
        results_df = load_data(search_sql, params=(f"%{search_query}%", f"%{search_query}%", limit))
    else:
        search_sql = f"""
            SELECT patent_id, title, grant_date, filing_date 
            FROM patents 
            ORDER BY {order_sql}
            LIMIT ?
        """
        results_df = load_data(search_sql, params=(limit,))
    
    if not results_df.empty:
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    else:
        st.info("No patents found matching your criteria.")

with tab5:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Patent Pendency Analysis")
    st.markdown("""
    <div class="info-card">
    <b>Patent pendency</b> is the time between a patent application filing date and the grant date.
    Long pendency (3–5+ years) can delay inventors from commercializing technology.
    Tracking this over time reveals efficiency improvements or bottlenecks at patent offices worldwide.
    </div>
    """, unsafe_allow_html=True)

    pendency_trend = load_data("""
        SELECT filing_year,
               ROUND(AVG((JULIANDAY(grant_date) - JULIANDAY(filing_date)) / 365.25), 2) as avg_pendency_years,
               COUNT(*) as patent_count
        FROM patents
        WHERE grant_date IS NOT NULL AND filing_date IS NOT NULL
              AND grant_date > filing_date AND filing_year IS NOT NULL
              AND filing_year >= 1980
        GROUP BY filing_year
        HAVING patent_count > 50
        ORDER BY filing_year
    """)
    if not pendency_trend.empty:
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(
            x=pendency_trend['filing_year'], y=pendency_trend['avg_pendency_years'],
            name='Avg Pendency (years)', line=dict(color='#f59e0b', width=3),
            fill='tozeroy', fillcolor='rgba(245,158,11,0.1)',
            mode='lines+markers', marker=dict(size=5)
        ))
        fig_p.update_layout(
            title_text="Average Patent Pendency by Filing Year",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1",
            xaxis=dict(showgrid=False, title="Filing Year"),
            yaxis=dict(showgrid=True, gridcolor="#334155", title="Years to Grant")
        )
        st.plotly_chart(fig_p, use_container_width=True)

    st.subheader("Inventor Productivity Distribution")
    st.markdown("""
    <div class="info-card">
    Most inventors file only 1–2 patents in their career — a classic <b>power-law (Pareto) distribution</b>.
    A small elite group of serial inventors drives a disproportionate share of innovation.
    This insight is critical for identifying key talent and R&D hotspots.
    </div>
    """, unsafe_allow_html=True)
    inv_prod = load_data("""
        SELECT patent_count, COUNT(*) as num_inventors
        FROM (
            SELECT inventor_id, COUNT(patent_id) as patent_count
            FROM relationships
            GROUP BY inventor_id
        )
        GROUP BY patent_count
        ORDER BY patent_count
        LIMIT 30
    """)
    if not inv_prod.empty:
        fig_ip = px.bar(
            inv_prod, x='patent_count', y='num_inventors',
            labels={'patent_count': 'Patents per Inventor', 'num_inventors': 'Number of Inventors'},
            color='num_inventors', color_continuous_scale='Blues'
        )
        fig_ip.update_layout(
            title_text="Inventor Productivity: How Many Patents Does Each Inventor File?",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", coloraxis_showscale=False
        )
        st.plotly_chart(fig_ip, use_container_width=True)

    st.subheader("Innovation by Decade")
    st.markdown("""
    <div class="info-card">
    Grouping patent activity into decades reveals macro-level waves of innovation — from the electronics boom
    of the 1980s, through the internet era of the 1990s–2000s, to the modern AI and biotech surge.
    Each decade's dominant assignees reflect the technology paradigm of that era.
    </div>
    """, unsafe_allow_html=True)
    decade_df = load_data("""
        SELECT (grant_year / 10) * 10 as decade, COUNT(*) as total
        FROM patents
        WHERE grant_year IS NOT NULL AND grant_year >= 1950
        GROUP BY decade
        ORDER BY decade
    """)
    if not decade_df.empty:
        decade_df['decade_label'] = decade_df['decade'].astype(str) + 's'
        fig_d = px.bar(
            decade_df, x='decade_label', y='total',
            color='total', color_continuous_scale='Viridis',
            labels={'decade_label': 'Decade', 'total': 'Patents Granted'}
        )
        fig_d.update_layout(
            title_text="Patents Granted Per Decade",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", coloraxis_showscale=False
        )
        st.plotly_chart(fig_d, use_container_width=True)

with tab6:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Top Companies: Innovation Over Time")
    st.markdown("""
    <div class="info-card">
    Tracking how the top 6 corporations' annual patent output evolves reveals competitive R&D strategy shifts.
    A company ramping up patents signals aggressive market positioning; a decline may indicate strategic pivots
    or reduced R&D spending.
    </div>
    """, unsafe_allow_html=True)

    top6_df = load_data("""
        SELECT c.name FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.name ORDER BY COUNT(*) DESC LIMIT 6
    """)
    if not top6_df.empty:
        top6_names = tuple(top6_df['name'].tolist())
        placeholders = ','.join(['?' for _ in top6_names])
        co_time = load_data(f"""
            SELECT c.name, p.grant_year, COUNT(*) as patents
            FROM companies c
            JOIN relationships r ON c.company_id = r.company_id
            JOIN patents p ON r.patent_id = p.patent_id
            WHERE c.name IN ({placeholders}) AND p.grant_year IS NOT NULL
            GROUP BY c.name, p.grant_year
            ORDER BY p.grant_year
        """, params=top6_names)
        if not co_time.empty:
            fig_ct = px.line(
                co_time, x='grant_year', y='patents', color='name',
                labels={'grant_year': 'Year', 'patents': 'Patents Granted', 'name': 'Company'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_ct.update_layout(
                title_text="Top 6 Companies — Annual Patent Output",
                title_font=dict(size=20, color="#f8fafc"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis=dict(showgrid=False, title="Year"),
                yaxis=dict(showgrid=True, gridcolor="#334155", title="Patents per Year"),
                legend=dict(title='Company')
            )
            st.plotly_chart(fig_ct, use_container_width=True)

    st.subheader("Country vs. Top Company Share")
    st.markdown("""
    <div class="info-card">
    This breakdown shows which countries are home to the most prolific patent-filing companies.
    Dominant countries like the <b>US, Japan, and South Korea</b> often reflect strong state-backed R&D cultures
    and robust intellectual property legal frameworks that incentivize patenting.
    </div>
    """, unsafe_allow_html=True)
    country_co = load_data("""
        SELECT i.country, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country != 'Unknown'
        GROUP BY i.country
        ORDER BY patents DESC
        LIMIT 20
    """)
    if not country_co.empty:
        fig_cc = px.bar(
            country_co, x='country', y='patents',
            color='patents', color_continuous_scale='Teal',
            labels={'country': 'Country', 'patents': 'Total Patents'}
        )
        fig_cc.update_layout(
            title_text="Top 20 Countries by Patent Output",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", coloraxis_showscale=False,
            xaxis=dict(showgrid=False, title="Country", tickangle=-35),
            yaxis=dict(showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_cc, use_container_width=True)

    st.subheader("Corporate Concentration: Patent Share of Top 10 Companies")
    st.markdown("""
    <div class="info-card">
    If the top 10 companies hold a large share of all patents, it signals a <b>highly concentrated innovation
    landscape</b> dominated by tech giants. A more distributed share points to a diverse, open innovation
    ecosystem with healthy competition from SMEs and research institutions.
    </div>
    """, unsafe_allow_html=True)
    conc_df = load_data("""
        SELECT c.name, COUNT(r.patent_id) as patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.name ORDER BY patents DESC LIMIT 10
    """)
    total_pats = total_patents_df.iloc[0]['t'] if not total_patents_df.empty else 1
    if not conc_df.empty:
        top10_total = conc_df['patents'].sum()
        others = total_pats - top10_total
        conc_all = pd.concat([conc_df, pd.DataFrame([{'name': 'All Others', 'patents': others}])])
        fig_conc = px.pie(
            conc_all, values='patents', names='name', hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_conc.update_traces(
            textposition='inside', textinfo='percent+label',
            marker=dict(line=dict(color='#0f1117', width=2))
        )
        fig_conc.update_layout(
            title_text="Patent Share: Top 10 Companies vs. Rest of World",
            title_font=dict(size=20, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1", showlegend=False
        )
        st.plotly_chart(fig_conc, use_container_width=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9em; letter-spacing: 0.05em;'>DATA POWERED BY SQLITE PIPELINE BACKEND</p>", unsafe_allow_html=True)
