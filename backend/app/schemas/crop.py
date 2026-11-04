from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CropCategory(str, Enum):
    """Broad agronomic classification category."""

    CEREAL = "CEREAL"
    PULSE = "PULSE"
    OILSEED = "OILSEED"
    COMMERCIAL = "COMMERCIAL"  # Sugarcane, Cotton, etc.
    HORTICULTURE = "HORTICULTURE"  # Vegetables, Fruits, Spices
    FODDER = "FODDER"


class CroppingSeason(str, Enum):
    """Agricultural cropping season classification in India."""

    KHARIF = "KHARIF"  # Monsoon season (approx. June to October)
    RABI = "RABI"  # Winter season (approx. October to March)
    ZAID = "ZAID"  # Summer season (approx. March to June)
    PERENNIAL = "PERENNIAL"  # Year-round crops (e.g., Sugarcane, Banana)


class WaterRequirementCategory(str, Enum):
    """Categorical classification of seasonal crop water consumption."""

    LOW = "LOW"  # < 400 mm
    MEDIUM = "MEDIUM"  # 400 - 800 mm
    HIGH = "HIGH"  # 800 - 1400 mm
    VERY_HIGH = "VERY_HIGH"  # > 1400 mm (e.g., Paddy, Sugarcane)


class Crop(BaseModel):
    """Crop agronomic profile and baseline domain parameters.
    
    Note: Agronomic ranges (temperature, water, pH) represent baseline domain guidelines
    subject to regional micro-climate and cultivar-specific calibration.
    """

    id: str = Field(..., description="Unique alphanumeric identifier for the crop (e.g., 'CROP-PADDY')")
    name: str = Field(..., description="Common English name (e.g., 'Paddy / Rice')")
    botanical_name: Optional[str] = Field(
        default=None,
        description="Scientific taxonomic binomial nomenclature (e.g., 'Oryza sativa')",
    )
    local_name_ta: Optional[str] = Field(
        default=None,
        description="Vernacular local name in Tamil (e.g., 'நெல்')",
    )
    category: CropCategory = Field(..., description="Agricultural category")
    season: CroppingSeason = Field(..., description="Primary cropping season")
    water_category: WaterRequirementCategory = Field(
        ...,
        description="General water intensity category",
    )
    optimal_temp_min_c: float = Field(
        ...,
        description="Baseline minimum optimal temperature in °C",
    )
    optimal_temp_max_c: float = Field(
        ...,
        description="Baseline maximum optimal temperature in °C",
    )
    water_requirement_mm_min: float = Field(
        ...,
        ge=0.0,
        description="Baseline minimum total seasonal water requirement in mm",
    )
    water_requirement_mm_max: float = Field(
        ...,
        ge=0.0,
        description="Baseline maximum total seasonal water requirement in mm",
    )
    optimal_soil_ph_min: float = Field(
        default=6.0,
        ge=0.0,
        le=14.0,
        description="Baseline minimum optimal soil pH",
    )
    optimal_soil_ph_max: float = Field(
        default=7.5,
        ge=0.0,
        le=14.0,
        description="Baseline maximum optimal soil pH",
    )
    rooting_depth_m_max: float = Field(
        default=1.0,
        gt=0.0,
        description="Baseline maximum effective crop rooting depth in meters",
    )
    typical_maturity_days: int = Field(
        ...,
        gt=0,
        description="Typical crop cycle duration from sowing to harvest in days",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_agronomic_ranges(self) -> "Crop":
        if self.optimal_temp_min_c > self.optimal_temp_max_c:
            raise ValueError(
                f"optimal_temp_min_c ({self.optimal_temp_min_c}°C) cannot exceed optimal_temp_max_c ({self.optimal_temp_max_c}°C)"
            )
        if self.water_requirement_mm_min > self.water_requirement_mm_max:
            raise ValueError(
                f"water_requirement_mm_min ({self.water_requirement_mm_min} mm) cannot exceed water_requirement_mm_max ({self.water_requirement_mm_max} mm)"
            )
        if self.optimal_soil_ph_min > self.optimal_soil_ph_max:
            raise ValueError(
                f"optimal_soil_ph_min ({self.optimal_soil_ph_min}) cannot exceed optimal_soil_ph_max ({self.optimal_soil_ph_max})"
            )
        return self


class CropSummary(BaseModel):
    """Concise representation of a crop for listings and select options."""

    id: str = Field(..., description="Crop identifier")
    name: str = Field(..., description="Common English name")
    local_name_ta: Optional[str] = Field(default=None, description="Vernacular Tamil name")
    category: CropCategory
    season: CroppingSeason
    water_category: WaterRequirementCategory

    model_config = ConfigDict(extra="forbid")
