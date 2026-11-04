from datetime import date, datetime, timedelta, timezone
import pytest
from pydantic import ValidationError

from app.schemas.common import DataSourceMetadata, DataSourceType, GeoCoordinate
from app.schemas.crop import Crop, CropCategory, CroppingSeason, WaterRequirementCategory
from app.schemas.growth_stage import ActiveCropCycle, GrowthStageName, GrowthStageSpecification
from app.schemas.location import Block, District, LocationLevel, LocationReference, State, Village
from app.schemas.risk import (
    AgriculturalRiskAssessment,
    AssessmentMethodology,
    RiskCategory,
    RiskFactorContribution,
    RiskSeverityLevel,
)
from app.schemas.soil import MoistureMeasurementType, SoilMoistureReading, SoilProfile, SoilTextureClass
from app.schemas.water import GroundwaterLevelReading, ReservoirStatus, WaterDemandSupplyBalance, WaterSourceType
from app.schemas.weather import WeatherForecastPoint, WeatherForecastSeries, WeatherObservation


@pytest.fixture
def sample_source_metadata() -> DataSourceMetadata:
    return DataSourceMetadata(
        source_name="India Meteorological Department (IMD)",
        source_type=DataSourceType.OBSERVED,
        retrieved_at=datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc),
        source_record_id="IMD-AWS-43245",
        spatial_resolution_m=1000.0,
        confidence_score=0.98,
    )


@pytest.fixture
def sample_location_ref() -> LocationReference:
    return LocationReference(
        state_id="ST-TN",
        state_name="Tamil Nadu",
        district_id="DT-TNJ",
        district_name="Thanjavur",
        block_id="BK-BUD",
        block_name="Budalur",
        village_id="VL-KOV",
        village_name="Kovilpathu",
        lgd_code=638421,
        coordinates=GeoCoordinate(latitude=10.7867, longitude=79.1378, elevation_m=58.0),
    )


# 1. Common & Provenance Tests
def test_geo_coordinate_bounds():
    valid = GeoCoordinate(latitude=10.5, longitude=78.2, elevation_m=45.0)
    assert valid.latitude == 10.5

    with pytest.raises(ValidationError):
        GeoCoordinate(latitude=95.0, longitude=78.0)  # Invalid latitude

    with pytest.raises(ValidationError):
        GeoCoordinate(latitude=10.0, longitude=185.0)  # Invalid longitude


def test_data_source_metadata_refinements(sample_source_metadata):
    assert sample_source_metadata.source_record_id == "IMD-AWS-43245"
    assert sample_source_metadata.spatial_resolution_m == 1000.0

    # Test confidence score boundary
    with pytest.raises(ValidationError):
        DataSourceMetadata(
            source_name="Sensor",
            source_type=DataSourceType.OBSERVED,
            retrieved_at=datetime.now(timezone.utc),
            confidence_score=1.5,
        )


# 2. Location Tests
def test_location_hierarchy_with_lgd_codes(sample_location_ref):
    village = Village(
        id="VL-1",
        name="Kovilpathu",
        lgd_code=638421,
        total_cultivable_area_ha=320.5,
    )
    block = Block(id="BK-1", name="Budalur", lgd_code=5821, villages=[village])
    district = District(
        id="DT-1",
        name="Thanjavur",
        lgd_code=582,
        agro_climatic_zone="Cauvery Delta Zone",
        blocks=[block],
    )
    state = State(id="ST-1", name="Tamil Nadu", state_code="TN", lgd_code=33, districts=[district])

    assert state.districts[0].blocks[0].villages[0].lgd_code == 638421
    assert sample_location_ref.lgd_code == 638421


# 3. Crop Tests
def test_valid_crop_profile():
    crop = Crop(
        id="CROP-PADDY",
        name="Paddy / Rice",
        botanical_name="Oryza sativa",
        local_name_ta="நெல்",
        category=CropCategory.CEREAL,
        season=CroppingSeason.KHARIF,
        water_category=WaterRequirementCategory.VERY_HIGH,
        optimal_temp_min_c=22.0,
        optimal_temp_max_c=32.0,
        water_requirement_mm_min=1100.0,
        water_requirement_mm_max=1400.0,
        optimal_soil_ph_min=5.5,
        optimal_soil_ph_max=7.0,
        typical_maturity_days=125,
    )
    assert crop.name == "Paddy / Rice"
    assert crop.optimal_temp_min_c < crop.optimal_temp_max_c


def test_crop_invalid_temperature_range():
    with pytest.raises(ValidationError) as exc:
        Crop(
            id="CROP-INVALID",
            name="Invalid Crop",
            category=CropCategory.CEREAL,
            season=CroppingSeason.RABI,
            water_category=WaterRequirementCategory.LOW,
            optimal_temp_min_c=35.0,
            optimal_temp_max_c=20.0,  # min > max
            water_requirement_mm_min=300.0,
            water_requirement_mm_max=500.0,
            typical_maturity_days=90,
        )
    assert "optimal_temp_min_c" in str(exc.value)


