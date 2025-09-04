from __future__ import annotations
from typing import Optional
from enum import Enum as PyEnum
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB

# Helpers
def utcnow() -> datetime:
    return datetime.now(timezone.utc)

# ---------- Roles ----------
class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=2, max_length=50)

class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role_id: int = Field(foreign_key="roles.id", index=True)
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

# ---------- Users ----------
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=320)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)  # immutable (login-only)
    display_name: Optional[str] = Field(default=None, max_length=80)
    password_hash: str
    profile_private: bool = Field(default=False)
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

# ---------- Groups ----------
class GroupType(str, PyEnum):
    GENERIC = "generic"
    INSTITUTION = "institution"

class Group(SQLModel, table=True):
    __tablename__ = "groups"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True, min_length=3, max_length=80)
    name: str = Field(max_length=120)
    description: Optional[str] = None
    type: GroupType = Field(default=GroupType.GENERIC)        # "generic" | "institution"
    verified: bool = Field(default=False)             # admin-approved flag for institution groups
    is_public: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    class MemberRole(str, PyEnum):
        ADMIN = "admin"
        MEMBER = "member"

    role: MemberRole = Field(default=MemberRole.MEMBER)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_member"),)

# ---------- Posts / Comments / Reactions ----------
# Post content as JSON blocks (see product spec); store in JSONB
class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    author_user_id: int = Field(foreign_key="users.id", index=True)
    group_id: Optional[int] = Field(default=None, foreign_key="groups.id", index=True)
    title: Optional[str] = None  # required when group_id is not null (enforce in service layer)
    content: dict = Field(sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
    __table_args__ = (Index("ix_posts_group_recent", "group_id", "created_at"),)

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    author_user_id: int = Field(foreign_key="users.id", index=True)
    body: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)

ReactionTarget = None
class ReactionTarget(str, PyEnum):
    POST = "post"
    COMMENT = "comment"

ReactionType = None
class ReactionType(str, PyEnum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"

class Reaction(SQLModel, table=True):
    __tablename__ = "reactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    target_type: ReactionTarget
    target_id: int = Field(index=True)  # post.id or comment.id depending on target_type
    reaction: ReactionType = Field(default=ReactionType.LIKE)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target_reaction"),)

# ---------- Follows ----------
class FollowTarget(str, PyEnum):
    USER = "user"
    GROUP = "group"
class Follow(SQLModel, table=True):
    __tablename__ = "follows"
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_user_id: int = Field(foreign_key="users.id", index=True)
    target_type: FollowTarget
    target_id: int = Field(index=True)  # users.id or groups.id
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("follower_user_id", "target_type", "target_id", name="uq_follow"),)

# ---------- Reports ----------
class ReportTarget(str, PyEnum):
    USER = "user"
    GROUP = "group"
    POST = "post"
    COMMENT = "comment"
class Report(SQLModel, table=True):
    __tablename__ = "reports"
    id: Optional[int] = Field(default=None, primary_key=True)
    reporter_user_id: int = Field(foreign_key="users.id", index=True)
    target_type: ReportTarget
    target_id: int = Field(index=True)
    reason: str
    class ReportStatus(str, PyEnum):
        OPEN = "open"
        CLOSED = "closed"

    status: ReportStatus = Field(default=ReportStatus.OPEN)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)

# ---------- 1–1 Conversations ----------
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_a_id: int = Field(foreign_key="users.id", index=True)
    user_b_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id", name="uq_pair"),)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    sender_user_id: int = Field(foreign_key="users.id", index=True)
    body: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
