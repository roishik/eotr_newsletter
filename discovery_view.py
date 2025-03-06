# discovery_view.py
import streamlit as st
from datetime import datetime, timedelta
from news_service import NewsAPIService

def render_news_discovery():
    """
    Renders the 'Discover News' section in Streamlit, allowing users
    to pick a topic, timeframe, and search for relevant articles.
    Selected articles persist in `st.session_state["selected_articles"]`.
    """
    # Apply custom styling
    st.markdown("""
    <style>
    .news-card {
        background-color: white;
        border-radius: 8px;
        border-left: 4px solid #5F9EA0;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .news-card-dark {
        background-color: #3c4043;
        border-radius: 8px;
        border-left: 4px solid #8ab4f8;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .trending-tag {
        background-color: #5F9EA0;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-left: 8px;
    }
    .read-more-btn {
        background-color: #5F9EA0;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 0.8rem;
        margin-top: 10px;
        display: inline-block;
    }
    .search-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .search-container-dark {
        background-color: #3c4043;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .saved-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .saved-container-dark {
        background-color: #3c4043;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .saved-article {
        background-color: #f8f9fa;
        border-left: 3px solid #5F9EA0;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .saved-article-dark {
        background-color: #4c4f52;
        border-left: 3px solid #8ab4f8;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Determine theme
    is_dark_mode = st.session_state.get("theme", "Light") == "Dark"

    # Update the header with styled banner
    st.markdown(f"""
    <div style="
        background: linear-gradient(to right, #2e6c80, #5F9EA0);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        color: white;
    ">
        <div style="flex: 0 0 30px;">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 20H5V9L12 4L19 9V20Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 16H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 13H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div style="flex: 1; margin-left: 15px;">
            <h2 style="margin: 0; font-size: 1.5rem; color: white;">Discover News</h2>
            <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">Find trending articles for your newsletter</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create a card-like container for search options
    search_container_class = "search-container-dark" if is_dark_mode else "search-container"
    search_title_color = "#8ab4f8" if is_dark_mode else "#2e6c80"
    search_border_color = "#5f6368" if is_dark_mode else "#e6e6e6"
    
    st.markdown(f"""
    <div class="{search_container_class}">
        <h3 style="
            color: {search_title_color};
            margin-top: 0;
            font-size: 1.2rem;
            border-bottom: 1px solid {search_border_color};
            padding-bottom: 8px;
        ">Search Parameters</h3>
    </div>
    """, unsafe_allow_html=True)

    # Rest of your search controls
    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox(
            "Choose a topic",
            ["AI", "Auto Industry", "Technology"],
            key="news_topic"
        )
    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            ["Last Week", "Last Month"],
            key="news_timeframe"
        )
    
    custom_query = st.text_input("Enter additional keywords (optional)", key="news_query")
    
    # Convert timeframe to date range
    if timeframe == "Last Week":
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    else:  # "Last Month"
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        today = datetime.utcnow()
        first_day_of_last_month = today.replace(day=1) - timedelta(days=1)
        first_day_of_last_month = first_day_of_last_month.replace(day=1)
        from_date = max(thirty_days_ago, first_day_of_last_month).strftime("%Y-%m-%d")

    to_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Initialize session state for search results
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []

    if "selected_articles" not in st.session_state:
        st.session_state["selected_articles"] = []

    # Styled search button
    if st.button("🔍 Search News", key="search_btn"):
        # Show loading animation
        with st.spinner("Searching for news..."):
            # Combine topic + custom query
            final_query = topic
            if custom_query.strip():
                final_query += f" {custom_query.strip()}"

            # Call NewsAPI
            newsapi = NewsAPIService()
            try:
                articles = newsapi.fetch_articles(
                    query=final_query,
                    from_date=from_date,
                    to_date=to_date,
                    sort_by="popularity",
                    page_size=20
                )
                st.session_state["search_results"] = articles
            except Exception as e:
                st.error(f"Error fetching news: {e}")
                st.session_state["search_results"] = []

    # Display results with modern cards
    articles = st.session_state["search_results"]
    selected_articles = st.session_state["selected_articles"]
    
    if not articles:
        st.info("Enter your criteria and press 'Search News' to begin.")
    else:
        st.success(f"Found {len(articles)} articles!")
        
        # Add sorting options
        sort_option = st.selectbox(
            "Sort articles by:",
            ["Popularity", "Most Recent", "Relevance"],
            key="sort_option"
        )
        
        # Sorting logic
        if sort_option == "Most Recent":
            articles = sorted(articles, key=lambda x: x.get("publishedAt", ""), reverse=True)
        
        # Display articles in a modern card layout
        for idx, article in enumerate(articles):
            title = article["title"]
            source = article["source"]["name"] if article["source"] else "Unknown"
            published = article.get("publishedAt", "")[:10]
            description = article.get("description", "")
            url = article.get("url", "")
            trending_icon = "🔥" if idx < 3 else ""
            
            # Check if article is selected
            checked = any(a["title"] == title for a in selected_articles)
            
            # Card style based on theme
            card_class = "news-card-dark" if is_dark_mode else "news-card"
            text_color = "#e8eaed" if is_dark_mode else "#333"
            meta_color = "#aaa" if is_dark_mode else "#777"
            
            # Card HTML
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-weight: bold; font-size: 1.1rem; color: {text_color};">
                        {trending_icon} {title}
                        {f'<span class="trending-tag">Trending</span>' if idx < 3 else ''}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 0.8rem; color: {meta_color};">{source}</span>
                    <span style="font-size: 0.8rem; color: {meta_color};">{published}</span>
                </div>
                <p style="margin: 5px 0; font-size: 0.9rem; color: {text_color};">{description[:120]}...</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <a href="{url}" target="_blank" class="read-more-btn">Read Article</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add checkbox for selection under the card
            is_selected = st.checkbox(f"Save this article to my collection", value=checked, key=f"article_{idx}")
            
            # Handle selection persistence
            if is_selected and not any(a["title"] == title for a in selected_articles):
                selected_articles.append(article)
            elif not is_selected:
                selected_articles = [a for a in selected_articles if a["title"] != title]
        
        # Update session state with selections
        st.session_state["selected_articles"] = selected_articles

    # Show selected articles in a nice collection view
    if selected_articles:
        saved_container_class = "saved-container-dark" if is_dark_mode else "saved-container"
        saved_title_color = "#8ab4f8" if is_dark_mode else "#2e6c80"
        saved_border_color = "#5f6368" if is_dark_mode else "#e6e6e6"
        saved_article_class = "saved-article-dark" if is_dark_mode else "saved-article"
        saved_text_color = "#e8eaed" if is_dark_mode else "#333"
        saved_meta_color = "#aaa" if is_dark_mode else "#777"
        link_color = "#8ab4f8" if is_dark_mode else "#5F9EA0"
        
        st.markdown(f"""
        <div class="{saved_container_class}">
            <h3 style="
                color: {saved_title_color};
                margin-top: 0;
                font-size: 1.2rem;
                border-bottom: 1px solid {saved_border_color};
                padding-bottom: 8px;
            ">Saved Articles ({len(selected_articles)})</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Show saved articles in two columns
        col1, col2 = st.columns(2)
        for i, article in enumerate(selected_articles):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"""
                <div class="{saved_article_class}">
                    <div style="font-weight: bold; color: {saved_text_color};">{article['title']}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: {saved_meta_color}; margin-top: 5px;">
                        <span>{article['source']['name']}</span>
                        <a href="{article['url']}" target="_blank" style="color: {link_color};">Read</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add a button to add selected articles to newsletter with improved styling
        col1, col2 = st.columns([3, 1])
        with col2:
            st.button("➕ Add to Newsletter", key="add_to_newsletter")
            
        # Add option to clear selections
        with col1:
            if st.button("🗑️ Clear All Selections", key="clear_selections"):
                st.session_state["selected_articles"] = []
                st.rerun()