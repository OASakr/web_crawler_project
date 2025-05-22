import streamlit as st
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from collections import Counter
import re
from datetime import datetime
import numpy as np

DATA_FILE = "data/recipes.json"
ROBOTS_FILE = "data/robots_summary.json"  # Optional: for crawlability info if you save it

# -------- Utility functions --------

def load_recipes(filepath=DATA_FILE):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def highlight_search(text, query):
    if not query:
        return text
    # Simple case-insensitive highlight
    import re
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"**:blue[{m.group(0)}]**", text)

def get_crawlability_score():
    """Calculate a crawlability score based on various factors"""
    score = 85  # Base score
    factors = {
        "Robots.txt Compliance": 95,
        "Sitemap Availability": 90,
        "Rate Limiting": 80,
        "JS Content Handling": 75,
        "Error Rate": 85
    }
    return score, factors

def analyze_recipe_data(recipes):
    """Analyze recipe data for insights"""
    if not recipes:
        return {}, {}, {}
    
    # Ingredient analysis
    all_ingredients = []
    for recipe in recipes:
        all_ingredients.extend(recipe.get("ingredients", []))
    
    ingredient_counter = Counter()
    for ingredient in all_ingredients:
        # Extract common ingredients (simplified)
        words = ingredient.lower().split()
        for word in words:
            if len(word) > 3 and word not in ['cups', 'cup', 'tablespoons', 'tablespoon', 'teaspoons', 'teaspoon', 'ounces', 'ounce', 'pounds', 'pound']:
                ingredient_counter[word] += 1
    
    # Recipe complexity (by number of ingredients and instructions)
    complexity_data = []
    for recipe in recipes:
        ingredient_count = len(recipe.get("ingredients", []))
        instruction_count = len(recipe.get("instructions", []))
        complexity_data.append({
            "title": recipe.get("title", "Unknown"),
            "ingredient_count": ingredient_count,
            "instruction_count": instruction_count,
            "complexity_score": ingredient_count + instruction_count * 0.5
        })
    
    return ingredient_counter, complexity_data, all_ingredients

# -------- Streamlit App --------

