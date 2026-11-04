from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import GeoCoordinate


class LocationLevel(str, Enum):
    """Administrative granularity level."""

    STATE = "STATE"
    DISTRICT = "DISTRICT"
    BLOCK = "BLOCK"  # Block / Taluk / Tehsil
    VILLAGE = "VILLAGE"  # Gram Panchayat / Revenue Village


class Village(BaseModel):
    """Village-level agricultural unit."""

    id: str = Field(..., description="Unique internal village identifier")
    name: str = Field(..., description="Village or Gram Panchayat name")
    lgd_code: Optional[int] = Field(
        default=None,
        gt=0,
        description="Local Government Directory (LGD) village code in India if assigned",
    )
    center_point: Optional[GeoCoordinate] = Field(
        default=None,
        description="Centroid coordinate of the village area",
    )
    total_cultivable_area_ha: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Total cultivable agricultural land area in hectares",
    )

    model_config = ConfigDict(extra="forbid")


class Block(BaseModel):
    """Block / Taluk administrative subdivision."""

    id: str = Field(..., description="Unique internal block identifier")
    name: str = Field(..., description="Block or Taluk name")
    lgd_code: Optional[int] = Field(
        default=None,
        gt=0,
        description="Local Government Directory (LGD) sub-district / block code",
    )
    villages: List[Village] = Field(
        default_factory=list,
        description="List of constituent villages within this block",
    )

    model_config = ConfigDict(extra="forbid")


class District(BaseModel):
    """District administrative agricultural jurisdiction."""

    id: str = Field(..., description="Unique internal district identifier")
    name: str = Field(..., description="District name (e.g., 'Thanjavur', 'Coimbatore')")
    lgd_code: Optional[int] = Field(
        default=None,
        gt=0,
        description="Local Government Directory (LGD) district code",
    )
    agro_climatic_zone: Optional[str] = Field(
        default=None,
        description="Official agro-climatic zone classification (e.g., 'Cauvery Delta Zone')",
    )
    blocks: List[Block] = Field(
        default_factory=list,
        description="List of administrative blocks in the district",
    )

    model_config = ConfigDict(extra="forbid")


class State(BaseModel):
    """State-level administrative entity."""

    id: str = Field(..., description="Unique internal state identifier")
    name: str = Field(..., description="State name (e.g., 'Tamil Nadu')")
    state_code: str = Field(
        ...,
        min_length=2,
        max_length=4,
        description="Standard 2 to 4 character state code (e.g., 'TN')",
    )
    lgd_code: Optional[int] = Field(
        default=None,
        gt=0,
        description="Local Government Directory (LGD) state code",
    )
    districts: List[District] = Field(
        default_factory=list,
        description="Districts within the state",
    )

    model_config = ConfigDict(extra="forbid")


class LocationReference(BaseModel):
    """Normalized spatial reference used across agricultural observations and assessments."""

    state_id: str = Field(..., description="State identifier")
    state_name: Optional[str] = Field(default=None, description="State display name")
    district_id: str = Field(..., description="District identifier")
    district_name: Optional[str] = Field(default=None, description="District display name")
    block_id: Optional[str] = Field(
        default=None,
        description="Optional block or taluk identifier",
    )
    block_name: Optional[str] = Field(default=None, description="Block display name")
    village_id: Optional[str] = Field(
        default=None,
        description="Optional village identifier",
    )
    village_name: Optional[str] = Field(default=None, description="Village display name")
    lgd_code: Optional[int] = Field(
        default=None,
        gt=0,
        description="Most granular Indian LGD code available for this reference",
    )
    coordinates: Optional[GeoCoordinate] = Field(
        default=None,
        description="Precise geo-coordinate point if field or sensor location is known",
    )

    model_config = ConfigDict(extra="forbid")
