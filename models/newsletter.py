from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime
import json
import os

@dataclass
class MediaContent:
    """Data structure for rich media content."""
    type: str  # "image", "video", "chart", "interactive"
    url: str
    caption: str = ""
    alt_text: str = ""
    width: int = 800
    height: int = 600
    position: str = "center"  # "left", "center", "right"
    metadata: Dict = field(default_factory=dict)

@dataclass
class SectionData:
    """Data structure for a newsletter section."""
    urls: str = ""
    notes: str = ""
    prompt: str = ""
    content: str = ""
    media_content: List[MediaContent] = field(default_factory=list)
    
    def is_generated(self) -> bool:
        """Check if this section has generated content."""
        return bool(self.content.strip())
    
    def add_media(self, media: MediaContent) -> None:
        """Add media content to the section."""
        self.media_content.append(media)
    
    def remove_media(self, index: int) -> None:
        """Remove media content from the section."""
        if 0 <= index < len(self.media_content):
            self.media_content.pop(index)
    
    def reorder_media(self, old_index: int, new_index: int) -> None:
        """Reorder media content in the section."""
        if 0 <= old_index < len(self.media_content) and 0 <= new_index < len(self.media_content):
            media = self.media_content.pop(old_index)
            self.media_content.insert(new_index, media)

@dataclass
class RearviewSectionData(SectionData):
    """Data structure for a Rearview Mirror section."""
    index: int = 1