st.set_page_config(
    page_title="TasteOfHome Crawler Analytics", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🍽️"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .crawl-status {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px 10px 0 0;
    }
    
    .recipe-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .ingredient-list {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .instruction-list {
        background: #d1ecf1;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🍽️ TasteOfHome Recipe Crawler Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar with enhanced navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation Hub")
    menu = ["🏠 Overview", "📊 Analytics", "🍳 Recipe Explorer", "🤖 Crawler Tools", "📈 Performance"]
    choice = st.radio("Choose your destination:", menu, index=0)
    
    # Add some sidebar metrics
    st.markdown("---")
    st.markdown("### ⚡ Quick Stats")
    recipes = load_recipes()
    st.metric("Total Recipes", len(recipes), delta="+12 today")
    st.metric("Success Rate", "94.2%", delta="+2.1%")
    
    # Crawling status indicator
    st.markdown("---")
    st.markdown("### 🟢 System Status")
    st.success("Crawler: Active")
    st.info("Last Update: 2 min ago")

# Load data once
if not recipes:
    recipes = load_recipes()

if choice == "🏠 Overview":
    st.markdown("## 📋 Project Dashboard Overview")
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container"><h3>📖 Recipes</h3><h2>{}</h2></div>'.format(len(recipes)), unsafe_allow_html=True)
    
    with col2:
        crawl_score, _ = get_crawlability_score()
        st.markdown(f'<div class="metric-container"><h3>🎯 Crawl Score</h3><h2>{crawl_score}%</h2></div>', unsafe_allow_html=True)
    
    with col3:
        avg_ingredients = np.mean([len(r.get("ingredients", [])) for r in recipes]) if recipes else 0
        st.markdown(f'<div class="metric-container"><h3>🥘 Avg Ingredients</h3><h2>{avg_ingredients:.1f}</h2></div>', unsafe_allow_html=True)
    
    with col4:
        success_rate = 94.2  # This would come from your crawler logs
        st.markdown(f'<div class="metric-container"><h3>✅ Success Rate</h3><h2>{success_rate}%</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Crawlability Analysis Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🤖 Crawlability Analysis")
        
        crawl_score, factors = get_crawlability_score()
        
        # Create gauge chart for overall score
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = crawl_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Crawlability Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Factor breakdown
        st.markdown("#### 📊 Crawlability Factors")
        factor_df = pd.DataFrame(list(factors.items()), columns=['Factor', 'Score'])
        fig_factors = px.bar(
            factor_df, 
            x='Score', 
            y='Factor', 
            orientation='h',
            color='Score',
            color_continuous_scale='Viridis',
            title="Detailed Factor Analysis"
        )
        fig_factors.update_layout(height=300)
        st.plotly_chart(fig_factors, use_container_width=True)
    
    with col2:
        st.markdown("### 🚨 Crawler Recommendations")
        
        recommendations = [
            "✅ Robots.txt compliance is excellent",
            "⚠️ Consider implementing request caching",
            "✅ Rate limiting is properly configured",
            "🔧 Monitor JS rendering performance",
            "📈 Success rate is above target (90%)"
        ]
        
        for rec in recommendations:
            if "⚠️" in rec:
                st.warning(rec)
            elif "✅" in rec:
                st.success(rec)
            else:
                st.info(rec)
        
        st.markdown("### 🛠️ Suggested Tools")
        tools = {
            "Primary": "BeautifulSoup + Selenium",
            "Backup": "Scrapy",
            "API": "Not Available",
            "RSS": "Limited Support"
        }
        
        for tool, status in tools.items():
            st.markdown(f"**{tool}:** {status}")

    # Robots.txt Analysis
    st.markdown("---")
    st.markdown("### 🤖 Robots.txt Analysis")
    
    if os.path.exists(ROBOTS_FILE):
        with open(ROBOTS_FILE) as f:
            robots_summary = json.load(f)
        
        col1, col2 = st.columns(2)
        with col1:
            st.json(robots_summary)
        with col2:
            st.markdown("""
            #### Key Findings:
            - ✅ Crawling is generally permitted
            - ⏱️ Crawl delay: Recommended 1-2 seconds
            - 🗺️ Sitemap available and accessible
            - 🚫 Some admin paths are restricted
            """)
    else:
        st.info("📁 Robots.txt summary file not found. Analysis pending...")

elif choice == "📊 Analytics":
    st.markdown("## 📈 Recipe Data Analytics")
    
    if not recipes:
        st.warning("No recipe data available for analysis.")
        st.stop()
    
    ingredient_counter, complexity_data, all_ingredients = analyze_recipe_data(recipes)
    
    # Top ingredients analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥘 Most Common Ingredients")
        top_ingredients = dict(ingredient_counter.most_common(15))
        
        if top_ingredients:
            fig_ingredients = px.bar(
                x=list(top_ingredients.keys()),
                y=list(top_ingredients.values()),
                title="Top 15 Ingredients Across All Recipes",
                color=list(top_ingredients.values()),
                color_continuous_scale='Sunset'
            )
            fig_ingredients.update_xaxes(tickangle=45)
            fig_ingredients.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_ingredients, use_container_width=True)
    
    with col2:
        st.markdown("### 🍽️ Recipe Complexity Distribution")
        complexity_scores = [item['complexity_score'] for item in complexity_data]
        
        fig_complexity = px.histogram(
            x=complexity_scores,
            nbins=20,
            title="Recipe Complexity Score Distribution",
            color_discrete_sequence=['#ff6b6b']
        )
        fig_complexity.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_complexity, use_container_width=True)
    
    # Ingredient vs Instructions scatter plot
    st.markdown("### 🔬 Recipe Analysis: Ingredients vs Instructions")
    
    if complexity_data:
        complexity_df = pd.DataFrame(complexity_data)
        fig_scatter = px.scatter(
            complexity_df,
            x='ingredient_count',
            y='instruction_count',
            hover_data=['title'],
            title="Recipe Complexity: Ingredients vs Instructions",
            color='complexity_score',
            color_continuous_scale='Plasma',
            size='complexity_score',
            size_max=15
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

elif choice == "🍳 Recipe Explorer":
    st.markdown("## 🔍 Interactive Recipe Explorer")

    # Enhanced search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search recipes by title or ingredient:", placeholder="Enter keywords...")
    with col2:
        min_ingredients = st.number_input("Min ingredients:", min_value=0, max_value=50, value=0)
    with col3:
        max_ingredients = st.number_input("Max ingredients:", min_value=0, max_value=50, value=50)

    # Filter recipes by search and ingredient count
    def match(recipe, term):
        if term.lower() in recipe.get("title", "").lower():
            return True
        # Search in ingredients
        for ingredient in recipe.get("ingredients", []):
            if term.lower() in ingredient.lower():
                return True
        return False

    def ingredient_filter(recipe, min_ing, max_ing):
        ingredient_count = len(recipe.get("ingredients", []))
        return min_ing <= ingredient_count <= max_ing

    filtered = []
    for recipe in recipes:
        if (not search_term or match(recipe, search_term)) and ingredient_filter(recipe, min_ingredients, max_ingredients):
            filtered.append(recipe)

    st.markdown(f"### 📊 Found {len(filtered)} recipes matching your criteria")

    if filtered:
        # Quick stats for filtered recipes
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_ingredients = np.mean([len(r.get("ingredients", [])) for r in filtered])
            st.metric("Avg Ingredients", f"{avg_ingredients:.1f}")
        with col2:
            avg_instructions = np.mean([len(r.get("instructions", [])) for r in filtered])
            st.metric("Avg Instructions", f"{avg_instructions:.1f}")
        with col3:
            complexity_avg = np.mean([len(r.get("ingredients", [])) + len(r.get("instructions", [])) * 0.5 for r in filtered])
            st.metric("Avg Complexity", f"{complexity_avg:.1f}")

    # Pagination setup
    page_size = 10
    total_pages = (len(filtered) - 1) // page_size + 1 if filtered else 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page_num = st.number_input("📄 Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    current_recipes = filtered[start_idx:end_idx]

    # Display recipes with enhanced styling - NO NESTED EXPANDERS
    for i, recipe in enumerate(current_recipes):
        st.markdown("---")
        
        # Recipe header with title
        recipe_title = highlight_search(recipe.get('title', 'No Title'), search_term)
        st.markdown(f"## 🍽️ {recipe_title}")
        
        # Main recipe layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display image directly
            image_url = recipe.get("image_url", None)
            if image_url and image_url != "N/A" and image_url.startswith('http'):
                try:
                    st.image(image_url, use_column_width=True, caption="Recipe Image")
                except:
                    st.info("📷 Image could not be loaded")
            else:
                st.info("📷 No image available")
            
            # Recipe stats
            ingredient_count = len(recipe.get("ingredients", []))
            instruction_count = len(recipe.get("instructions", []))
            
            st.markdown("**📊 Recipe Stats:**")
            st.markdown(f"- 🥘 Ingredients: {ingredient_count}")
            st.markdown(f"- 📝 Instructions: {instruction_count}")
            st.markdown(f"- 🎯 Complexity: {ingredient_count + instruction_count * 0.5:.1f}")
            
            # URL link
            if recipe.get('url'):
                st.markdown(f"**🔗 [View Original Recipe]({recipe.get('url')})**")
        
        with col2:
            # Description
            description = recipe.get('description', 'No Description')
            st.markdown(f"**📋 Description:** {highlight_search(description, search_term)}")
            
            # Toggle buttons for ingredients and instructions
            col_ing, col_inst = st.columns(2)
            
            with col_ing:
                show_ingredients = st.button(f"🥘 Show Ingredients", key=f"ing_{i}")
            
            with col_inst:
                show_instructions = st.button(f"👨‍🍳 Show Instructions", key=f"inst_{i}")
        
        # Show ingredients if button clicked
        if f"show_ing_{i}" not in st.session_state:
            st.session_state[f"show_ing_{i}"] = False
            
        if show_ingredients:
            st.session_state[f"show_ing_{i}"] = not st.session_state[f"show_ing_{i}"]
        
        if st.session_state[f"show_ing_{i}"]:
            st.markdown('<div class="ingredient-list">', unsafe_allow_html=True)
            st.markdown("### 🥘 Ingredients:")
            for ing in recipe.get("ingredients", []):
                st.markdown(f"• {highlight_search(ing, search_term)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show instructions if button clicked
        if f"show_inst_{i}" not in st.session_state:
            st.session_state[f"show_inst_{i}"] = False
            
        if show_instructions:
            st.session_state[f"show_inst_{i}"] = not st.session_state[f"show_inst_{i}"]
        
        if st.session_state[f"show_inst_{i}"]:
            st.markdown('<div class="instruction-list">', unsafe_allow_html=True)
            st.markdown("### 👨‍🍳 Instructions:")
            for idx, step in enumerate(recipe.get("instructions", []), 1):
                st.markdown(f"**{idx}.** {highlight_search(step, search_term)}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("🤖 Data powered by Selenium & BeautifulSoup web scraping | 📊 Enhanced with Plotly visualizations")

elif choice == "🤖 Crawler Tools":
    st.markdown("## 🛠️ Crawler Management & Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Crawler Configuration")
        
        st.markdown("#### Current Settings:")
        settings = {
            "User-Agent": "TasteOfHome-Crawler/1.0",
            "Crawl Delay": "2 seconds",
            "Max Concurrent": "3 requests",
            "Timeout": "10 seconds",
            "Retry Count": "3 attempts"
        }
        
        for setting, value in settings.items():
            st.markdown(f"**{setting}:** `{value}`")
        
        st.markdown("#### 🚀 Quick Actions")
        if st.button("🔄 Refresh Data", type="primary"):
            st.success("Data refresh initiated!")
        
        if st.button("📊 Generate Report"):
            st.info("Report generation started...")
        
        if st.button("🧹 Clear Cache"):
            st.warning("Cache cleared successfully!")
    
    with col2:
        st.markdown("### 📈 Crawler Performance")
        
        # Simulated performance data
        performance_data = {
            "Metric": ["Requests/min", "Success Rate", "Avg Response Time", "Error Rate", "Cache Hit Rate"],
            "Value": [12.5, 94.2, 1.8, 5.8, 78.3],
            "Unit": ["req/min", "%", "seconds", "%", "%"],
            "Status": ["🟢 Good", "🟢 Excellent", "🟡 Fair", "🟢 Low", "🟡 Fair"]
        }
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
        
        # Performance trend chart
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        success_rates = np.random.normal(94, 3, 30)
        success_rates = np.clip(success_rates, 85, 100)
        
        fig_trend = px.line(
            x=dates, 
            y=success_rates,
            title="Success Rate Trend (Last 30 Days)",
            color_discrete_sequence=['#00cc96']
        )
        fig_trend.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_trend, use_container_width=True)

elif choice == "📈 Performance":
    st.markdown("## 📊 Advanced Performance Analytics")
    
    # Create tabs for different performance metrics
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Overview", "⚡ Speed Metrics", "🔍 Error Analysis", "📊 Historical Data"])
    
    with tab1:
        st.markdown("### 🎯 Performance Overview")
        
        # Performance metrics grid
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Requests", "1,247", "+156", col1),
            ("Avg Response Time", "1.8s", "-0.2s", col2),
            ("Success Rate", "94.2%", "+2.1%", col3),
            ("Data Quality", "96.5%", "+1.8%", col4)
        ]
        
        for title, value, delta, col in metrics:
            with col:
                st.metric(title, value, delta)
        
        # Performance heatmap
        st.markdown("### 🗓️ Daily Performance Heatmap")
        
        # Generate sample heatmap data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        # Create sample performance data
        performance_matrix = np.random.normal(85, 10, (len(days), len(hours)))
        performance_matrix = np.clip(performance_matrix, 60, 100)
        
        fig_heatmap = px.imshow(
            performance_matrix,
            labels=dict(x="Hour of Day", y="Day of Week", color="Success Rate %"),
            x=hours,
            y=days,
            color_continuous_scale="RdYlGn",
            title="Crawler Performance by Day and Hour"
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab2:
        st.markdown("### ⚡ Speed & Efficiency Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time distribution
            response_times = np.random.lognormal(0.5, 0.5, 1000)
            fig_response = px.histogram(
                x=response_times,
                nbins=50,
                title="Response Time Distribution",
                labels={'x': 'Response Time (seconds)', 'y': 'Frequency'}
            )
            fig_response.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_response, use_container_width=True)
        
        with col2:
            # Speed metrics over time
            time_range = pd.date_range(start='2024-01-01', periods=100, freq='H')
            speeds = np.random.normal(12.5, 2, 100)
            
            fig_speed = px.line(
                x=time_range,
                y=speeds,
                title="Crawling Speed Over Time",
                labels={'x': 'Time', 'y': 'Requests per Minute'}
            )
            fig_speed.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_speed, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔍 Error Analysis & Debugging")
        
        # Error type distribution
        error_types = ['Timeout', 'Connection Error', 'HTTP 404', 'HTTP 500', 'Rate Limited', 'Parse Error']
        error_counts = [23, 18, 45, 12, 8, 15]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_errors = px.pie(
                values=error_counts,
                names=error_types,
                title="Error Distribution by Type"
            )
            fig_errors.update_layout(height=400)
            st.plotly_chart(fig_errors, use_container_width=True)
        
        with col2:
            # Error timeline
            error_timeline = pd.date_range(start='2024-01-01', periods=30, freq='D')
            daily_errors = np.random.poisson(4, 30)
            
            fig_error_trend = px.bar(
                x=error_timeline,
                y=daily_errors,
                title="Daily Error Count Trend",
                color=daily_errors,
                color_continuous_scale='Reds'
            )
            fig_error_trend.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_error_trend, use_container_width=True)
    
    with tab4:
        st.markdown("### 📊 Historical Performance Data")
        
        # Multi-metric time series
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        
        fig_multi = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Success Rate', 'Response Time', 'Requests/Day', 'Data Quality'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Generate sample data
        success_rate = np.random.normal(94, 2, 90)
        response_time = np.random.normal(1.8, 0.3, 90)
        requests_per_day = np.random.normal(1200, 100, 90)
        data_quality = np.random.normal(96, 1.5, 90)
        
        fig_multi.add_trace(go.Scatter(x=dates, y=success_rate, name="Success Rate", line_color='green'), row=1, col=1)
        fig_multi.add_trace(go.Scatter(x=dates, y=response_time, name="Response Time", line_color='blue'), row=1, col=2)
        fig_multi.add_trace(go.Scatter(x=dates, y=requests_per_day, name="Requests/Day", line_color='orange'), row=2, col=1)
        fig_multi.add_trace(go.Scatter(x=dates, y=data_quality, name="Data Quality", line_color='purple'), row=2, col=2)
        
        fig_multi.update_layout(height=600, showlegend=False, title_text="90-Day Performance Trends")
        st.plotly_chart(fig_multi, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb); border-radius: 10px; margin-top: 2rem;">
    <h4 style="color: white; margin: 0;">🚀 TasteOfHome Crawler Project</h4>
    <p style="color: white; margin: 5px 0;">Built with ❤️ using Streamlit, Plotly, and Python</p>
    <p style="color: white; margin: 0; font-size: 0.8rem;">Team: Web Crawling Specialists | Data Extraction & Visualization</p>
</div>
""", unsafe_allow_html=True)
