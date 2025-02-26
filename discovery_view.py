# discovery_view.py
import streamlit as st
from datetime import datetime, timedelta
from news_service import NewsAPIService

def render_news_discovery():
    """
    Renders the 'Discover News' section in Streamlit, allowing users
    to pick a topic, timeframe, and search for relevant articles.
    Returns a list of selected articles (each is a dict with keys like title, url, etc.).
    """
    st.header("Discover News")
    st.write("Use this section to find trending news in AI, Auto Industry, or Technology.")

    # -- Topic selection
    topic = st.selectbox(
        "Choose a topic",
        ["AI", "Auto Industry", "Technology"]
    )

    # -- Timeframe selection
    timeframe = st.selectbox(
        "Timeframe",
        ["Last Week", "Last Month"]
    )

    # Convert timeframe to date range
    if timeframe == "Last Week":
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    else:  # "Last Month"
        from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    to_date = datetime.utcnow().strftime("%Y-%m-%d")

    # -- Optional custom query
    custom_query = st.text_input("Enter additional keywords (optional)", "")

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
                sort_by="popularity",  # sorts primarily by popularity
                page_size=20
            )

        if not articles:
            st.warning("No articles found. Try changing your keywords or timeframe.")
        else:
            st.success(f"Found {len(articles)} articles!")

            # Display articles in a selectable list
            selected_indices = []
            for idx, article in enumerate(articles):
                title = article["title"]
                source = article["source"]["name"] if article["source"] else "Unknown"
                published = article.get("publishedAt", "")[:10]
                description = article.get("description", "")
                # Basic logic for trending (just highlight top few articles)
                trending_icon = "🔥" if idx < 3 else ""

                # Show a checkbox for selection
                if st.checkbox(f"{trending_icon} {title}", key=f"article_{idx}"):
                    selected_indices.append(idx)

                # Show minimal metadata
                st.write(f"**Source**: {source} | **Date**: {published}")
                st.write(f"**Description**: {description[:120]}...")  # limit text
                st.markdown(f"[Read More]({article.get('url', '')})")
                st.markdown("---")

            # -- Prepare the selected articles data
            # Store it in session_state so we can retrieve in app.py
            selected_articles = [articles[i] for i in selected_indices]
            st.session_state["discovered_articles"] = selected_articles

            if selected_articles:
                st.success(f"{len(selected_articles)} article(s) selected.")
    else:
        st.info("Enter your criteria and press 'Search News' to begin.")
