from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50, regex=r"^[a-zA-Z0-9_-]+$")
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=200)
    is_active: bool = Field(default=True)
    openai_api_key: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    prompt_templates: List["PromptTemplate"] = Relationship(back_populates="user")
    favorites: List["UserFavorite"] = Relationship(back_populates="user")
    generations: List["PromptGeneration"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color: str = Field(default="#3B82F6", max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    prompt_templates: List["PromptTemplate"] = Relationship(back_populates="category")


class PromptTemplate(SQLModel, table=True):
    __tablename__ = "prompt_templates"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: str = Field(max_length=10000)  # The actual prompt template with placeholders
    keywords: List[str] = Field(default=[], sa_column=Column(JSON))  # For search functionality
    parameters: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))  # Dynamic parameter definitions
    is_public: bool = Field(default=False)  # Whether template is shared publicly
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)  # Track how often template is used
    user_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="prompt_templates")
    category: Optional[Category] = Relationship(back_populates="prompt_templates")
    favorites: List["UserFavorite"] = Relationship(back_populates="prompt_template")
    generations: List["PromptGeneration"] = Relationship(back_populates="prompt_template")


class UserFavorite(SQLModel, table=True):
    __tablename__ = "user_favorites"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    prompt_template_id: int = Field(foreign_key="prompt_templates.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="favorites")
    prompt_template: PromptTemplate = Relationship(back_populates="favorites")


class PromptGeneration(SQLModel, table=True):
    __tablename__ = "prompt_generations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    prompt_template_id: int = Field(foreign_key="prompt_templates.id")
    input_parameters: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # User-provided parameter values
    generated_prompt: str = Field(max_length=15000)  # Final prompt after parameter substitution
    openai_response: Optional[str] = Field(default=None, max_length=50000)  # OpenAI API response
    openai_model: str = Field(default="gpt-3.5-turbo", max_length=50)  # Model used for generation
    tokens_used: Optional[int] = Field(default=None)  # Tokens consumed
    cost: Optional[Decimal] = Field(default=Decimal("0"), decimal_places=6, max_digits=10)  # Cost of generation
    status: str = Field(default="pending", max_length=20)  # pending, completed, failed
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="generations")
    prompt_template: PromptTemplate = Relationship(back_populates="generations")


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50, regex=r"^[a-zA-Z0-9_-]+$")
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(max_length=200)


class UserLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    email: Optional[str] = Field(
        default=None, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    full_name: Optional[str] = Field(default=None, max_length=200)
    openai_api_key: Optional[str] = Field(default=None, max_length=255)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color: str = Field(default="#3B82F6", max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7, regex=r"^#[0-9A-Fa-f]{6}$")


class PromptTemplateCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: str = Field(max_length=10000)
    keywords: List[str] = Field(default=[])
    parameters: List[Dict[str, Any]] = Field(default=[])
    is_public: bool = Field(default=False)
    category_id: Optional[int] = Field(default=None)


class PromptTemplateUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: Optional[str] = Field(default=None, max_length=10000)
    keywords: Optional[List[str]] = Field(default=None)
    parameters: Optional[List[Dict[str, Any]]] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class PromptGenerationCreate(SQLModel, table=False):
    prompt_template_id: int
    input_parameters: Dict[str, Any] = Field(default={})
    openai_model: str = Field(default="gpt-3.5-turbo", max_length=50)


class PromptGenerationUpdate(SQLModel, table=False):
    openai_response: Optional[str] = Field(default=None, max_length=50000)
    tokens_used: Optional[int] = Field(default=None)
    cost: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    status: Optional[str] = Field(default=None, max_length=20)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    completed_at: Optional[datetime] = Field(default=None)


# Search and filter schemas
class PromptTemplateSearch(SQLModel, table=False):
    query: Optional[str] = Field(default=None, max_length=200)
    category_id: Optional[int] = Field(default=None)
    keywords: Optional[List[str]] = Field(default=None)
    user_id: Optional[int] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserDashboardStats(SQLModel, table=False):
    total_templates: int
    total_generations: int
    total_favorites: int
    recent_generations: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]
    monthly_usage: List[Dict[str, Any]]
