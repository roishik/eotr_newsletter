import streamlit as st
from utils.content_utils import (
    edit_section_content, 
    generate_newsletter_html,
    render_newsletter_preview
)
from services.llm_service import LLMService

def render_edit_view(llm_service: LLMService):
    """
    Render the Edit Mode view with enhanced context for AI editing.
    
    Args:
        llm_service: Instance of LLMService for content editing
    """
    st.header("Newsletter Edit Mode")
    st.markdown("""
    <div style="
        background-color: #f8f9fa;
        border-left: 4px solid #5F9EA0;
        padding: 10px 15px;
        margin-bottom: 20px;
        border-radius: 4px;
    ">
        <h4 style="margin-top: 0; color: #2e6c80;">📝 Edit Mode</h4>
        <p>In this mode, you can review and edit each section of your newsletter, then ask the AI to refine it based on your instructions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if any sections have been generated
    if not st.session_state.get("generated_sections", {}):
        st.warning("No sections have been generated yet. Please switch to Generate Mode first to create content.")
        if st.button("Switch to Generate Mode"):
            st.session_state.edit_mode = False
            st.rerun()
    else:
        # Layout for edit mode
        sections = []
        sections.append("Windshield View")
        for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
            sections.append(f"Rearview Mirror {i}")
        sections.append("Dashboard Data")
        sections.append("The Next Lane")
        
        # Setup three-column layout as per requirements
        selected_section = st.selectbox("Select section to edit", sections)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("Original Content")
            original_text = st.session_state.get("generated_sections", {}).get(selected_section, "")
            if original_text:
                # Use text area to allow manual edits
                edited_text = st.text_area(
                    "You can also edit directly:",
                    value=original_text,
                    height=300,
                    key=f"manual_edit_{selected_section}"
                )
                # Store manual edits in session state
                if edited_text != original_text:
                    if "edited_sections" not in st.session_state:
                        st.session_state.edited_sections = {}
                    st.session_state.edited_sections[selected_section] = edited_text
            else:
                st.info(f"No content has been generated for {selected_section} yet.")
        
        with col2:
            st.subheader("Edit Instructions")
            edit_prompt = st.text_area(
                "Enter your editing instructions",
                value="",
                height=150,
                placeholder="e.g., Make it shorter, Use more technical language, Add more industry context, etc.",
                key=f"edit_prompt_{selected_section}"
            )
            
            if st.button("Apply AI Edit"):
                if not original_text:
                    st.error("Cannot edit empty content. Please generate content first.")
                elif not edit_prompt:
                    st.error("Please provide editing instructions.")
                else:
                    with st.spinner("Applying edits..."):
                        # Get the latest version (either original or manually edited)
                        if "edited_sections" not in st.session_state:
                            st.session_state.edited_sections = {}
                            
                        text_to_edit = st.session_state.edited_sections.get(selected_section, original_text)
                        
                        # Gather context information for the selected section
                        # First, determine which section we're editing to get the right context
                        section_type = ""
                        section_index = 0
                        
                        if selected_section == "Windshield View":
                            section_type = "windshield"
                        elif selected_section.startswith("Rearview Mirror "):
                            section_type = "rearview"
                            # Extract the index from "Rearview Mirror X"
                            section_index = int(selected_section.split(" ")[-1])
                        elif selected_section == "Dashboard Data":
                            section_type = "dashboard"
                        elif selected_section == "The Next Lane":
                            section_type = "nextlane"
                        
                        # Get the URL sources for this section
                        url_key = f"{section_type}_urls"
                        if section_type == "rearview":
                            url_key = f"rearview_urls_{section_index}"
                            
                        # Get notes for this section
                        notes_key = f"{section_type}_notes"
                        if section_type == "rearview":
                            notes_key = f"rearview_notes_{section_index}"
                            
                        # Get section-specific prompt
                        prompt_key = f"{section_type}_prompt"
                        if section_type == "rearview":
                            prompt_key = f"rearview_prompt_{section_index}"
                        
                        # Extract article text from URLs
                        from utils.content_utils import extract_article_text
                        urls = st.session_state.get(url_key, "")
                        article_text = extract_article_text(urls) if urls else ""
                        
                        # Get user notes
                        notes = st.session_state.get(notes_key, "")
                        
                        # Get section prompt
                        section_prompt = st.session_state.get(prompt_key, "")
                        
                        # Get overall prompt
                        overall_prompt = st.session_state.get("overall_prompt", "")
                        
                        # Call the enhanced edit_section_content function with all context
                        edited_text = edit_section_content(
                            llm_service=llm_service,
                            section_key=selected_section,
                            original_text=text_to_edit,
                            edit_prompt=edit_prompt,
                            provider=st.session_state.get("selected_provider", "OpenAI"),
                            model=st.session_state.get("selected_model", "gpt-4o"),
                            article_text=article_text,
                            notes=notes,
                            section_prompt=section_prompt,
                            overall_prompt=overall_prompt
                        )
                        
                        st.session_state.edited_sections[selected_section] = edited_text
                        st.success("Edit applied!")
        
        with col3:
            st.subheader("Edited Result")
            edited_text = st.session_state.get("edited_sections", {}).get(selected_section, "")
            if edited_text:
                st.write(edited_text)
                if st.button("Keep this edit"):
                    # Update the generated_sections with the edited version
                    if "generated_sections" not in st.session_state:
                        st.session_state.generated_sections = {}
                        
                    st.session_state.generated_sections[selected_section] = edited_text
                    
                    # Clear the edited version from edited_sections since it's now the official version
                    # This ensures the manual edit field will show the updated content
                    if selected_section in st.session_state.edited_sections:
                        del st.session_state.edited_sections[selected_section]
                        
                    st.success(f"Updated {selected_section} with edited version!")
                    
                    # Force a rerun to refresh the UI with updated content
                    st.rerun()
            else:
                st.info("No edits applied yet.")
        
        # Button to generate final newsletter with edits
        st.markdown("---")
        if st.button("Generate Final Newsletter"):
            with st.spinner("Assembling final newsletter..."):
                # First update any edited sections into the generated_sections
                if "generated_sections" not in st.session_state:
                    st.session_state.generated_sections = {}
                
                for section, content in st.session_state.get("edited_sections", {}).items():
                    if content:  # Only update if there's content
                        st.session_state.generated_sections[section] = content
                
                # Then generate the newsletter with the updated sections
                sections_content = ""
                # Fixed order as before
                section_pairs = []
                section_pairs.append(("Windshield View", st.session_state.generated_sections.get("Windshield View", "Not generated yet.")))
                for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                    section_pairs.append((f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", "Not generated yet.")))
                section_pairs.append(("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", "Not generated yet.")))
                section_pairs.append(("The Next Lane", st.session_state.generated_sections.get("The Next Lane", "Not generated yet.")))
                
                for title, content in section_pairs:
                    sections_content += f"""
                    <div class="section">
                        <h2>{title}</h2>
                        <p>{content}</p>
                    </div>
                    """
                
                newsletter_html = generate_newsletter_html(
                    sections_content, 
                    theme=st.session_state.get('theme', 'Light'),
                    language=st.session_state.get('language', 'English')
                )
                
                st.success("Final Newsletter Created!")
                render_newsletter_preview(newsletter_html)
                
                st.download_button(
                    "Download Final Newsletter",
                    data=newsletter_html,
                    file_name=f"final_newsletter_{st.session_state.get('timestamp', '')}",
                    mime="text/html"
                )
        
        # Option to return to generation mode
        if st.button("Return to Generate Mode"):
            st.session_state.edit_mode = False
            st.rerun()