import streamlit as st
from config.prompts import DEFAULT_PROMPTS
from ui.components import (
    section_input_form, 
    show_completion_status, 
    loading_animation,
    display_language_indicator,
    display_prompt_expander
)
from utils.content_utils import (
    extract_article_text, 
    generate_section_content, 
    generate_newsletter_html,
    render_newsletter_preview
)
from services.llm_service import LLMService
import streamlit.components.v1 as components

def render_generate_view(llm_service: LLMService):
    """
    Render the Generate Mode view.
    
    Args:
        llm_service: Instance of LLMService for content generation
    """
    # Two-column layout
    main_panel, right_panel = st.columns([1, 2])

    with main_panel:
        st.header("Content Generation")
        with st.expander("Overall Prompt", expanded=False):
            st.text_area(
                "Overall Newsletter Style",
                value=st.session_state.get("overall_prompt", DEFAULT_PROMPTS["overall"]),
                key="overall_prompt",
                height=150
            )

        # Windshield View Section
        st.subheader("Windshield View")
        windshield_urls, windshield_notes, windshield_prompt = section_input_form(
            "Windshield View",
            "windshield_urls",
            "windshield_notes",
            "windshield_prompt",
            DEFAULT_PROMPTS["windshield"]
        )
        
        st.markdown('<div class="section-controls-row">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="small")
        with col1:
            if st.button("🔄 Gen", key="generate_windshield", help="Generate section"):
                with st.spinner("Generating Windshield section..."):
                    article_text = extract_article_text(windshield_urls)
                    generated_text = generate_section_content(
                        llm_service=llm_service,
                        section_key="windshield",
                        article_text=article_text,
                        notes=windshield_notes,
                        section_prompt=windshield_prompt,
                        provider=st.session_state.get("selected_provider", "OpenAI"),
                        model=st.session_state.get("selected_model", "gpt-4o"),
                        language=st.session_state.get("language", "English")
                    )
                    if "generated_sections" not in st.session_state:
                        st.session_state.generated_sections = {}
                    st.session_state.generated_sections["Windshield View"] = generated_text
                    st.success("Windshield section generated!")
        with col2:
            if st.button("✏️ Edit", key="edit_windshield", help="Edit section"):
                st.session_state.edit_section = True
                st.session_state.current_section = "Windshield View"
        with col3:
            if st.button("🗑️ Del", key="delete_windshield", help="Delete section"):
                if "generated_sections" in st.session_state:
                    st.session_state.generated_sections.pop("Windshield View", None)
                st.success("Windshield section deleted!")
        with col4:
            if st.button("🔍 Prm", key="prompt_windshield", help="Show prompt"):
                st.session_state.show_prompt = True
                st.session_state.current_section = "Windshield View"
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.get("show_prompt", False) and st.session_state.get("current_section") == "Windshield View":
            display_prompt_expander("windshield")
            if st.button("Close Prompt", key="close_prompt_windshield"):
                st.session_state.show_prompt = False
                st.rerun()

        # Rearview Mirror Section (multiple stories)
        st.subheader("Rearview Mirror (Multiple Stories)")
        num_rearview = st.number_input(
            "Number of Rearview Stories",
            min_value=1,
            max_value=5,
            value=st.session_state.get("num_rearview", 3),
            step=1,
            key="num_rearview"
        )
        
        for i in range(1, int(num_rearview) + 1):
            st.markdown(f"**Story {i}**")
            story_urls, story_notes, story_prompt = section_input_form(
                f"Story {i}",
                f"rearview_urls_{i}",
                f"rearview_notes_{i}",
                f"rearview_prompt_{i}",
                DEFAULT_PROMPTS["rearview"]
            )
            
            st.markdown('<div class="section-controls-row">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="small")
            with col1:
                if st.button(f"🔄 Gen", key=f"generate_rearview_{i}", help="Generate section"):
                    with st.spinner(f"Generating Rearview {i} section..."):
                        article_text = extract_article_text(story_urls)
                        generated_text = generate_section_content(
                            llm_service=llm_service,
                            section_key=f"rearview_{i}",
                            article_text=article_text,
                            notes=story_notes,
                            section_prompt=story_prompt,
                            provider=st.session_state.get("selected_provider", "OpenAI"),
                            model=st.session_state.get("selected_model", "gpt-4o"),
                            language=st.session_state.get("language", "English")
                        )
                        
                        if "generated_sections" not in st.session_state:
                            st.session_state.generated_sections = {}
                        
                        st.session_state.generated_sections[f"Rearview Mirror {i}"] = generated_text
                        st.success(f"Rearview {i} section generated!")
            
            with col2:
                if st.button(f"✏️ Edit", key=f"edit_rearview_{i}", help="Edit section"):
                    st.session_state.edit_section = True
                    st.session_state.current_section = f"Rearview Mirror {i}"
            
            with col3:
                if st.button(f"🗑️ Del", key=f"delete_rearview_{i}", help="Delete section"):
                    if "generated_sections" in st.session_state:
                        st.session_state.generated_sections.pop(f"Rearview Mirror {i}", None)
                    st.success(f"Rearview {i} section deleted!")
            
            with col4:
                if st.button(f"🔍 Prm", key=f"prompt_rearview_{i}", help="Show prompt"):
                    st.session_state.show_prompt = True
                    st.session_state.current_section = f"Rearview Mirror {i}"
            
            st.markdown('</div>', unsafe_allow_html=True)
            if st.session_state.get("show_prompt", False) and st.session_state.get("current_section") == f"Rearview Mirror {i}":
                display_prompt_expander(f"rearview_{i}")
                if st.button("Close Prompt", key=f"close_prompt_rearview_{i}"):
                    st.session_state.show_prompt = False
                    st.rerun()

        # Dashboard Data Section
        st.subheader("Dashboard Data")
        dashboard_urls, dashboard_notes, dashboard_prompt = section_input_form(
            "Dashboard Data",
            "dashboard_urls",
            "dashboard_notes",
            "dashboard_prompt",
            DEFAULT_PROMPTS["dashboard"]
        )
        
        st.markdown('<div class="section-controls-row">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="small")
        with col1:
            if st.button("🔄 Gen", key="generate_dashboard", help="Generate section"):
                with st.spinner("Generating Dashboard section..."):
                    article_text = extract_article_text(dashboard_urls)
                    generated_text = generate_section_content(
                        llm_service=llm_service,
                        section_key="dashboard",
                        article_text=article_text,
                        notes=dashboard_notes,
                        section_prompt=dashboard_prompt,
                        provider=st.session_state.get("selected_provider", "OpenAI"),
                        model=st.session_state.get("selected_model", "gpt-4o"),
                        language=st.session_state.get("language", "English")
                    )
                    
                    if "generated_sections" not in st.session_state:
                        st.session_state.generated_sections = {}
                    
                    st.session_state.generated_sections["Dashboard Data"] = generated_text
                    st.success("Dashboard section generated!")
        
        with col2:
            if st.button("✏️ Edit", key="edit_dashboard", help="Edit section"):
                st.session_state.edit_section = True
                st.session_state.current_section = "Dashboard Data"
        
        with col3:
            if st.button("🗑️ Del", key="delete_dashboard", help="Delete section"):
                if "generated_sections" in st.session_state:
                    st.session_state.generated_sections.pop("Dashboard Data", None)
                st.success("Dashboard section deleted!")
        
        with col4:
            if st.button("🔍 Prm", key="prompt_dashboard", help="Show prompt"):
                st.session_state.show_prompt = True
                st.session_state.current_section = "Dashboard Data"
        
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.get("show_prompt", False) and st.session_state.get("current_section") == "Dashboard Data":
            display_prompt_expander("dashboard")
            if st.button("Close Prompt", key="close_prompt_dashboard"):
                st.session_state.show_prompt = False
                st.rerun()

        # The Next Lane Section
        st.subheader("The Next Lane")
        nextlane_urls, nextlane_notes, nextlane_prompt = section_input_form(
            "The Next Lane",
            "nextlane_urls",
            "nextlane_notes",
            "nextlane_prompt",
            DEFAULT_PROMPTS["nextlane"]
        )
        
        st.markdown('<div class="section-controls-row">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="small")
        with col1:
            if st.button("🔄 Gen", key="generate_nextlane", help="Generate section"):
                with st.spinner("Generating The Next Lane section..."):
                    article_text = extract_article_text(nextlane_urls)
                    generated_text = generate_section_content(
                        llm_service=llm_service,
                        section_key="nextlane",
                        article_text=article_text,
                        notes=nextlane_notes,
                        section_prompt=nextlane_prompt,
                        provider=st.session_state.get("selected_provider", "OpenAI"),
                        model=st.session_state.get("selected_model", "gpt-4o"),
                        language=st.session_state.get("language", "English")
                    )
                    
                    if "generated_sections" not in st.session_state:
                        st.session_state.generated_sections = {}
                    
                    st.session_state.generated_sections["The Next Lane"] = generated_text
                    st.success("The Next Lane section generated!")
        
        with col2:
            if st.button("✏️ Edit", key="edit_nextlane", help="Edit section"):
                st.session_state.edit_section = True
                st.session_state.current_section = "The Next Lane"
        
        with col3:
            if st.button("🗑️ Del", key="delete_nextlane", help="Delete section"):
                if "generated_sections" in st.session_state:
                    st.session_state.generated_sections.pop("The Next Lane", None)
                st.success("The Next Lane section deleted!")
        
        with col4:
            if st.button("🔍 Prm", key="prompt_nextlane", help="Show prompt"):
                st.session_state.show_prompt = True
                st.session_state.current_section = "The Next Lane"
        
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.get("show_prompt", False) and st.session_state.get("current_section") == "The Next Lane":
            display_prompt_expander("nextlane")
            if st.button("Close Prompt", key="close_prompt_nextlane"):
                st.session_state.show_prompt = False
                st.rerun()

    with right_panel:
        st.header("Newsletter Summary")
        # Display language selection
        display_language_indicator()
        
        # Display completion status at the top
        if "generated_sections" in st.session_state:
            # Calculate sections list
            sections = ["Windshield View"]
            for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                sections.append(f"Rearview Mirror {i}")
            sections.extend(["Dashboard Data", "The Next Lane"])
            
            show_completion_status(sections, st.session_state.generated_sections)
        
        st.markdown("This panel displays the generated sections in fixed order. If a section has not been generated yet, a placeholder is shown.")
        
        def display_section(title, content):
            st.markdown(f"### {title}")
            st.write(content if content else "Not generated yet.")
        
        # Display all sections in the right panel
        if "generated_sections" in st.session_state:
            display_section("Windshield View", st.session_state.generated_sections.get("Windshield View", ""))
            for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                display_section(f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", ""))
            display_section("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", ""))
            display_section("The Next Lane", st.session_state.generated_sections.get("The Next Lane", ""))