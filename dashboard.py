import streamlit as st
import sqlite3
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

def load_data(query, params=None):
    db_path = 'patent_database.db'
    if not os.path.exists(db_path):
        st.error(f"Database not found at {db_path}. Please run `python main.py` first.")
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

col1, col2, col3 = st.columns(3)

with col1:
    val = total_patents_df.iloc[0]['t'] if not total_patents_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Total Patents Analyzed</div></div>', unsafe_allow_html=True)
with col2:
    val = total_inventors_df.iloc[0]['t'] if not total_inventors_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Registered Inventors</div></div>', unsafe_allow_html=True)
with col3:
    val = total_companies_df.iloc[0]['t'] if not total_companies_df.empty else 0
    st.markdown(f'<div class="metric-container"><div class="metric-value">{val:,}</div><div class="metric-label">Company Assignees</div></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Main layout logic
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Trends", "🏆 Top Innovators", "🌍 Global Distribution", "🔍 Search & Explore"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Patent Activity Over Time")
    st.markdown("""
    <div class="info-card">
    This visualization tracks the volume of patents filed and granted each year. 
    A spike in filings often indicates a period of rapid technological advancement or an increase in R&D investment.
    </div>
    """, unsafe_allow_html=True)
    
    # We now have grant_year and filing_year
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
                                 line=dict(color='#3b82f6', width=4), fill='tozeroy'))
        fig.add_trace(go.Scatter(x=trends_df['activity_year'], y=trends_df['grants'], name='Grants',
                                 line=dict(color='#10b981', width=4, dash='dot')))
        
        fig.update_layout(
            title_text="Annual Patent Filings vs Grants",
            title_font=dict(size=24, color="#f8fafc"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cbd5e1",
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(showgrid=False, title="Year"),
            yaxis=dict(showgrid=True, gridcolor="#334155", title="Number of Patents"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

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

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9em; letter-spacing: 0.05em;'>DATA POWERED BY SQLITE PIPELINE BACKEND</p>", unsafe_allow_html=True)
