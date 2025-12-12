"""SQLAlchemy database models for Semantic SEO Platform."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Date, Index, UniqueConstraint
)
from sqlalchemy.orm import (
    declarative_base, relationship, Mapped, mapped_column
)

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Project(Base):
    """
    Project model - represents a Semantic SEO project.
    
    Based on Koray's framework:
    - Source Context: Who you are and how you make money
    - Central Entity: Main subject matter of the project
    - Central Search Intent: Unification of source context + entity
    """
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_context: Mapped[Optional[str]] = mapped_column(Text)
    central_entity: Mapped[Optional[str]] = mapped_column(String(255))
    central_search_intent: Mapped[Optional[str]] = mapped_column(Text)
    functional_words: Mapped[Optional[Dict]] = mapped_column(
        JSON, default=list
    )  # Predicates/verbs
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    topical_maps: Mapped[List["TopicalMap"]] = relationship(
        "TopicalMap", back_populates="project", cascade="all, delete-orphan"
    )
    content_briefs: Mapped[List["ContentBrief"]] = relationship(
        "ContentBrief", back_populates="project", cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "source_context": self.source_context,
            "central_entity": self.central_entity,
            "central_search_intent": self.central_search_intent,
            "functional_words": self.functional_words or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TopicalMap(Base):
    """
    Topical Map model - semantic blueprint for entity coverage.
    
    Types:
    - raw: Initial entity-attribute mapping
    - processed: With title tags, URLs, meta descriptions
    """
    __tablename__ = "topical_maps"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(20), default="raw"
    )  # raw or processed
    core_section: Mapped[Optional[Dict]] = mapped_column(JSON)
    outer_section: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="topical_maps"
    )
    entities: Mapped[List["Entity"]] = relationship(
        "Entity", back_populates="topical_map", cascade="all, delete-orphan"
    )
    attributes: Mapped[List["Attribute"]] = relationship(
        "Attribute", back_populates="topical_map", cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "type": self.type,
            "core_section": self.core_section,
            "outer_section": self.outer_section,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Entity(Base):
    """
    Entity model - concepts within a topical map.
    
    Types:
    - central: The main entity of the project
    - derived: Entities that branch from the central entity
    - sibling: Related entities in the same class
    
    Scores (PPR - Prominence, Popularity, Relevance):
    - prominence: Can the entity be defined without this? (1-10)
    - popularity: Search demand (1-10)
    - relevance: Fit with source context (1-10)
    """
    __tablename__ = "entities"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    topical_map_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topical_maps.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(20), default="derived"
    )  # central, derived, sibling
    wikidata_id: Mapped[Optional[str]] = mapped_column(String(50))
    properties: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # PPR Scores
    prominence_score: Mapped[int] = mapped_column(Integer, default=5)
    popularity_score: Mapped[int] = mapped_column(Integer, default=5)
    relevance_score: Mapped[int] = mapped_column(Integer, default=5)
    
    # Relationships
    topical_map: Mapped["TopicalMap"] = relationship(
        "TopicalMap", back_populates="entities"
    )
    entity_attributes: Mapped[List["EntityAttribute"]] = relationship(
        "EntityAttribute", back_populates="entity", cascade="all, delete-orphan"
    )
    content_briefs: Mapped[List["ContentBrief"]] = relationship(
        "ContentBrief", back_populates="entity"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_entities_map", "topical_map_id"),
    )
    
    @property
    def total_score(self) -> int:
        """Calculate total PPR score."""
        return self.prominence_score + self.popularity_score + self.relevance_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topical_map_id": self.topical_map_id,
            "name": self.name,
            "type": self.type,
            "wikidata_id": self.wikidata_id,
            "properties": self.properties,
            "prominence_score": self.prominence_score,
            "popularity_score": self.popularity_score,
            "relevance_score": self.relevance_score,
            "total_score": self.total_score,
        }


class Attribute(Base):
    """
    Attribute model - properties/aspects of entities.
    
    Classification (Unique-First Rule):
    - unique: Features only this entity has
    - root: Attributes in all instances of the class
    - rarer: Attributes in some but not all instances
    
    Section:
    - core: Directly tied to monetization
    - outer: Builds trust and historical data
    """
    __tablename__ = "attributes"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    topical_map_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topical_maps.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    classification: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # unique, root, rarer
    section: Mapped[str] = mapped_column(
        String(10), default="core"
    )  # core or outer
    depth_level: Mapped[int] = mapped_column(Integer, default=1)
    search_volume: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    topical_map: Mapped["TopicalMap"] = relationship(
        "TopicalMap", back_populates="attributes"
    )
    entity_attributes: Mapped[List["EntityAttribute"]] = relationship(
        "EntityAttribute", back_populates="attribute", cascade="all, delete-orphan"
    )
    content_briefs: Mapped[List["ContentBrief"]] = relationship(
        "ContentBrief", back_populates="attribute"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_attributes_map", "topical_map_id"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topical_map_id": self.topical_map_id,
            "name": self.name,
            "classification": self.classification,
            "section": self.section,
            "depth_level": self.depth_level,
            "search_volume": self.search_volume,
        }


class EntityAttribute(Base):
    """
    Entity-Attribute relationship model.
    
    Links entities to their attributes with relationship metadata.
    """
    __tablename__ = "entity_attributes"
    
    entity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True
    )
    attribute_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("attributes.id", ondelete="CASCADE"),
        primary_key=True
    )
    relationship_type: Mapped[Optional[str]] = mapped_column(String(50))
    metadata: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Relationships
    entity: Mapped["Entity"] = relationship(
        "Entity", back_populates="entity_attributes"
    )
    attribute: Mapped["Attribute"] = relationship(
        "Attribute", back_populates="entity_attributes"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "attribute_id": self.attribute_id,
            "relationship_type": self.relationship_type,
            "metadata": self.metadata,
        }


class ContentBrief(Base):
    """
    Content Brief model - CorelIS framework implementation.
    
    Status workflow (color-coded):
    - black: Brief not ready
    - orange: Brief ready
    - yellow: Writing in progress
    - blue: Written, awaiting publication
    - green: Published
    
    CorelIS components:
    - Contextual Vector: Logical heading flow
    - Contextual Hierarchy: H2/H3/H4 weighting
    - Contextual Structure: Format instructions
    - Contextual Connection: Internal links
    """
    __tablename__ = "content_briefs"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("entities.id", ondelete="SET NULL")
    )
    attribute_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("attributes.id", ondelete="SET NULL")
    )
    
    # Meta elements
    title_tag: Mapped[Optional[str]] = mapped_column(String(255))
    url_slug: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    h1: Mapped[Optional[str]] = mapped_column(String(255))
    image_alts: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(10), default="black"
    )  # black, orange, yellow, blue, green
    
    # Context
    macro_context: Mapped[Optional[str]] = mapped_column(Text)
    micro_contexts: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Publication timing
    target_publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Content specifications
    word_count_target: Mapped[Optional[int]] = mapped_column(Integer)
    authorship_codes: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="content_briefs"
    )
    entity: Mapped[Optional["Entity"]] = relationship(
        "Entity", back_populates="content_briefs"
    )
    attribute: Mapped[Optional["Attribute"]] = relationship(
        "Attribute", back_populates="content_briefs"
    )
    sections: Mapped[List["BriefSection"]] = relationship(
        "BriefSection", back_populates="brief", cascade="all, delete-orphan"
    )
    outgoing_links: Mapped[List["InternalLink"]] = relationship(
        "InternalLink",
        foreign_keys="InternalLink.source_brief_id",
        back_populates="source_brief",
        cascade="all, delete-orphan"
    )
    incoming_links: Mapped[List["InternalLink"]] = relationship(
        "InternalLink",
        foreign_keys="InternalLink.target_brief_id",
        back_populates="target_brief",
        cascade="all, delete-orphan"
    )
    publication: Mapped[Optional["Publication"]] = relationship(
        "Publication", back_populates="brief", uselist=False
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_briefs_project", "project_id"),
        Index("idx_briefs_status", "status"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "entity_id": self.entity_id,
            "attribute_id": self.attribute_id,
            "title_tag": self.title_tag,
            "url_slug": self.url_slug,
            "meta_description": self.meta_description,
            "h1": self.h1,
            "image_alts": self.image_alts,
            "status": self.status,
            "macro_context": self.macro_context,
            "micro_contexts": self.micro_contexts,
            "target_publish_date": (
                self.target_publish_date.isoformat()
                if self.target_publish_date else None
            ),
            "actual_publish_date": (
                self.actual_publish_date.isoformat()
                if self.actual_publish_date else None
            ),
            "word_count_target": self.word_count_target,
            "authorship_codes": self.authorship_codes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BriefSection(Base):
    """
    Brief Section model - heading structure within a brief.
    
    Question types:
    - boolean: Yes/No answers
    - definitional: "What is..." questions
    - grouping: "Types of..." questions
    - comparative: "Best...", "Vs..." questions
    - none: Not a question
    
    Format instructions:
    - FS: Featured Snippet (under 40 words)
    - PAA: People Also Ask (single definitive sentence)
    - listing: List format
    - long_form: Extended explanation
    - table: Table format
    """
    __tablename__ = "brief_sections"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    brief_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("content_briefs.id", ondelete="CASCADE"),
        nullable=False
    )
    heading_level: Mapped[Optional[str]] = mapped_column(
        String(5)
    )  # H2, H3, H4, H5
    heading_text: Mapped[str] = mapped_column(String(500), nullable=False)
    order_position: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # boolean, definitional, grouping, comparative, none
    format_instruction: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # FS, PAA, listing, long_form, table
    content_instructions: Mapped[Optional[Dict]] = mapped_column(JSON)
    required_terms: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Relationships
    brief: Mapped["ContentBrief"] = relationship(
        "ContentBrief", back_populates="sections"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "brief_id": self.brief_id,
            "heading_level": self.heading_level,
            "heading_text": self.heading_text,
            "order_position": self.order_position,
            "question_type": self.question_type,
            "format_instruction": self.format_instruction,
            "content_instructions": self.content_instructions,
            "required_terms": self.required_terms,
        }


class InternalLink(Base):
    """
    Internal Link model - links between content briefs.
    
    Implements Koray's linking strategy:
    - Root document links get highest priority
    - Heading-Anchor-Title alignment
    - Contextual bridges for topic transitions
    """
    __tablename__ = "internal_links"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    source_brief_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("content_briefs.id", ondelete="CASCADE"),
        nullable=False
    )
    target_brief_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("content_briefs.id", ondelete="CASCADE"),
        nullable=False
    )
    anchor_text: Mapped[Optional[str]] = mapped_column(String(255))
    placement_section: Mapped[Optional[str]] = mapped_column(String(255))
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1-10, 1=highest
    is_contextual_bridge: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    source_brief: Mapped["ContentBrief"] = relationship(
        "ContentBrief",
        foreign_keys=[source_brief_id],
        back_populates="outgoing_links"
    )
    target_brief: Mapped["ContentBrief"] = relationship(
        "ContentBrief",
        foreign_keys=[target_brief_id],
        back_populates="incoming_links"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "source_brief_id", "target_brief_id",
            name="uq_link_pair"
        ),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_brief_id": self.source_brief_id,
            "target_brief_id": self.target_brief_id,
            "anchor_text": self.anchor_text,
            "placement_section": self.placement_section,
            "priority": self.priority,
            "is_contextual_bridge": self.is_contextual_bridge,
        }


class Publication(Base):
    """
    Publication model - published content from briefs.
    """
    __tablename__ = "publications"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    brief_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("content_briefs.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    url: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text)
    schema_markup: Mapped[Optional[Dict]] = mapped_column(JSON)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    gsc_data: Mapped[Optional[Dict]] = mapped_column(JSON)
    performance_metrics: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Relationships
    brief: Mapped["ContentBrief"] = relationship(
        "ContentBrief", back_populates="publication"
    )
    query_data: Mapped[List["QueryData"]] = relationship(
        "QueryData", back_populates="publication", cascade="all, delete-orphan"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "brief_id": self.brief_id,
            "url": self.url,
            "schema_markup": self.schema_markup,
            "published_at": (
                self.published_at.isoformat()
                if self.published_at else None
            ),
            "gsc_data": self.gsc_data,
            "performance_metrics": self.performance_metrics,
        }


class QueryData(Base):
    """
    Query Data model - GSC query performance data.
    
    Used for:
    - 3-Column Query Analysis
    - Lost/New query detection
    - Performance tracking
    """
    __tablename__ = "query_data"
    
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    publication_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("publications.id", ondelete="CASCADE"),
        nullable=False
    )
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[Optional[float]] = mapped_column(Float)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[Optional[float]] = mapped_column(Float)
    date: Mapped[Optional[datetime]] = mapped_column(Date)
    
    # Relationships
    publication: Mapped["Publication"] = relationship(
        "Publication", back_populates="query_data"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_query_data_publication", "publication_id"),
        Index("idx_query_data_date", "date"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "publication_id": self.publication_id,
            "query": self.query,
            "position": self.position,
            "clicks": self.clicks,
            "impressions": self.impressions,
            "ctr": self.ctr,
            "date": self.date.isoformat() if self.date else None,
        }