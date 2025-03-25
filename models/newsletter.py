from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime
import json
import os

@dataclass
class SectionData:
    """Data structure for a newsletter section."""
    urls: str = ""
    notes: str = ""
    prompt: str = ""
    content: str = ""
    
    def is_generated(self) -> bool:
        """Check if this section has generated content."""
        return bool(self.content.strip())

@dataclass
class RearviewSectionData(SectionData):
    """Data structure for a Rearview Mirror section."""
    index: int = 1

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