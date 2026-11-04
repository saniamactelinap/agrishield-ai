from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DataSourceType(str, Enum):
    """Classification of data provenance to distinguish observed facts from predictions."""

    OBSERVED = "OBSERVED"  # Physical sensors, in-situ weather stations, ground truth surveys
    FORECAST = "FORECAST"  # Numerical weather predictions, forward projections
    ESTIMATED = "ESTIMATED"  # Satellite remote-sensing retrievals, proxy estimations
    DERIVED = "DERIVED"  # Calculated agronomic balances, empirical indices (e.g. GDD)


class DataSourceMetadata(BaseModel):
    """Metadata describing data origin, retrieval timestamp, and technical provenance."""

    source_name: str = Field(
        ...,
        description="Name of the data provider or instrument (e.g., 'IMD', 'Sentinel-2', 'Field Sensor')",
    )
    source_type: DataSourceType = Field(
        ...,
        description="Provenance category separating ground observations from model forecasts and satellite estimates",
    )
    retrieved_at: datetime = Field(
        ...,
        description="Timestamp indicating when this observation or dataset was retrieved/ingested",
    )
    source_record_id: Optional[str] = Field(
        default=None,
        description="Optional upstream unique identifier from the source provider (e.g., station ID, scene ID)",
    )
    spatial_resolution_m: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Spatial resolution in meters for satellite imagery or gridded weather/soil models",
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Normalized confidence or data quality score between 0.0 and 1.0",
    )

    model_config = ConfigDict(extra="forbid")


class GeoCoordinate(BaseModel):
    """Geographic point coordinate with optional elevation."""

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees (WGS 84)",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees (WGS 84)",
    )
    elevation_m: Optional[float] = Field(
        default=None,
        description="Elevation above mean sea level in meters",
    )

    model_config = ConfigDict(extra="forbid")
