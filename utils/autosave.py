import time
import json
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st

class AutoSave:
    """Manages automatic saving of newsletter drafts."""
    
    def __init__(self, save_interval: int = 300):  # 5 minutes default
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.autosave_dir = Path("drafts/autosave")
        self.autosave_dir.mkdir(parents=True, exist_ok=True)
    
    def should_save(self) -> bool:
        """Check if it's time to auto-save."""
        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            self.last_save_time = current_time
            return True
        return False
    
    def save_draft(self, newsletter_data: Dict[str, Any], draft_id: Optional[str] = None) -> str:
        """Save the current draft."""
        if draft_id is None:
            draft_id = f"autosave_{int(time.time())}"
        
        save_path = self.autosave_dir / f"{draft_id}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(newsletter_data, f, ensure_ascii=False, indent=2)
        
        return draft_id
    
    def load_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Load a draft by ID."""
        save_path = self.autosave_dir / f"{draft_id}.json"
        if not save_path.exists():
            return None
        
        with open(save_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_drafts(self) -> list[Dict[str, Any]]:
        """List all auto-saved drafts."""
        drafts = []
        for save_file in self.autosave_dir.glob("*.json"):
            try:
                with open(save_file, "r", encoding="utf-8") as f:
                    draft_data = json.load(f)
                    drafts.append({
                        "id": save_file.stem,
                        "timestamp": int(save_file.stem.split("_")[1]),
                        "data": draft_data
                    })
            except Exception as e:
                st.error(f"Error loading draft {save_file.name}: {str(e)}")
        
        return sorted(drafts, key=lambda x: x["timestamp"], reverse=True)
    
    def cleanup_old_drafts(self, max_age_hours: int = 24):
        """Remove drafts older than specified hours."""
        current_time = time.time()
        for save_file in self.autosave_dir.glob("*.json"):
            try:
                timestamp = int(save_file.stem.split("_")[1])
                age_hours = (current_time - timestamp) / 3600
                if age_hours > max_age_hours:
                    save_file.unlink()
            except Exception as e:
                st.error(f"Error cleaning up draft {save_file.name}: {str(e)}")

def setup_autosave():
    """Setup auto-save functionality in the Streamlit app."""
    if "autosave" not in st.session_state:
        st.session_state.autosave = AutoSave()
    
    if "last_modified" not in st.session_state:
        st.session_state.last_modified = time.time()
    
    # Check for unsaved changes
    if st.session_state.get("newsletter_data"):
        current_time = time.time()
        if current_time - st.session_state.last_modified >= 60:  # 1 minute
            st.session_state.last_modified = current_time
            if st.session_state.autosave.should_save():
                draft_id = st.session_state.autosave.save_draft(st.session_state.newsletter_data)
                st.toast(f"Auto-saved draft: {draft_id}", icon="💾")
    
    # Add auto-save settings to sidebar
    with st.sidebar.expander("Auto-save Settings", expanded=False):
        save_interval = st.number_input(
            "Auto-save interval (seconds)",
            min_value=60,
            max_value=3600,
            value=st.session_state.autosave.save_interval,
            step=60
        )
        st.session_state.autosave.save_interval = save_interval
        
        if st.button("View Auto-saved Drafts"):
            st.session_state.show_autosave_drafts = True
    
    # Show auto-saved drafts dialog
    if st.session_state.get("show_autosave_drafts", False):
        with st.sidebar.expander("Auto-saved Drafts", expanded=True):
            drafts = st.session_state.autosave.list_drafts()
            if not drafts:
                st.info("No auto-saved drafts found.")
            else:
                for draft in drafts:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(draft["timestamp"]))
                    if st.button(f"Load draft from {timestamp}", key=f"load_{draft['id']}"):
                        st.session_state.newsletter_data = draft["data"]
                        st.session_state.last_modified = draft["timestamp"]
                        st.success("Draft loaded successfully!")
                        st.session_state.show_autosave_drafts = False
                        st.rerun()
            
            if st.button("Close"):
                st.session_state.show_autosave_drafts = False 