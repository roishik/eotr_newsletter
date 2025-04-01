import streamlit as st
from typing import Dict, Callable

class KeyboardShortcuts:
    """Manages keyboard shortcuts for the application."""
    
    def __init__(self):
        self.shortcuts: Dict[str, Callable] = {}
        self._setup_default_shortcuts()
    
    def _setup_default_shortcuts(self):
        """Setup default keyboard shortcuts."""
        self.shortcuts = {
            "ctrl+s": self._save_draft,
            "ctrl+o": self._open_draft,
            "ctrl+n": self._new_draft,
            "ctrl+g": self._generate_section,
            "ctrl+e": self._edit_section,
            "ctrl+p": self._preview_newsletter,
            "ctrl+1": lambda: self._switch_section("Windshield View"),
            "ctrl+2": lambda: self._switch_section("Dashboard Data"),
            "ctrl+3": lambda: self._switch_section("The Next Lane"),
            "ctrl+4": lambda: self._switch_section("Rearview Mirror 1"),
            "ctrl+5": lambda: self._switch_section("Rearview Mirror 2"),
            "ctrl+6": lambda: self._switch_section("Rearview Mirror 3"),
            "ctrl+d": self._toggle_dark_mode,
            "ctrl+l": self._toggle_language,
            "ctrl+h": self._show_help
        }
    
    def register_shortcut(self, key: str, callback: Callable):
        """Register a new keyboard shortcut."""
        self.shortcuts[key] = callback
    
    def _save_draft(self):
        """Save current draft."""
        if "save_draft" in st.session_state:
            st.session_state.save_draft()
    
    def _open_draft(self):
        """Open draft dialog."""
        st.session_state.show_draft_dialog = True
    
    def _new_draft(self):
        """Create new draft."""
        st.session_state.clear_draft = True
    
    def _generate_section(self):
        """Generate current section."""
        if "current_section" in st.session_state:
            st.session_state.generate_section = True
    
    def _edit_section(self):
        """Edit current section."""
        if "current_section" in st.session_state:
            st.session_state.edit_section = True
    
    def _preview_newsletter(self):
        """Preview newsletter."""
        st.session_state.preview_newsletter = True
    
    def _switch_section(self, section: str):
        """Switch to specified section."""
        st.session_state.current_section = section
    
    def _toggle_dark_mode(self):
        """Toggle dark mode."""
        current_theme = st.session_state.get("theme", "Light")
        st.session_state.theme = "Dark" if current_theme == "Light" else "Light"
    
    def _toggle_language(self):
        """Toggle language."""
        current_lang = st.session_state.get("language", "English")
        st.session_state.language = "Hebrew" if current_lang == "English" else "English"
    
    def _show_help(self):
        """Show keyboard shortcuts help."""
        st.session_state.show_shortcuts_help = True

def add_keyboard_shortcuts():
    """Add keyboard shortcuts to the application."""
    shortcuts = KeyboardShortcuts()
    
    # Add keyboard shortcuts help button
    if st.sidebar.button("⌨️ Keyboard Shortcuts"):
        st.session_state.show_shortcuts_help = True
    
    # Show shortcuts help dialog
    if st.session_state.get("show_shortcuts_help", False):
        with st.sidebar.expander("Keyboard Shortcuts", expanded=True):
            st.markdown("""
            ### Navigation
            - `Ctrl + 1`: Windshield View
            - `Ctrl + 2`: Dashboard Data
            - `Ctrl + 3`: The Next Lane
            - `Ctrl + 4-6`: Rearview Mirror sections
            
            ### Actions
            - `Ctrl + S`: Save Draft
            - `Ctrl + O`: Open Draft
            - `Ctrl + N`: New Draft
            - `Ctrl + G`: Generate Section
            - `Ctrl + E`: Edit Section
            - `Ctrl + P`: Preview Newsletter
            
            ### Settings
            - `Ctrl + D`: Toggle Dark Mode
            - `Ctrl + L`: Toggle Language
            - `Ctrl + H`: Show this help
            """)
            if st.button("Close Help"):
                st.session_state.show_shortcuts_help = False

