from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.common import DataSourceMetadata
from app.schemas.location import LocationReference


class SoilTextureClass(str, Enum):
    """USDA and Indian Agricultural Research Institute soil texture classes."""

    CLAY = "CLAY"
    SILTY_CLAY = "SILTY_CLAY"
    SANDY_CLAY = "SANDY_CLAY"
    CLAY_LOAM = "CLAY_LOAM"
    SILTY_CLAY_LOAM = "SILTY_CLAY_LOAM"
    SANDY_CLAY_LOAM = "SANDY_CLAY_LOAM"
    LOAM = "LOAM"
    SILT_LOAM = "SILT_LOAM"
    SANDY_LOAM = "SANDY_LOAM"
    LOAMY_SAND = "LOAMY_SAND"
    SAND = "SAND"
    BLACK_COTTON = "BLACK_COTTON"  # Vertisol commonly found in Deccan & southern plateau
    RED_SOIL = "RED_SOIL"  # Alfisol widely prevalent in Tamil Nadu
    ALLUVIAL = "ALLUVIAL"  # River delta sediments (Cauvery delta)


class MoistureMeasurementType(str, Enum):
    """Measurement methodology distinguishing volumetric from gravimetric moisture."""

    VOLUMETRIC_PERCENT = "VOLUMETRIC_PERCENT"  # VWC (cm³ water / cm³ soil × 100%)
    GRAVIMETRIC_PERCENT = "GRAVIMETRIC_PERCENT"  # GWC (g water / g dry soil × 100%)


class SoilProfile(BaseModel):
    """Physicochemical soil characteristics and baseline moisture retention thresholds."""

    profile_id: str = Field(..., description="Unique soil profile identifier")
    location: LocationReference = Field(..., description="Geographic administrative location of the surveyed profile")
    texture_class: SoilTextureClass = Field(..., description="Predominant soil texture classification")
    ph: float = Field(
        ...,
        ge=0.0,
        le=14.0,
        description="Soil reaction / acidity-alkalinity index (pH 0 - 14)",
    )
    electrical_conductivity_ds_m: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Salinity index in deciSiemens per meter (dS/m) at 25°C",
    )
    organic_carbon_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Soil organic carbon percentage (SOC %)",
    )
    available_n_kg_ha: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Available mineralizable Nitrogen in kilograms per hectare (kg/ha)",
    )
    available_p_kg_ha: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Available Phosphorus in kilograms per hectare (kg/ha)",
    )
    available_k_kg_ha: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Available Potassium in kilograms per hectare (kg/ha)",
    )
    field_capacity_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Volumetric water content at field capacity (-33 kPa matric potential) in %",
    )
    wilting_point_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Volumetric water content at permanent wilting point (-1500 kPa matric potential) in %",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Laboratory soil test report or national soil health card metadata",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_hydraulic_limits(self) -> "SoilProfile":
        if self.wilting_point_pct >= self.field_capacity_pct:
            raise ValueError(
                f"wilting_point_pct ({self.wilting_point_pct}%) must be strictly lower than field_capacity_pct ({self.field_capacity_pct}%)"
            )
        return self


class SoilMoistureReading(BaseModel):
    """Discrete soil moisture reading from in-situ TDR/capacitance sensors or satellite estimates.
    
    The measurement_type field explicitly identifies whether moisture is reported
    as Volumetric Water Content (VWC) or Gravimetric Water Content (GWC).
    """

    reading_id: str = Field(..., description="Unique reading identifier")
    timestamp: datetime = Field(..., description="Measurement timestamp (UTC/ISO-8601)")
    location: LocationReference = Field(..., description="Measurement location")
    depth_cm: float = Field(
        ...,
        gt=0.0,
        description="Sensor or retrieval depth below soil surface in centimeters (e.g., 10.0, 30.0, 60.0 cm)",
    )
    measurement_type: MoistureMeasurementType = Field(
        ...,
        description="Explicit measurement basis: VOLUMETRIC_PERCENT or GRAVIMETRIC_PERCENT",
    )
    moisture_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Soil moisture percentage (0.0% to 100.0%) corresponding to measurement_type",
    )
    plant_available_water_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Relative fraction of total available water remaining between wilting point and field capacity",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Provenance identifying sensor hardware (OBSERVED) or satellite retrieval like SMAP/Sentinel-1 (ESTIMATED)",
    )

    model_config = ConfigDict(extra="forbid")