@dataclass
class NewsletterAnalytics:
    """Data structure for newsletter analytics."""
    views: int = 0
    unique_views: int = 0
    engagement_time: float = 0.0
    bounce_rate: float = 0.0
    click_through_rate: float = 0.0
    social_shares: Dict[str, int] = field(default_factory=dict)
    section_engagement: Dict[str, float] = field(default_factory=dict)
    reader_feedback: List[Dict] = field(default_factory=list)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Newsletter:
    """Data structure for the entire newsletter."""
    windshield: SectionData = field(default_factory=SectionData)
    rearview_sections: Dict[int, RearviewSectionData] = field(default_factory=dict)
    dashboard: SectionData = field(default_factory=SectionData)
    nextlane: SectionData = field(default_factory=SectionData)
    
    # General newsletter settings
    overall_prompt: str = ""
    num_rearview: int = 3
    edited_sections: Dict[str, str] = field(default_factory=dict)
    selected_provider: str = "OpenAI"
    selected_model: str = "gpt-4o"
    language: str = "English"
    theme: str = "Light"
    
    # Version control
    version: int = 1
    parent_version: Optional[int] = None
    version_history: List[Dict] = field(default_factory=list)
    last_modified: datetime.datetime = field(default_factory=datetime.datetime.now)
    modified_by: str = "system"
    
    # Analytics
    analytics: NewsletterAnalytics = field(default_factory=NewsletterAnalytics)
    
    def __post_init__(self):
        """Initialize rearview sections if needed."""
        # Ensure we have the correct number of rearview sections
        for i in range(1, self.num_rearview + 1):
            if i not in self.rearview_sections:
                self.rearview_sections[i] = RearviewSectionData(index=i)
    
    def get_section_names(self) -> List[str]:
        """Get all section names in proper order."""
        sections = ["Windshield View"]
        for i in range(1, self.num_rearview + 1):
            sections.append(f"Rearview Mirror {i}")
        sections.extend(["Dashboard Data", "The Next Lane"])
        return sections
    
    def get_generated_sections(self) -> Dict[str, str]:
        """Get a dictionary of all generated sections."""
        sections = {}
        if self.windshield.is_generated():
            sections["Windshield View"] = self.windshield.content
        
        for i, section in self.rearview_sections.items():
            if section.is_generated():
                sections[f"Rearview Mirror {i}"] = section.content
        
        if self.dashboard.is_generated():
            sections["Dashboard Data"] = self.dashboard.content
        
        if self.nextlane.is_generated():
            sections["The Next Lane"] = self.nextlane.content
        
        return sections
    
    def get_completion_percentage(self) -> int:
        """Calculate the completion percentage of the newsletter."""
        total_sections = 2 + len(self.rearview_sections)  # Windshield + Dashboard + NextLane + Rearviews
        completed = 0
        
        if self.windshield.is_generated():
            completed += 1
        
        for section in self.rearview_sections.values():
            if section.is_generated():
                completed += 1
        
        if self.dashboard.is_generated():
            completed += 1
        
        if self.nextlane.is_generated():
            completed += 1
        
        return int((completed / total_sections) * 100) if total_sections > 0 else 0
    
    def to_dict(self) -> dict:
        """Convert the newsletter to a dictionary for saving."""
        data = {
            "overall_prompt": self.overall_prompt,
            "windshield_urls": self.windshield.urls,
            "windshield_notes": self.windshield.notes,
            "windshield_prompt": self.windshield.prompt,
            "num_rearview": self.num_rearview,
            "dashboard_urls": self.dashboard.urls,
            "dashboard_notes": self.dashboard.notes,
            "dashboard_prompt": self.dashboard.prompt,
            "nextlane_urls": self.nextlane.urls,
            "nextlane_notes": self.nextlane.notes,
            "nextlane_prompt": self.nextlane.prompt,
            "generated_sections": self.get_generated_sections(),
            "edited_sections": self.edited_sections,
            "selected_provider": self.selected_provider,
            "selected_model": self.selected_model,
            "language": self.language,
            "theme": self.theme
        }
        
        # Add rearview sections
        for i, section in self.rearview_sections.items():
            data[f"rearview_urls_{i}"] = section.urls
            data[f"rearview_notes_{i}"] = section.notes
            data[f"rearview_prompt_{i}"] = section.prompt
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Newsletter':
        """Create a Newsletter instance from a dictionary."""
        newsletter = cls(
            overall_prompt=data.get("overall_prompt", ""),
            num_rearview=data.get("num_rearview", 3),
            edited_sections=data.get("edited_sections", {}),
            selected_provider=data.get("selected_provider", "OpenAI"),
            selected_model=data.get("selected_model", "gpt-4o"),
            language=data.get("language", "English"),
            theme=data.get("theme", "Light")
        )
        
        # Load main sections
        newsletter.windshield = SectionData(
            urls=data.get("windshield_urls", ""),
            notes=data.get("windshield_notes", ""),
            prompt=data.get("windshield_prompt", ""),
            content=data.get("generated_sections", {}).get("Windshield View", "")
        )
        
        newsletter.dashboard = SectionData(
            urls=data.get("dashboard_urls", ""),
            notes=data.get("dashboard_notes", ""),
            prompt=data.get("dashboard_prompt", ""),
            content=data.get("generated_sections", {}).get("Dashboard Data", "")
        )
        
        newsletter.nextlane = SectionData(
            urls=data.get("nextlane_urls", ""),
            notes=data.get("nextlane_notes", ""),
            prompt=data.get("nextlane_prompt", ""),
            content=data.get("generated_sections", {}).get("The Next Lane", "")
        )
        
        # Load rearview sections
        for i in range(1, newsletter.num_rearview + 1):
            newsletter.rearview_sections[i] = RearviewSectionData(
                index=i,
                urls=data.get(f"rearview_urls_{i}", ""),
                notes=data.get(f"rearview_notes_{i}", ""),
                prompt=data.get(f"rearview_prompt_{i}", ""),
                content=data.get("generated_sections", {}).get(f"Rearview Mirror {i}", "")
            )
        
        return newsletter

    def save(self, drafts_dir="drafts") -> str:
        """Save the newsletter as a draft file."""
        os.makedirs(drafts_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{drafts_dir}/draft_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
        
        return filename
    
    @classmethod
    def load(cls, filename: str) -> 'Newsletter':
        """Load a newsletter from a draft file."""
        with open(filename, "r") as f:
            data = json.load(f)
        
        return cls.from_dict(data)

    def create_new_version(self, user: str = "system") -> 'Newsletter':
        """Create a new version of the newsletter."""
        # Save current state to history
        self.version_history.append({
            "version": self.version,
            "timestamp": self.last_modified,
            "modified_by": self.modified_by,
            "data": self.to_dict()
        })
        
        # Create new version
        new_version = Newsletter(
            windshield=self.windshield,
            rearview_sections=self.rearview_sections,
            dashboard=self.dashboard,
            nextlane=self.nextlane,
            overall_prompt=self.overall_prompt,
            num_rearview=self.num_rearview,
            edited_sections=self.edited_sections,
            selected_provider=self.selected_provider,
            selected_model=self.selected_model,
            language=self.language,
            theme=self.theme,
            version=self.version + 1,
            parent_version=self.version,
            version_history=self.version_history,
            last_modified=datetime.datetime.now(),
            modified_by=user
        )
        
        return new_version
    
    def get_version_history(self) -> List[Dict]:
        """Get the version history of the newsletter."""
        return self.version_history
    
    def restore_version(self, version: int) -> Optional['Newsletter']:
        """Restore a specific version of the newsletter."""
        for history_entry in self.version_history:
            if history_entry["version"] == version:
                return Newsletter.from_dict(history_entry["data"])
        return None
    
    def get_version_diff(self, version1: int, version2: int) -> Dict[str, List[str]]:
        """Get the differences between two versions."""
        v1_data = None
        v2_data = None
        
        for history_entry in self.version_history:
            if history_entry["version"] == version1:
                v1_data = history_entry["data"]
            elif history_entry["version"] == version2:
                v2_data = history_entry["data"]
        
        if not v1_data or not v2_data:
            return {}
        
        diff = {}
        for section in ["Windshield View", "Dashboard Data", "The Next Lane"]:
            v1_content = v1_data.get("generated_sections", {}).get(section, "")
            v2_content = v2_data.get("generated_sections", {}).get(section, "")
            if v1_content != v2_content:
                diff[section] = [v1_content, v2_content]
        
        for i in range(1, max(v1_data.get("num_rearview", 3), v2_data.get("num_rearview", 3)) + 1):
            section = f"Rearview Mirror {i}"
            v1_content = v1_data.get("generated_sections", {}).get(section, "")
            v2_content = v2_data.get("generated_sections", {}).get(section, "")
            if v1_content != v2_content:
                diff[section] = [v1_content, v2_content]
        
        return diff

    def update_analytics(self, **kwargs) -> None:
        """Update newsletter analytics."""
        for key, value in kwargs.items():
            if hasattr(self.analytics, key):
                setattr(self.analytics, key, value)
        self.analytics.last_updated = datetime.datetime.now()
    
    def get_engagement_score(self) -> float:
        """Calculate overall engagement score."""
        weights = {
            "views": 0.2,
            "unique_views": 0.2,
            "engagement_time": 0.2,
            "bounce_rate": 0.2,
            "click_through_rate": 0.2
        }
        
        # Normalize values
        max_views = max(1000, self.analytics.views)
        max_unique_views = max(800, self.analytics.unique_views)
        max_engagement_time = max(300, self.analytics.engagement_time)
        
        normalized_values = {
            "views": self.analytics.views / max_views,
            "unique_views": self.analytics.unique_views / max_unique_views,
            "engagement_time": self.analytics.engagement_time / max_engagement_time,
            "bounce_rate": 1 - (self.analytics.bounce_rate / 100),  # Invert bounce rate
            "click_through_rate": self.analytics.click_through_rate / 100
        }
        
        # Calculate weighted score
        score = sum(weights[k] * normalized_values[k] for k in weights)
        return round(score * 100, 2)  # Convert to percentage
    
    def get_section_engagement(self) -> Dict[str, float]:
        """Get engagement metrics for each section."""
        return self.analytics.section_engagement
    
    def add_reader_feedback(self, feedback: Dict) -> None:
        """Add reader feedback to analytics."""
        feedback["timestamp"] = datetime.datetime.now()
        self.analytics.reader_feedback.append(feedback)
    
    def get_feedback_summary(self) -> Dict[str, int]:
        """Get summary of reader feedback."""
        summary = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        for feedback in self.analytics.reader_feedback:
            sentiment = feedback.get("sentiment", "neutral")
            summary[sentiment] += 1
        
        return summary

    def add_articles_to_section(self, section_name: str, articles: List[Dict]) -> None:
        """Add articles to a specific section."""
        # Convert articles to URLs string
        urls = "\n".join([article["url"] for article in articles])
        
        # Add to appropriate section
        if section_name == "Windshield View":
            self.windshield.urls = urls
        elif section_name == "Dashboard Data":
            self.dashboard.urls = urls
        elif section_name == "The Next Lane":
            self.nextlane.urls = urls
        elif section_name.startswith("Rearview Mirror"):
            try:
                index = int(section_name.split()[-1])
                if index in self.rearview_sections:
                    self.rearview_sections[index].urls = urls
            except ValueError:
                pass