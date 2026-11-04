from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.location import LocationReference


class GrowthStageName(str, Enum):
    """Standardized phenological crop growth stages."""

    GERMINATION = "GERMINATION"
    VEGETATIVE = "VEGETATIVE"
    TILLERING = "TILLERING"  # For cereals / grasses
    FLOWERING = "FLOWERING"
    GRAIN_FILLING = "GRAIN_FILLING"  # Pod / grain development
    MATURITY = "MATURITY"
    HARVEST = "HARVEST"


class GrowthStageSpecification(BaseModel):
    """Phenological growth stage parameters and baseline crop coefficient (Kc).
    
    Note: Stage durations and Kc values are configurable domain baselines
    used for FAO-56 Penman-Monteith crop water requirement calculations.
    """

    crop_id: str = Field(..., description="Referenced crop identifier")
    stage_name: GrowthStageName = Field(..., description="Phenological growth stage name")
    stage_order: int = Field(
        ...,
        ge=1,
        description="Sequential ordinal position of the stage (1-indexed)",
    )
    duration_days_min: int = Field(
        ...,
        gt=0,
        description="Minimum typical duration of this stage in days",
    )
    duration_days_max: int = Field(
        ...,
        gt=0,
        description="Maximum typical duration of this stage in days",
    )
    baseline_gdd_c: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Baseline accumulated Growing Degree Days required for this stage in °C-days",
    )
    kc_coefficient: float = Field(
        ...,
        gt=0.0,
        le=2.0,
        description="Baseline FAO-56 crop coefficient (Kc) for reference evapotranspiration adjustment",
    )
    is_critical_water_stage: bool = Field(
        default=False,
        description="True if moisture deficit at this stage induces irreversible yield penalties",
    )
    pest_disease_susceptibilities: List[str] = Field(
        default_factory=list,
        description="List of common pest or disease outbreaks associated with this stage",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_duration_range(self) -> "GrowthStageSpecification":
        if self.duration_days_min > self.duration_days_max:
            raise ValueError(
                f"duration_days_min ({self.duration_days_min}) cannot exceed duration_days_max ({self.duration_days_max})"
            )
        return self


class ActiveCropCycle(BaseModel):
    """Real-world tracked crop cycle for a field or geographic cluster."""

    cycle_id: str = Field(..., description="Unique tracked cycle identifier")
    crop_id: str = Field(..., description="Referenced crop identifier")
    location: LocationReference = Field(..., description="Geographic location of the cultivated area")
    sowing_date: date = Field(..., description="Date of sowing or transplanting")
    current_stage: GrowthStageName = Field(..., description="Current observed or modeled growth stage")
    estimated_harvest_date: Optional[date] = Field(
        default=None,
        description="Projected harvest date based on duration and weather progression",
    )
    area_sown_ha: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Total cultivated area in hectares for this cycle",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self) -> "ActiveCropCycle":
        if self.estimated_harvest_date and self.estimated_harvest_date < self.sowing_date:
            raise ValueError(
                f"estimated_harvest_date ({self.estimated_harvest_date}) cannot be earlier than sowing_date ({self.sowing_date})"
            )
        return self
