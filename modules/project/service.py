"""Project service for CRUD operations on SEO projects."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from config.database import get_session_local
from utils.database import Project


class ProjectService:
    """Service for managing Semantic SEO projects."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize project service.
        
        Args:
            db_session: Optional SQLAlchemy session (creates new if not provided)
        """
        self._session = db_session
        self._owns_session = db_session is None
    
    @property
    def session(self) -> Session:
        """Get database session."""
        if self._session is None:
            SessionLocal = get_session_local()
            self._session = SessionLocal()
        return self._session
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session if we own it."""
        if self._owns_session and self._session:
            self._session.close()
    
    def create_project(
        self,
        name: str,
        source_context: Optional[str] = None,
        central_entity: Optional[str] = None,
        central_search_intent: Optional[str] = None,
        functional_words: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            source_context: Who you are and how you monetize
            central_entity: Main subject matter
            central_search_intent: Unification of context + entity
            functional_words: Predicates/verbs users associate
        
        Returns:
            Created project as dictionary
        """
        project = Project(
            name=name,
            source_context=source_context,
            central_entity=central_entity,
            central_search_intent=central_search_intent,
            functional_words=functional_words or [],
        )
        
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        
        return project.to_dict()
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project UUID
        
        Returns:
            Project as dictionary or None if not found
        """
        project = self.session.query(Project).filter(
            Project.id == project_id
        ).first()
        
        return project.to_dict() if project else None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.
        
        Returns:
            List of projects as dictionaries
        """
        projects = self.session.query(Project).order_by(
            Project.updated_at.desc()
        ).all()
        
        return [p.to_dict() for p in projects]
    
    def update_project(
        self,
        project_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update a project.
        
        Args:
            project_id: Project UUID
            **kwargs: Fields to update
        
        Returns:
            Updated project as dictionary or None if not found
        """
        project = self.session.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            return None
        
        # Update allowed fields
        allowed_fields = {
            "name",
            "source_context",
            "central_entity",
            "central_search_intent",
            "functional_words",
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        self.session.commit()
        self.session.refresh(project)
        
        return project.to_dict()
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all related data.
        
        Args:
            project_id: Project UUID
        
        Returns:
            True if deleted, False if not found
        """
        project = self.session.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            return False
        
        self.session.delete(project)
        self.session.commit()
        
        return True
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for a project.
        
        Args:
            project_id: Project UUID
        
        Returns:
            Dictionary with project statistics
        """
        from utils.database import (
            TopicalMap, ContentBrief, Publication
        )
        
        # Count topical maps
        map_count = self.session.query(TopicalMap).filter(
            TopicalMap.project_id == project_id
        ).count()
        
        # Count briefs by status
        brief_stats = {}
        for status in ["black", "orange", "yellow", "blue", "green"]:
            count = self.session.query(ContentBrief).filter(
                ContentBrief.project_id == project_id,
                ContentBrief.status == status
            ).count()
            brief_stats[status] = count
        
        total_briefs = sum(brief_stats.values())
        
        # Count publications
        pub_count = self.session.query(Publication).join(
            ContentBrief
        ).filter(
            ContentBrief.project_id == project_id
        ).count()
        
        return {
            "project_id": project_id,
            "topical_maps": map_count,
            "total_briefs": total_briefs,
            "briefs_by_status": brief_stats,
            "publications": pub_count,
            "coverage_score": self._calculate_coverage(project_id),
        }
    
    def _calculate_coverage(self, project_id: str) -> float:
        """
        Calculate topical coverage score.
        
        Args:
            project_id: Project UUID
        
        Returns:
            Coverage score between 0 and 1
        """
        from utils.database import Entity, Attribute, ContentBrief
        
        # Get total mapped attributes
        total_attrs = self.session.query(Attribute).join(
            TopicalMap
        ).filter(
            TopicalMap.project_id == project_id
        ).count()
        
        if total_attrs == 0:
            return 0.0
        
        # Get attributes with briefs (green status = covered)
        covered = self.session.query(ContentBrief).filter(
            ContentBrief.project_id == project_id,
            ContentBrief.status == "green"
        ).count()
        
        return min(covered / total_attrs, 1.0)
    
    def duplicate_project(
        self,
        project_id: str,
        new_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Duplicate a project (without content).
        
        Args:
            project_id: Source project UUID
            new_name: Name for the new project
        
        Returns:
            New project as dictionary or None if source not found
        """
        source = self.session.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not source:
            return None
        
        new_project = Project(
            name=new_name,
            source_context=source.source_context,
            central_entity=source.central_entity,
            central_search_intent=source.central_search_intent,
            functional_words=source.functional_words,
        )
        
        self.session.add(new_project)
        self.session.commit()
        self.session.refresh(new_project)
        
        return new_project.to_dict()
    
    def export_project(
        self,
        project_id: str,
        include_briefs: bool = True,
        include_maps: bool = True
    ) -> Dict[str, Any]:
        """
        Export all project data.
        
        Args:
            project_id: Project UUID
            include_briefs: Include content briefs
            include_maps: Include topical maps
        
        Returns:
            Complete project data as dictionary
        """
        from utils.database import TopicalMap, ContentBrief, Entity, Attribute
        
        project = self.get_project(project_id)
        if not project:
            return {}
        
        export_data = {
            "project": project,
            "exported_at": datetime.utcnow().isoformat(),
        }
        
        if include_maps:
            maps = self.session.query(TopicalMap).filter(
                TopicalMap.project_id == project_id
            ).all()
            
            maps_data = []
            for tm in maps:
                map_dict = tm.to_dict()
                
                # Include entities
                entities = self.session.query(Entity).filter(
                    Entity.topical_map_id == tm.id
                ).all()
                map_dict["entities"] = [e.to_dict() for e in entities]
                
                # Include attributes
                attrs = self.session.query(Attribute).filter(
                    Attribute.topical_map_id == tm.id
                ).all()
                map_dict["attributes"] = [a.to_dict() for a in attrs]
                
                maps_data.append(map_dict)
            
            export_data["topical_maps"] = maps_data
        
        if include_briefs:
            briefs = self.session.query(ContentBrief).filter(
                ContentBrief.project_id == project_id
            ).all()
            export_data["content_briefs"] = [b.to_dict() for b in briefs]
        
        return export_data


# Import for backwards compatibility with TopicalMap
from utils.database import TopicalMap