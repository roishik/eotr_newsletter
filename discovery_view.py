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

    st.header("Discover News")
    st.write("Use this section to find trending news in AI, Auto Industry, or Technology.")

    # -- Topic selection
    topic = st.selectbox(
        "Choose a topic",
        ["AI", "Auto Industry", "Technology"],
        key="news_topic"
    )

    # -- Timeframe selection
    timeframe = st.selectbox(
        "Timeframe",
        ["Last Week", "Last Month"],
        key="news_timeframe"
    )

    # Convert timeframe to date range
    if timeframe == "Last Week":
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    else:  # "Last Month"
        from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    to_date = datetime.utcnow().strftime("%Y-%m-%d")

    # -- Optional custom query
    custom_query = st.text_input("Enter additional keywords (optional)", key="news_query")

    # -- Initialize session state for search results
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []

    if "selected_articles" not in st.session_state:
        st.session_state["selected_articles"] = []

    # -- Search button
    if st.button("Search News"):
        # Combine topic + custom query
        final_query = topic
        if custom_query.strip():
            final_query += f" {custom_query.strip()}"

        # Call NewsAPI
        newsapi = NewsAPIService()
        with st.spinner("Searching for news..."):
            articles = newsapi.fetch_articles(
                query=final_query,
                from_date=from_date,
                to_date=to_date,
                sort_by="popularity",
                page_size=20
            )

        # Store results in session state without resetting selected articles
        st.session_state["search_results"] = articles

    # -- Display results if they exist
    articles = st.session_state["search_results"]
    selected_articles = st.session_state["selected_articles"]
    
    if not articles:
        st.info("Enter your criteria and press 'Search News' to begin.")
    else:
        st.success(f"Found {len(articles)} articles!")

        for idx, article in enumerate(articles):
            title = article["title"]
            source = article["source"]["name"] if article["source"] else "Unknown"
            published = article.get("publishedAt", "")[:10]
            description = article.get("description", "")
            trending_icon = "🔥" if idx < 3 else ""

            # Checkbox for selection (persistent using session state)
            checked = any(a["title"] == title for a in selected_articles)
            is_selected = st.checkbox(f"{trending_icon} {title}", value=checked, key=f"article_{idx}")

            # Handle selection persistence
            if is_selected and not any(a["title"] == title for a in selected_articles):
                selected_articles.append(article)
            elif not is_selected:
                selected_articles = [a for a in selected_articles if a["title"] != title]

            # Show article details
            st.write(f"**Source**: {source} | **Date**: {published}")
            st.write(f"**Description**: {description[:120]}...")
            st.markdown(f"[Read More]({article.get('url', '')})")
            st.markdown("---")

        # Update session state with selections
        st.session_state["selected_articles"] = selected_articles

    # Show selected articles
    if selected_articles:
        st.subheader("Saved Articles:")
        for article in selected_articles:
            st.markdown(f"✅ [{article['title']}]({article['url']})")
