import streamlit as st
from config.prompts import DEFAULT_PROMPTS
from ui.components import (
    section_input_form, 
    show_completion_status, 
    loading_animation,
    display_language_indicator
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
        windshield_urls, windshield_notes, windshield_prompt = section_input_form(
            "Windshield View",
            "windshield_urls",
            "windshield_notes",
            "windshield_prompt",
            DEFAULT_PROMPTS["windshield"]
        )
        
        if st.button("Generate Windshield Section"):
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
                
                # Initialize generated_sections if not exists
                if "generated_sections" not in st.session_state:
                    st.session_state.generated_sections = {}
                
                st.session_state.generated_sections["Windshield View"] = generated_text
                st.success("Windshield section generated!")

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
            
            if st.button(f"Generate Rearview {i} Section"):
                with st.spinner(f"Generating Rearview {i} section..."):
                    print(f"\n[Generate View] Generating Rearview Mirror {i}")
                    print(f"[Generate View] Session state keys: {st.session_state.keys()}")
                    print(f"[Generate View] rearview_urls_{i}: {st.session_state.get(f'rearview_urls_{i}', '')}")
                    print(f"[Generate View] rearview_notes_{i}: {st.session_state.get(f'rearview_notes_{i}', '')}")
                    print(f"[Generate View] rearview_prompt_{i}: {st.session_state.get(f'rearview_prompt_{i}', '')}")
                    
                    article_text = extract_article_text(st.session_state[f"rearview_urls_{i}"])
                    generated_text = generate_section_content(
                        llm_service=llm_service,
                        section_key="rearview",
                        article_text=article_text,
                        notes=st.session_state[f"rearview_notes_{i}"],
                        section_prompt=st.session_state[f"rearview_prompt_{i}"],
                        provider=st.session_state.get("selected_provider", "OpenAI"),
                        model=st.session_state.get("selected_model", "gpt-4o"),
                        language=st.session_state.get("language", "English")
                    )
                    
                    # Initialize generated_sections if not exists
                    if "generated_sections" not in st.session_state:
                        st.session_state.generated_sections = {}
                    
                    st.session_state.generated_sections[f"Rearview Mirror {i}"] = generated_text
                    print(f"[Generate View] Generated content length: {len(generated_text)} characters")
                    st.success(f"Rearview {i} section generated!")

        # Dashboard Data Section
        dashboard_urls, dashboard_notes, dashboard_prompt = section_input_form(
            "Dashboard Data",
            "dashboard_urls",
            "dashboard_notes",
            "dashboard_prompt",
            DEFAULT_PROMPTS["dashboard"]
        )
        
        if st.button("Generate Dashboard Section"):
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
                
                # Initialize generated_sections if not exists
                if "generated_sections" not in st.session_state:
                    st.session_state.generated_sections = {}
                
                st.session_state.generated_sections["Dashboard Data"] = generated_text
                st.success("Dashboard section generated!")

        # The Next Lane Section
        nextlane_urls, nextlane_notes, nextlane_prompt = section_input_form(
            "The Next Lane",
            "nextlane_urls",
            "nextlane_notes",
            "nextlane_prompt",
            DEFAULT_PROMPTS["nextlane"]
        )
        
        if st.button("Generate Next Lane Section"):
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
                
                # Initialize generated_sections if not exists
                if "generated_sections" not in st.session_state:
                    st.session_state.generated_sections = {}
                
                st.session_state.generated_sections["The Next Lane"] = generated_text
                st.success("The Next Lane section generated!")

        # Create complete newsletter
        st.markdown("---")
        if st.button("Create Newsletter"):
            with st.spinner("Assembling Newsletter..."):
                sections_content = ""
                # Fixed order: Windshield, Rearview stories, Dashboard, Next Lane
                sections = []
                sections.append(("Windshield View", st.session_state.generated_sections.get("Windshield View", "Not generated yet.")))
                for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                    sections.append((f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", "Not generated yet.")))
                sections.append(("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", "Not generated yet.")))
                sections.append(("The Next Lane", st.session_state.generated_sections.get("The Next Lane", "Not generated yet.")))
                
                for title, content in sections:
                    # Determine text direction based on language
                    dir_attr = 'rtl' if st.session_state.get('language', 'English') == "Hebrew" else 'ltr'
                    sections_content += f"""
                    <div class="section" dir="{dir_attr}">
                        <h2>{title}</h2>
                        <p>{content}</p>
                    </div>
                    """
                
                newsletter_html = generate_newsletter_html(
                    sections_content, 
                    theme=st.session_state.get('theme', 'Light'),
                    language=st.session_state.get('language', 'English')
                )
                
                st.success("Newsletter Created!")
                render_newsletter_preview(newsletter_html)
                
                st.download_button(
                    "Download Newsletter",
                    data=newsletter_html,
                    file_name=f"newsletter_{st.session_state.get('timestamp', '')}",
                    mime="text/html"
                )

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