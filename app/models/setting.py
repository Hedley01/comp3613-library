
from sqlmodel import Field, SQLModel

class PolicySetting(SQLModel, table=True):
    """Key/value settings. Holds the active conflict policy under 'conflict_policy'."""

    key: str = Field(primary_key=True)
    value: str