# 4. Growth Stage Tests
def test_growth_stage_and_active_cycle(sample_location_ref):
    stage = GrowthStageSpecification(
        crop_id="CROP-PADDY",
        stage_name=GrowthStageName.TILLERING,
        stage_order=3,
        duration_days_min=20,
        duration_days_max=30,
        baseline_gdd_c=420.0,
        kc_coefficient=1.15,
        is_critical_water_stage=True,
    )
    assert stage.kc_coefficient == 1.15
    assert stage.is_critical_water_stage is True

    # Active cycle dates validation
    sowing = date(2026, 6, 15)
    harvest = date(2026, 10, 20)
    cycle = ActiveCropCycle(
        cycle_id="CYC-2026-001",
        crop_id="CROP-PADDY",
        location=sample_location_ref,
        sowing_date=sowing,
        current_stage=GrowthStageName.VEGETATIVE,
        estimated_harvest_date=harvest,
        area_sown_ha=12.5,
    )
    assert cycle.estimated_harvest_date > cycle.sowing_date

    with pytest.raises(ValidationError):
        ActiveCropCycle(
            cycle_id="CYC-BAD",
            crop_id="CROP-PADDY",
            location=sample_location_ref,
            sowing_date=date(2026, 6, 15),
            current_stage=GrowthStageName.VEGETATIVE,
            estimated_harvest_date=date(2026, 5, 10),  # harvest before sowing
        )


# 5. Weather Tests
def test_weather_observation_and_forecast(sample_location_ref, sample_source_metadata):
    obs = WeatherObservation(
        observation_id="OBS-9921",
        timestamp=datetime.now(timezone.utc),
        location=sample_location_ref,
        temperature_c=31.4,
        temp_min_c=24.2,
        temp_max_c=33.8,
        relative_humidity_pct=72.0,
        rainfall_mm=12.4,
        wind_speed_kmh=15.2,
        reference_et0_mm=4.6,
        source=sample_source_metadata,
    )
    assert obs.rainfall_mm == 12.4

    # Forecast point timing check
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=24)
    forecast = WeatherForecastPoint(
        forecast_generated_at=now,
        forecast_target_time=future,
        lead_time_hours=24,
        location=sample_location_ref,
        temp_min_c=23.5,
        temp_max_c=32.0,
        expected_rainfall_mm=5.0,
        rainfall_probability_pct=65.0,
        source=sample_source_metadata,
    )
    assert forecast.lead_time_hours == 24

    with pytest.raises(ValidationError):
        WeatherForecastPoint(
            forecast_generated_at=future,
            forecast_target_time=now,  # target before generation
            lead_time_hours=0,
            location=sample_location_ref,
            temp_min_c=20.0,
            temp_max_c=30.0,
            expected_rainfall_mm=0.0,
            source=sample_source_metadata,
        )


# 6. Soil Tests
def test_soil_profile_and_moisture_refinements(sample_location_ref, sample_source_metadata):
    profile = SoilProfile(
        profile_id="SP-TNJ-01",
        location=sample_location_ref,
        texture_class=SoilTextureClass.ALLUVIAL,
        ph=6.8,
        field_capacity_pct=34.0,
        wilting_point_pct=16.0,
        available_n_kg_ha=240.0,
        available_p_kg_ha=18.5,
        available_k_kg_ha=290.0,
        source=sample_source_metadata,
    )
    assert profile.field_capacity_pct > profile.wilting_point_pct

    # Wilting point must be lower than field capacity
    with pytest.raises(ValidationError):
        SoilProfile(
            profile_id="SP-INVALID",
            location=sample_location_ref,
            texture_class=SoilTextureClass.CLAY,
            ph=7.0,
            field_capacity_pct=20.0,
            wilting_point_pct=25.0,  # Invalid: wilting point > field capacity
            source=sample_source_metadata,
        )

    # Explicit measurement type validation
    reading = SoilMoistureReading(
        reading_id="SMR-001",
        timestamp=datetime.now(timezone.utc),
        location=sample_location_ref,
        depth_cm=15.0,
        measurement_type=MoistureMeasurementType.VOLUMETRIC_PERCENT,
        moisture_pct=24.5,
        plant_available_water_pct=47.2,
        source=sample_source_metadata,
    )
    assert reading.measurement_type == MoistureMeasurementType.VOLUMETRIC_PERCENT
    assert reading.depth_cm == 15.0


