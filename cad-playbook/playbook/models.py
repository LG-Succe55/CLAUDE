"""Data shapes for what the agent extracts from a tutorial."""

from typing import List, Literal

from pydantic import BaseModel, Field

Software = Literal["CATIA 3DEXPERIENCE", "CATIA V5", "Autodesk Alias", "Other"]
Level = Literal["beginner", "intermediate", "advanced"]


class Step(BaseModel):
    order: int = Field(description="1-based position of the step in the workflow")
    action: str = Field(description="What the user does, in one imperative sentence")
    command: str = Field(description="Exact tool/command name as shown in the software, e.g. 'Multi-Sections Surface', 'Skin', 'Align'. Empty if none")
    menu_path: str = Field(description="Where to find the command (app > toolbar/section > command). Empty if not shown")
    settings: str = Field(description="Parameters, options and values used (continuity, degree, spans, tolerances...). Empty if none")
    timestamp_s: float = Field(description="Seconds into the video where this step is shown (page number for written manuals)")
    why: str = Field(description="The reason for the step, if the presenter explains it. Empty otherwise")


class Workflow(BaseModel):
    title: str = Field(description="Short task name, e.g. 'G2 blend between hood and fender'")
    software: Software
    app_or_workbench: str = Field(description="3DEXPERIENCE app (e.g. 'Generative Shape Design', 'ICEM Shape Design', 'Imagine & Shape') or Alias area (e.g. 'Surfaces palette', 'Evaluate'). Empty if unclear")
    vehicle_areas: List[str] = Field(description="Parts of a vehicle this applies to, e.g. 'hood', 'A-pillar', 'wheel arch', 'general surfacing'")
    level: Level
    goal: str = Field(description="What the finished result looks like, one or two sentences")
    start_s: float
    end_s: float
    steps: List[Step]
    tips: List[str] = Field(description="Practical tricks the presenter recommends")
    pitfalls: List[str] = Field(description="Mistakes to avoid or problems the presenter warns about")


class VideoExtraction(BaseModel):
    summary: str = Field(description="Two or three sentences on what the video teaches")
    workflows: List[Workflow]