def add_logo_and_banner(title="Mobileye Newsletter Generator", subtitle="Generate professional newsletters with AI assistance"):
    """Renders the application header with logo and banner."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(to right, #2e6c80, #5F9EA0);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            color: white;
        ">
            <div style="flex: 0 0 50px;">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="white"/>
                    <path d="M2 17L12 22L22 17" fill="white"/>
                    <path d="M2 12L12 17L22 12" fill="white"/>
                </svg>
            </div>
            <div style="flex: 1; margin-left: 15px;">
                <h1 style="margin: 0; font-size: 1.8rem; color: white;">{title}</h1>
                <p style="margin: 0; opacity: 0.8;">{subtitle}</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

def card(title, content, key=None):
    """Create a card-like container with a title and content."""
    is_dark = st.session_state.get('theme', 'Light') == 'Dark'
    
    bg_color = '#3c4043' if is_dark else 'white'
    title_color = '#8ab4f8' if is_dark else '#2e6c80'
    border_color = '#5f6368' if is_dark else '#e6e6e6'
    
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: {title_color};
            margin-top: 0;
            font-size: 1.2rem;
            border-bottom: 1px solid {border_color};
            padding-bottom: 8px;
        ">{title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

def loading_animation():
    """Display a loading spinner animation."""
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #5F9EA0;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
    </div>
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

def show_completion_status(sections, generated_sections):
    """Display newsletter completion status with progress bar."""
    completed_sections = [section for section in sections 
                        if section in generated_sections]
    
    completion_percentage = int(len(completed_sections) / len(sections) * 100) if sections else 0
    
    # Color based on completion
    if completion_percentage < 30:
        color = "#dc3545"  # Red
    elif completion_percentage < 70:
        color = "#ffc107"  # Yellow
    else:
        color = "#28a745"  # Green
    
    # Display the progress bar
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 5px;">Newsletter Completion: {completion_percentage}%</h4>
        <div style="
            background-color: #e9ecef;
            border-radius: 4px;
            height: 10px;
            width: 100%;
        ">
            <div style="
                background-color: {color};
                width: {completion_percentage}%;
                height: 100%;
                border-radius: 4px;
                transition: width 0.5s ease;
            "></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create horizontal layout using Streamlit columns
    cols = st.columns(len(sections))
    
    for i, (col, section) in enumerate(zip(cols, sections)):
        with col:
            is_complete = section in generated_sections
            st.markdown(f"{'✅' if is_complete else '⭕'} {section}")
    
    # Close the div for the progress bar
    st.markdown("</div>", unsafe_allow_html=True)

def section_input_form(section_name, urls_key, notes_key, prompt_key, default_prompt):
    """Render a standard section input form."""
    st.subheader(section_name)
    urls = st.text_input(
        "Enter article URLs (separated by ';;')",
        value=st.session_state.get(urls_key, ""),
        key=urls_key
    )
    notes = st.text_area(
        "Notes",
        value=st.session_state.get(notes_key, ""),
        key=notes_key,
        height=100
    )
    prompt = st.text_area(
        "Section Prompt",
        value=st.session_state.get(prompt_key, default_prompt),
        key=prompt_key,
        height=100
    )
    return urls, notes, prompt

def display_language_indicator():
    """Display the current language selection."""
    selected_language = st.session_state.get("language", "English")
    language_indicator = "🇺🇸 English" if selected_language == "English" else "🇮🇱 עברית"
    st.info(f"Selected Language: {language_indicator}", icon="🌐")

def add_section_controls(section_name: str, section_data: Dict):
    """Add controls for managing a section."""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Generate", key=f"generate_{section_name}"):
            st.session_state.generate_section = True
            st.session_state.current_section = section_name
    
    with col2:
        if st.button("✏️ Edit", key=f"edit_{section_name}"):
            st.session_state.edit_section = True
            st.session_state.current_section = section_name
    
    with col3:
        if st.button("🗑️ Delete", key=f"delete_{section_name}"):
            st.session_state.delete_section = True
            st.session_state.current_section = section_name
    
    # Add drag handle for reordering
    st.markdown(f"""
        <div class="drag-handle" data-section="{section_name}">
            <i class="fas fa-grip-vertical"></i>
        </div>
    """, unsafe_allow_html=True)

def add_drag_drop_support():
    """Add drag-and-drop support for reordering sections."""
    st.markdown("""
        <style>
            .drag-handle {
                cursor: move;
                padding: 5px;
                color: #666;
                display: inline-block;
            }
            .drag-handle:hover {
                color: #000;
            }
            .dragging {
                opacity: 0.5;
                background: #f0f0f0;
            }
            .drag-over {
                border-top: 2px solid #007bff;
            }
        </style>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const dragHandles = document.querySelectorAll('.drag-handle');
                let draggedSection = null;
                
                dragHandles.forEach(handle => {
                    handle.addEventListener('dragstart', function(e) {
                        draggedSection = this.closest('.section-container');
                        draggedSection.classList.add('dragging');
                    });
                    
                    handle.addEventListener('dragend', function(e) {
                        draggedSection.classList.remove('dragging');
                        draggedSection = null;
                    });
                });
                
                const sections = document.querySelectorAll('.section-container');
                sections.forEach(section => {
                    section.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        if (this !== draggedSection) {
                            this.classList.add('drag-over');
                        }
                    });
                    
                    section.addEventListener('dragleave', function(e) {
                        this.classList.remove('drag-over');
                    });
                    
                    section.addEventListener('drop', function(e) {
                        e.preventDefault();
                        this.classList.remove('drag-over');
                        
                        if (this !== draggedSection) {
                            const sections = Array.from(document.querySelectorAll('.section-container'));
                            const fromIndex = sections.indexOf(draggedSection);
                            const toIndex = sections.indexOf(this);
                            
                            // Update section order in session state
                            const sectionOrder = st.session_state.section_order || [];
                            const section = sectionOrder[fromIndex];
                            sectionOrder.splice(fromIndex, 1);
                            sectionOrder.splice(toIndex, 0, section);
                            st.session_state.section_order = sectionOrder;
                            
                            // Reorder sections in DOM
                            if (fromIndex < toIndex) {
                                this.parentNode.insertBefore(draggedSection, this.nextSibling);
                            } else {
                                this.parentNode.insertBefore(draggedSection, this);
                            }
                        }
                    });
                });
            });
        </script>
    """, unsafe_allow_html=True)

def render_section(section_name: str, section_data: Dict):
    """Render a section with drag-and-drop support."""
    st.markdown(f"""
        <div class="section-container" draggable="true">
            <h3>{section_name}</h3>
            <div class="section-content">
                {section_data.get('content', '')}
            </div>
    """, unsafe_allow_html=True)
    
    add_section_controls(section_name, section_data)
    
    st.markdown("</div>", unsafe_allow_html=True)