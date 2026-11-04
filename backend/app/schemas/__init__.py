"""AgriShield AI modular agricultural data schemas."""

from app.schemas.common import (
    DataSourceMetadata,
    DataSourceType,
    GeoCoordinate,
)
from app.schemas.crop import (
    Crop,
    CropCategory,
    CroppingSeason,
    CropSummary,
    WaterRequirementCategory,
)
from app.schemas.growth_stage import (
    ActiveCropCycle,
    GrowthStageName,
    GrowthStageSpecification,
)
from app.schemas.location import (
    Block,
    District,
    LocationLevel,
    LocationReference,
    State,
    Village,
)
from app.schemas.risk import (
    AgriculturalRiskAssessment,
    AssessmentMethodology,
    RiskCategory,
    RiskFactorContribution,
    RiskSeverityLevel,
)
from app.schemas.soil import (
    MoistureMeasurementType,
    SoilMoistureReading,
    SoilProfile,
    SoilTextureClass,
)
from app.schemas.water import (
    GroundwaterLevelReading,
    ReservoirStatus,
    WaterDemandSupplyBalance,
    WaterSourceType,
)
from app.schemas.weather import (
    WeatherForecastPoint,
    WeatherForecastSeries,
    WeatherObservation,
)

__all__ = [
    # Common
    "DataSourceMetadata",
    "DataSourceType",
    "GeoCoordinate",
    # Location
    "LocationLevel",
    "Village",
    "Block",
    "District",
    "State",
    "LocationReference",
    # Crop
    "CropCategory",
    "CroppingSeason",
    "WaterRequirementCategory",
    "Crop",
    "CropSummary",
    # Growth Stage
    "GrowthStageName",
    "GrowthStageSpecification",
    "ActiveCropCycle",
    # Weather
    "WeatherObservation",
    "WeatherForecastPoint",
    "WeatherForecastSeries",
    # Soil
    "SoilTextureClass",
    "MoistureMeasurementType",
    "SoilProfile",
    "SoilMoistureReading",
    # Water
    "WaterSourceType",
    "ReservoirStatus",
    "GroundwaterLevelReading",
    "WaterDemandSupplyBalance",
    # Risk
    "RiskCategory",
    "RiskSeverityLevel",
    "AssessmentMethodology",
    "RiskFactorContribution",
    "AgriculturalRiskAssessment",
]
