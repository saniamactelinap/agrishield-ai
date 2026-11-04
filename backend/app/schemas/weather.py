from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.common import DataSourceMetadata
from app.schemas.location import LocationReference


class WeatherObservation(BaseModel):
    """Ground-truth or in-situ weather observation.
    
    All measurable variables use explicit standard units:
    temperature (°C), rainfall (mm), humidity (%), wind speed (km/h),
    wind direction (degrees), solar radiation (MJ/m²/day), and ET0 (mm/day).
    """

    observation_id: str = Field(..., description="Unique observation identifier")
    timestamp: datetime = Field(..., description="Date and time when measurements were recorded (UTC/ISO-8601)")
    location: LocationReference = Field(..., description="Geographic administrative location of the weather station or sensor")
    temperature_c: float = Field(
        ...,
        description="Current ambient dry-bulb temperature in °C",
    )
    temp_min_c: Optional[float] = Field(
        default=None,
        description="Minimum temperature recorded during the observation period in °C",
    )
    temp_max_c: Optional[float] = Field(
        default=None,
        description="Maximum temperature recorded during the observation period in °C",
    )
    relative_humidity_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Relative humidity in percentage (0 - 100%)",
    )
    rainfall_mm: float = Field(
        ...,
        ge=0.0,
        description="Accumulated precipitation depth in millimeters (mm)",
    )
    wind_speed_kmh: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Wind speed in kilometers per hour (km/h)",
    )
    wind_direction_deg: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=360.0,
        description="Wind direction in degrees from true North (0 - 360°)",
    )
    solar_radiation_mj_m2: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Global daily solar radiation in megajoules per square meter (MJ/m²/day)",
    )
    reference_et0_mm: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="FAO-56 Penman-Monteith reference evapotranspiration in mm/day",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Provenance identifying the observation station and ingest timestamp",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_temperature_bounds(self) -> "WeatherObservation":
        if self.temp_min_c is not None and self.temp_max_c is not None:
            if self.temp_min_c > self.temp_max_c:
                raise ValueError(
                    f"temp_min_c ({self.temp_min_c}°C) cannot exceed temp_max_c ({self.temp_max_c}°C)"
                )
        return self


class WeatherForecastPoint(BaseModel):
    """Numerical weather forecast for a discrete target time."""

    forecast_generated_at: datetime = Field(
        ...,
        description="Model run initialization timestamp",
    )
    forecast_target_time: datetime = Field(
        ...,
        description="Projected valid timestamp for the weather conditions",
    )
    lead_time_hours: int = Field(
        ...,
        ge=0,
        description="Forecast horizon lead time in hours",
    )
    location: LocationReference = Field(..., description="Target geographical location")
    temp_min_c: float = Field(..., description="Projected minimum temperature in °C")
    temp_max_c: float = Field(..., description="Projected maximum temperature in °C")
    expected_rainfall_mm: float = Field(
        ...,
        ge=0.0,
        description="Quantitative precipitation forecast (QPF) in mm",
    )
    rainfall_probability_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Probability of precipitation (PoP) in percentage (0 - 100%)",
    )
    relative_humidity_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Projected relative humidity in %",
    )
    wind_speed_kmh: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Projected wind speed in km/h",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Forecast model metadata (e.g. IMD GFS, ECMWF)",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_forecast_timings_and_temps(self) -> "WeatherForecastPoint":
        if self.forecast_target_time < self.forecast_generated_at:
            raise ValueError(
                f"forecast_target_time ({self.forecast_target_time}) cannot precede forecast_generated_at ({self.forecast_generated_at})"
            )
        if self.temp_min_c > self.temp_max_c:
            raise ValueError(
                f"temp_min_c ({self.temp_min_c}°C) cannot exceed temp_max_c ({self.temp_max_c}°C)"
            )
        return self


class WeatherForecastSeries(BaseModel):
    """Ordered collection of sequential forecast points for a multi-day window."""

    series_id: str = Field(..., description="Unique identifier for the forecast bundle")
    generated_at: datetime = Field(..., description="Creation timestamp of the forecast package")
    location: LocationReference = Field(..., description="Target geographic jurisdiction")
    points: List[WeatherForecastPoint] = Field(
        ...,
        min_length=1,
        description="Sequential list of forecast timesteps",
    )
    source: DataSourceMetadata = Field(..., description="Forecast issuing authority / model")

    model_config = ConfigDict(extra="forbid")
