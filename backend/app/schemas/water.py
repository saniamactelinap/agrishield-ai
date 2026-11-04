from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.common import DataSourceMetadata
from app.schemas.location import LocationReference


class WaterSourceType(str, Enum):
    """Agricultural water supply sources."""

    RESERVOIR = "RESERVOIR"  # Major/medium dams
    CANAL = "CANAL"  # Irrigation distribution networks
    TANK = "TANK"  # Traditional minor irrigation tanks / Eri
    BOREWELL = "BOREWELL"  # Deep groundwater extraction
    RIVER = "RIVER"  # Direct lift / run-of-river
    GROUNDWATER = "GROUNDWATER"  # Shallow aquifer open wells


class ReservoirStatus(BaseModel):
    """Hydrological state of a major water reservoir or dam.
    
    Standard volume units: TMC (Thousand Million Cubic feet).
    Standard flow rate units: cusecs (cubic feet per second).
    Standard elevation units: meters.
    """

    reservoir_id: str = Field(..., description="Unique reservoir identifier (e.g., 'RES-METTUR')")
    name: str = Field(..., description="Reservoir name (e.g., 'Stanley Reservoir / Mettur Dam')")
    timestamp: datetime = Field(..., description="Observation reading timestamp (UTC/ISO-8601)")
    location: LocationReference = Field(..., description="Reservoir geographic jurisdiction")
    full_reservoir_level_m: float = Field(
        ...,
        gt=0.0,
        description="Full Reservoir Level (FRL) design elevation in meters",
    )
    current_water_level_m: float = Field(
        ...,
        ge=0.0,
        description="Current recorded water elevation in meters",
    )
    gross_capacity_tmc: float = Field(
        ...,
        gt=0.0,
        description="Gross live storage capacity at FRL in TMC (Thousand Million Cubic feet)",
    )
    current_storage_tmc: float = Field(
        ...,
        ge=0.0,
        description="Current live water storage volume in TMC",
    )
    inflow_cusecs: float = Field(
        ...,
        ge=0.0,
        description="Current inflow rate in cubic feet per second (cusecs)",
    )
    outflow_cusecs: float = Field(
        ...,
        ge=0.0,
        description="Current outflow or canal release rate in cubic feet per second (cusecs)",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="State Water Resources Department or Central Water Commission (CWC) metadata",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_storage_capacity(self) -> "ReservoirStatus":
        if self.current_storage_tmc > self.gross_capacity_tmc:
            raise ValueError(
                f"current_storage_tmc ({self.current_storage_tmc} TMC) cannot exceed gross_capacity_tmc ({self.gross_capacity_tmc} TMC)"
            )
        return self


class GroundwaterLevelReading(BaseModel):
    """Observation of subterranean aquifer water table depth."""

    reading_id: str = Field(..., description="Observation record identifier")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    location: LocationReference = Field(..., description="Monitoring well location")
    depth_to_water_m_bgl: float = Field(
        ...,
        ge=0.0,
        description="Depth to static water table in meters below ground level (m bgl)",
    )
    aquifer_category: Optional[str] = Field(
        default=None,
        description="Central Ground Water Board (CGWB) categorization: 'SAFE', 'SEMI_CRITICAL', 'CRITICAL', 'OVER_EXPLOITED'",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="State Groundwater Department or piezometer telemetry metadata",
    )

    model_config = ConfigDict(extra="forbid")


class WaterDemandSupplyBalance(BaseModel):
    """Aggregated agricultural water balance model across a designated accounting period.
    
    Standard volumetric unit: Million Cubic Meters (MCM).
    """

    balance_id: str = Field(..., description="Unique balance assessment identifier")
    period_start: date = Field(..., description="Accounting period start date")
    period_end: date = Field(..., description="Accounting period end date")
    location: LocationReference = Field(..., description="Target administrative district or block")
    crop_water_demand_mcm: float = Field(
        ...,
        ge=0.0,
        description="Estimated aggregate agricultural crop evapotranspiration demand in Million Cubic Meters (MCM)",
    )
    available_surface_water_mcm: float = Field(
        ...,
        ge=0.0,
        description="Available surface irrigation water allocation in Million Cubic Meters (MCM)",
    )
    available_groundwater_mcm: float = Field(
        ...,
        ge=0.0,
        description="Sustainable extractable groundwater volume in Million Cubic Meters (MCM)",
    )
    water_deficit_mcm: float = Field(
        ...,
        ge=0.0,
        description="Unmet irrigation water deficit in MCM, calculated consistently as max(0, demand - total_available)",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Hydrological model or departmental accounting metadata (DERIVED/ESTIMATED)",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_period_and_deficit_consistency(self) -> "WaterDemandSupplyBalance":
        if self.period_end < self.period_start:
            raise ValueError(
                f"period_end ({self.period_end}) cannot be earlier than period_start ({self.period_start})"
            )

        total_available = self.available_surface_water_mcm + self.available_groundwater_mcm
        expected_deficit = max(0.0, round(self.crop_water_demand_mcm - total_available, 4))
        actual_deficit = round(self.water_deficit_mcm, 4)

        if abs(actual_deficit - expected_deficit) > 0.01:
            raise ValueError(
                f"water_deficit_mcm ({self.water_deficit_mcm} MCM) is inconsistent with demand ({self.crop_water_demand_mcm} MCM) "
                f"minus total available ({total_available} MCM). Expected: {expected_deficit} MCM"
            )
        return self
