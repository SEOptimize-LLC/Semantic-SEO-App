"""Export utilities for Semantic SEO Platform."""

from __future__ import annotations

import json
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import pandas as pd


class ExportHandler:
    """Handle exports to various formats."""
    
    def __init__(self, export_path: Optional[Path] = None):
        """
        Initialize export handler.
        
        Args:
            export_path: Base path for file exports
        """
        if export_path is None:
            export_path = Path(__file__).parent.parent / "data" / "exports"
        
        self.export_path = Path(export_path)
        self.export_path.mkdir(parents=True, exist_ok=True)
    
    def to_json(
        self,
        data: Union[Dict, List],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export data to JSON.
        
        Args:
            data: Data to export
            filename: Optional filename to save to disk
            pretty: Whether to format with indentation
        
        Returns:
            JSON string
        """
        indent = 2 if pretty else None
        json_str = json.dumps(data, indent=indent, default=str)
        
        if filename:
            filepath = self.export_path / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        
        return json_str
    
    def to_csv(
        self,
        data: Union[pd.DataFrame, List[Dict]],
        filename: Optional[str] = None
    ) -> str:
        """
        Export data to CSV.
        
        Args:
            data: DataFrame or list of dicts to export
            filename: Optional filename to save to disk
        
        Returns:
            CSV string
        """
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data
        
        csv_str = df.to_csv(index=False)
        
        if filename:
            filepath = self.export_path / filename
            df.to_csv(filepath, index=False)
        
        return csv_str
    
    def to_excel(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        filename: str
    ) -> bytes:
        """
        Export data to Excel.
        
        Args:
            data: DataFrame or dict of DataFrames (for multiple sheets)
            filename: Filename to save
        
        Returns:
            Excel file bytes
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            if isinstance(data, dict):
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                data.to_excel(writer, sheet_name="Data", index=False)
        
        excel_bytes = output.getvalue()
        
        # Save to file
        filepath = self.export_path / filename
        with open(filepath, "wb") as f:
            f.write(excel_bytes)
        
        return excel_bytes
    
    def to_markdown(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None,
        template: str = "default"
    ) -> str:
        """
        Export data to Markdown.
        
        Args:
            data: Data to export
            filename: Optional filename to save
            template: Markdown template to use
        
        Returns:
            Markdown string
        """
        if template == "content_brief":
            md = self._brief_to_markdown(data)
        elif template == "topical_map":
            md = self._topical_map_to_markdown(data)
        else:
            md = self._default_to_markdown(data)
        
        if filename:
            filepath = self.export_path / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
        
        return md
    
    def _default_to_markdown(self, data: Dict) -> str:
        """Convert generic data to markdown."""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"## {key}")
                for k, v in value.items():
                    lines.append(f"- **{k}**: {v}")
            elif isinstance(value, list):
                lines.append(f"## {key}")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"### {item.get('name', 'Item')}")
                        for k, v in item.items():
                            if k != 'name':
                                lines.append(f"- **{k}**: {v}")
                    else:
                        lines.append(f"- {item}")
            else:
                lines.append(f"**{key}**: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _brief_to_markdown(self, brief: Dict) -> str:
        """Convert content brief to markdown format."""
        lines = []
        
        # Header
        lines.append(f"# Content Brief: {brief.get('title_tag', 'Untitled')}")
        lines.append("")
        lines.append(f"**Status**: {brief.get('status', 'unknown').upper()}")
        lines.append(f"**URL Slug**: `{brief.get('url_slug', '')}`")
        lines.append("")
        
        # Meta elements
        lines.append("## Meta Elements")
        lines.append("")
        lines.append(f"### Title Tag")
        lines.append(f"{brief.get('title_tag', '')}")
        lines.append("")
        lines.append(f"### Meta Description")
        lines.append(f"{brief.get('meta_description', '')}")
        lines.append("")
        lines.append(f"### H1")
        lines.append(f"{brief.get('h1', '')}")
        lines.append("")
        
        # Context
        lines.append("## Context")
        lines.append("")
        lines.append(f"**Macro Context**: {brief.get('macro_context', '')}")
        lines.append("")
        if brief.get("micro_contexts"):
            lines.append("**Micro Contexts**:")
            for ctx in brief.get("micro_contexts", []):
                lines.append(f"- {ctx}")
            lines.append("")
        
        # Sections
        if brief.get("sections"):
            lines.append("## Content Structure")
            lines.append("")
            
            for section in brief.get("sections", []):
                level = section.get("heading_level", "H2")
                heading = "#" * (int(level[1]) + 1)
                lines.append(
                    f"{heading} {section.get('heading_text', '')}"
                )
                
                if section.get("question_type"):
                    lines.append(
                        f"*Question Type: {section.get('question_type')}*"
                    )
                if section.get("format_instruction"):
                    lines.append(
                        f"*Format: {section.get('format_instruction')}*"
                    )
                
                if section.get("content_instructions"):
                    lines.append("")
                    lines.append("**Instructions:**")
                    instr = section.get("content_instructions", {})
                    for key, value in instr.items():
                        lines.append(f"- {key}: {value}")
                
                lines.append("")
        
        # Internal links
        if brief.get("internal_links"):
            lines.append("## Internal Links")
            lines.append("")
            lines.append("| Target | Anchor Text | Priority |")
            lines.append("|--------|-------------|----------|")
            
            for link in brief.get("internal_links", []):
                lines.append(
                    f"| {link.get('target', '')} "
                    f"| {link.get('anchor_text', '')} "
                    f"| {link.get('priority', '')} |"
                )
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        )
        
        return "\n".join(lines)
    
    def _topical_map_to_markdown(self, map_data: Dict) -> str:
        """Convert topical map to markdown format."""
        lines = []
        
        # Header
        lines.append(f"# Topical Map: {map_data.get('name', 'Untitled')}")
        lines.append("")
        lines.append(f"**Type**: {map_data.get('type', 'raw').upper()}")
        lines.append("")
        
        # Project context
        if map_data.get("project"):
            project = map_data.get("project", {})
            lines.append("## Project Context")
            lines.append("")
            lines.append(
                f"- **Source Context**: {project.get('source_context', '')}"
            )
            lines.append(
                f"- **Central Entity**: {project.get('central_entity', '')}"
            )
            lines.append(
                f"- **Central Search Intent**: "
                f"{project.get('central_search_intent', '')}"
            )
            lines.append("")
        
        # Core Section
        if map_data.get("core_section") or map_data.get("entities"):
            lines.append("## Core Section (Monetization)")
            lines.append("")
            
            core_entities = [
                e for e in map_data.get("entities", [])
                if any(
                    a.get("section") == "core"
                    for a in e.get("attributes", [])
                )
            ]
            
            for entity in core_entities:
                lines.append(f"### {entity.get('name', '')}")
                lines.append(
                    f"*Type: {entity.get('type', '')} | "
                    f"PPR Score: {entity.get('total_score', '')}*"
                )
                lines.append("")
                
                for attr in entity.get("attributes", []):
                    if attr.get("section") == "core":
                        lines.append(
                            f"- **{attr.get('name', '')}** "
                            f"({attr.get('classification', '')})"
                        )
                lines.append("")
        
        # Outer Section
        lines.append("## Outer Section (Trust/Authority)")
        lines.append("")
        
        outer_entities = [
            e for e in map_data.get("entities", [])
            if any(
                a.get("section") == "outer"
                for a in e.get("attributes", [])
            )
        ]
        
        for entity in outer_entities:
            lines.append(f"### {entity.get('name', '')}")
            for attr in entity.get("attributes", []):
                if attr.get("section") == "outer":
                    lines.append(f"- {attr.get('name', '')}")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        )
        
        return "\n".join(lines)
    
    @staticmethod
    def get_download_filename(
        base_name: str,
        extension: str
    ) -> str:
        """
        Generate a timestamped download filename.
        
        Args:
            base_name: Base name for the file
            extension: File extension (without dot)
        
        Returns:
            Formatted filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean base name
        clean_name = "".join(
            c if c.isalnum() or c in "-_" else "_"
            for c in base_name
        )
        return f"{clean_name}_{timestamp}.{extension}"


def export_project_data(
    project: Dict,
    topical_maps: List[Dict],
    briefs: List[Dict],
    format: str = "json"
) -> Union[str, bytes]:
    """
    Export all project data.
    
    Args:
        project: Project data
        topical_maps: List of topical maps
        briefs: List of content briefs
        format: Export format (json, csv, excel)
    
    Returns:
        Exported data in specified format
    """
    handler = ExportHandler()
    
    full_data = {
        "project": project,
        "topical_maps": topical_maps,
        "content_briefs": briefs,
        "exported_at": datetime.now().isoformat(),
    }
    
    if format == "json":
        return handler.to_json(full_data)
    elif format == "csv":
        # For CSV, we'll export briefs (most tabular data)
        return handler.to_csv(briefs)
    elif format == "excel":
        sheets = {
            "Project": pd.DataFrame([project]),
            "Briefs": pd.DataFrame(briefs),
        }
        filename = handler.get_download_filename(
            project.get("name", "export"), "xlsx"
        )
        return handler.to_excel(sheets, filename)
    else:
        raise ValueError(f"Unsupported format: {format}")