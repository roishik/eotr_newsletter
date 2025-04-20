import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import streamlit as st
from datetime import datetime

class CollaborationManager:
    """Manages real-time collaboration features."""
    
    def __init__(self, collaboration_dir: str = "collaboration"):
        self.collaboration_dir = Path(collaboration_dir)
        self.collaboration_dir.mkdir(parents=True, exist_ok=True)
        self.active_users_file = self.collaboration_dir / "active_users.json"
        self.changes_file = self.collaboration_dir / "changes.json"
        self._load_state()
    
    def _load_state(self):
        """Load collaboration state from files."""
        if self.active_users_file.exists():
            with open(self.active_users_file, "r") as f:
                self.active_users = json.load(f)
        else:
            self.active_users = {}
        
        if self.changes_file.exists():
            with open(self.changes_file, "r") as f:
                self.changes = json.load(f)
        else:
            self.changes = []
    
    def _save_state(self):
        """Save collaboration state to files."""
        with open(self.active_users_file, "w") as f:
            json.dump(self.active_users, f)
        with open(self.changes_file, "w") as f:
            json.dump(self.changes, f)
    
    def join_session(self, user_id: str, user_name: str, newsletter_id: str):
        """Join a collaboration session."""
        if newsletter_id not in self.active_users:
            self.active_users[newsletter_id] = {}
        
        self.active_users[newsletter_id][user_id] = {
            "name": user_name,
            "last_active": time.time(),
            "cursor_position": None,
            "selected_section": None
        }
        self._save_state()
    
    def leave_session(self, user_id: str, newsletter_id: str):
        """Leave a collaboration session."""
        if newsletter_id in self.active_users and user_id in self.active_users[newsletter_id]:
            del self.active_users[newsletter_id][user_id]
            if not self.active_users[newsletter_id]:
                del self.active_users[newsletter_id]
            self._save_state()
    
    def update_user_activity(self, user_id: str, newsletter_id: str, cursor_position: Optional[Dict] = None, selected_section: Optional[str] = None):
        """Update user's activity in the session."""
        if newsletter_id in self.active_users and user_id in self.active_users[newsletter_id]:
            self.active_users[newsletter_id][user_id].update({
                "last_active": time.time(),
                "cursor_position": cursor_position,
                "selected_section": selected_section
            })
            self._save_state()
    
    def get_active_users(self, newsletter_id: str) -> List[Dict[str, Any]]:
        """Get list of active users in a session."""
        if newsletter_id in self.active_users:
            return [
                {"id": uid, **user_data}
                for uid, user_data in self.active_users[newsletter_id].items()
            ]
        return []
    
    def record_change(self, newsletter_id: str, user_id: str, change_type: str, section: str, content: Any):
        """Record a change made by a user."""
        change = {
            "timestamp": time.time(),
            "newsletter_id": newsletter_id,
            "user_id": user_id,
            "type": change_type,
            "section": section,
            "content": content
        }
        self.changes.append(change)
        self._save_state()
    
    def get_recent_changes(self, newsletter_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent changes for a newsletter."""
        return [
            change for change in sorted(self.changes, key=lambda x: x["timestamp"], reverse=True)
            if change["newsletter_id"] == newsletter_id
        ][:limit]

def setup_collaboration():
    """Setup collaboration features in the Streamlit app."""
    if "collaboration" not in st.session_state:
        st.session_state.collaboration = CollaborationManager()
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = f"Anonymous User {st.session_state.user_id[-4:]}"
    
    # Add collaboration panel to sidebar
    with st.sidebar.expander("Collaboration", expanded=False):
        if st.session_state.get("newsletter_id"):
            # Join/leave session
            if st.button("Join Session"):
                st.session_state.collaboration.join_session(
                    st.session_state.user_id,
                    st.session_state.user_name,
                    st.session_state.newsletter_id
                )
                st.success("Joined collaboration session!")
            
            if st.button("Leave Session"):
                st.session_state.collaboration.leave_session(
                    st.session_state.user_id,
                    st.session_state.newsletter_id
                )
                st.success("Left collaboration session!")
            
            # Show active users
            st.subheader("Active Users")
            active_users = st.session_state.collaboration.get_active_users(st.session_state.newsletter_id)
            for user in active_users:
                st.markdown(f"- {user['name']}")
            
            # Show recent changes
            st.subheader("Recent Changes")
            changes = st.session_state.collaboration.get_recent_changes(st.session_state.newsletter_id)
            for change in changes:
                timestamp = datetime.fromtimestamp(change["timestamp"]).strftime("%H:%M:%S")
                st.markdown(f"**{timestamp}** - {change['user_id']} modified {change['section']}")
    
    # Update user activity
    if st.session_state.get("newsletter_id"):
        st.session_state.collaboration.update_user_activity(
            st.session_state.user_id,
            st.session_state.newsletter_id,
            cursor_position={"section": st.session_state.get("current_section")},
            selected_section=st.session_state.get("current_section")
        ) 