# 7. Water Resource Tests
def test_reservoir_and_water_balance_refinements(sample_location_ref, sample_source_metadata):
    # Reservoir capacity check
    res = ReservoirStatus(
        reservoir_id="RES-METTUR",
        name="Stanley Reservoir / Mettur Dam",
        timestamp=datetime.now(timezone.utc),
        location=sample_location_ref,
        full_reservoir_level_m=36.58,
        current_water_level_m=32.10,
        gross_capacity_tmc=93.47,
        current_storage_tmc=78.20,
        inflow_cusecs=12400.0,
        outflow_cusecs=10000.0,
        source=sample_source_metadata,
    )
    assert res.current_storage_tmc <= res.gross_capacity_tmc

    with pytest.raises(ValidationError):
        ReservoirStatus(
            reservoir_id="RES-OVERFLOW",
            name="Overflow Dam",
            timestamp=datetime.now(timezone.utc),
            location=sample_location_ref,
            full_reservoir_level_m=30.0,
            current_water_level_m=35.0,
            gross_capacity_tmc=50.0,
            current_storage_tmc=55.0,  # Exceeds gross capacity
            inflow_cusecs=100.0,
            outflow_cusecs=100.0,
            source=sample_source_metadata,
        )

    # Refinement 1: Water demand and supply balance
    balance = WaterDemandSupplyBalance(
        balance_id="WBAL-2026-Q3",
        period_start=date(2026, 7, 1),
        period_end=date(2026, 9, 30),
        location=sample_location_ref,
        crop_water_demand_mcm=180.0,
        available_surface_water_mcm=110.0,
        available_groundwater_mcm=40.0,
        water_deficit_mcm=30.0,  # 180 - (110 + 40) = 30
        source=sample_source_metadata,
    )
    assert balance.water_deficit_mcm == 30.0

    # Inconsistent deficit check
    with pytest.raises(ValidationError):
        WaterDemandSupplyBalance(
            balance_id="WBAL-BAD-DEFICIT",
            period_start=date(2026, 7, 1),
            period_end=date(2026, 9, 30),
            location=sample_location_ref,
            crop_water_demand_mcm=180.0,
            available_surface_water_mcm=110.0,
            available_groundwater_mcm=40.0,
            water_deficit_mcm=10.0,  # Inconsistent: should be 30.0
            source=sample_source_metadata,
        )

    # Inverted date period check
    with pytest.raises(ValidationError):
        WaterDemandSupplyBalance(
            balance_id="WBAL-BAD-DATES",
            period_start=date(2026, 10, 1),
            period_end=date(2026, 9, 1),  # End before start
            location=sample_location_ref,
            crop_water_demand_mcm=50.0,
            available_surface_water_mcm=25.0,
            available_groundwater_mcm=25.0,
            water_deficit_mcm=0.0,
            source=sample_source_metadata,
        )


# 8. Risk Assessment Tests
def test_risk_assessment_refinements(sample_location_ref, sample_source_metadata):
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=7)

    risk = AgriculturalRiskAssessment(
        assessment_id="RISK-2026-TNJ-001",
        assessment_timestamp=now,
        valid_until=expiry,
        methodology=AssessmentMethodology.MODEL_GENERATED,
        location=sample_location_ref,
        target_crop_id="CROP-PADDY",
        growth_stage=GrowthStageName.FLOWERING,
        primary_risk=RiskCategory.WATER_DEFICIT,
        severity=RiskSeverityLevel.HIGH,
        risk_score=78.5,
        is_verified=False,
        contributing_factors=[
            RiskFactorContribution(
                factor_name="Soil Moisture Deficit",
                contribution_weight=0.6,
                observed_value="VWC 12.1%",
                threshold_criteria="VWC < 16.0% (Wilting Point)",
            ),
            RiskFactorContribution(
                factor_name="Canal Supply Stoppage",
                contribution_weight=0.4,
                observed_value="0 cusecs for 6 days",
                threshold_criteria="Rotation schedule gap > 4 days",
            ),
        ],
        mitigation_advisory_en="Prioritize alternate wetting and drying (AWD) irrigation. Activate contingency community borewells.",
        mitigation_advisory_ta="காய்ச்சலும் பாய்ச்சலுமான மாற்றுப் பாசன முறையைக் கடைப்பிடிக்கவும்.",
        source=sample_source_metadata,
    )

    assert risk.methodology == AssessmentMethodology.MODEL_GENERATED
    assert risk.is_verified is False
    assert risk.risk_score == 78.5

    # Refinement 2: Expiration timestamp must be strictly later than assessment timestamp
    with pytest.raises(ValidationError):
        AgriculturalRiskAssessment(
            assessment_id="RISK-EXPIRED",
            assessment_timestamp=now,
            valid_until=now - timedelta(hours=1),  # Expired before creation
            methodology=AssessmentMethodology.RULE_BASED,
            location=sample_location_ref,
            primary_risk=RiskCategory.DROUGHT,
            severity=RiskSeverityLevel.LOW,
            risk_score=20.0,
            mitigation_advisory_en="Normal irrigation.",
            source=sample_source_metadata,
        )
