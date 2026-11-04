from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.common import DataSourceMetadata
from app.schemas.growth_stage import GrowthStageName
from app.schemas.location import LocationReference


class RiskCategory(str, Enum):
    """Categorization of agricultural threats and hazards."""

    DROUGHT = "DROUGHT"  # Meteorological, hydrological, or agricultural soil moisture drought
    FLOOD_WATERLOGGING = "FLOOD_WATERLOGGING"  # Excess precipitation, inundation, root zone asphyxiation
    HEAT_STRESS = "HEAT_STRESS"  # Extreme high temperature during sensitive reproductive stages
    PEST_OUTBREAK = "PEST_OUTBREAK"  # Entomological infestations (e.g., stem borer, fall armyworm)
    DISEASE_OUTBREAK = "DISEASE_OUTBREAK"  # Fungal, bacterial, or viral plant pathologies (e.g., blast, blight)
    WATER_DEFICIT = "WATER_DEFICIT"  # Reservoir depletion or canal closure impeding scheduled irrigation


class RiskSeverityLevel(str, Enum):
    """Graded hazard severity classification."""

    LOW = "LOW"  # Normal variability, monitoring advised
    MODERATE = "MODERATE"  # Advisory alert, non-urgent preventive measures
    HIGH = "HIGH"  # Severe hazard, active agronomic intervention required
    CRITICAL = "CRITICAL"  # Immediate threat of severe crop damage or localized crop failure


class AssessmentMethodology(str, Enum):
    """Evaluation methodology distinguishing algorithmic predictions from expert field surveys."""

    MODEL_GENERATED = "MODEL_GENERATED"  # ML/Statistical predictive model inference
    RULE_BASED = "RULE_BASED"  # Deterministic agro-meteorological threshold rules
    EXPERT_ASSESSED = "EXPERT_ASSESSED"  # Manual assessment by agricultural extension officers
    HYBRID_ENSEMBLE = "HYBRID_ENSEMBLE"  # Model output verified against rule-based expert constraints


class RiskFactorContribution(BaseModel):
    """Decomposition of an individual contributing factor to the aggregate risk score."""

    factor_name: str = Field(..., description="Name of the parameter (e.g., '14-Day Precipitation Deficit')")
    contribution_weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relative weight of this factor in the assessment model (0.0 to 1.0)",
    )
    observed_value: str = Field(
        ...,
        description="Empirical or simulated value of the factor (e.g., '-62% LPA', 'VWC 11.2%')",
    )
    threshold_criteria: Optional[str] = Field(
        default=None,
        description="Trigger benchmark or critical threshold (e.g., 'VWC < Wilting Point')",
    )

    model_config = ConfigDict(extra="forbid")


class AgriculturalRiskAssessment(BaseModel):
    """Multi-hazard agricultural risk assessment and bilingual farmer advisory.
    
    Adheres to strict data integrity: model predictions are explicitly marked
    via methodology and is_verified, never presented as unverified observed facts.
    """

    assessment_id: str = Field(..., description="Unique assessment record identifier")
    assessment_timestamp: datetime = Field(..., description="Timestamp when assessment was generated")
    valid_until: datetime = Field(..., description="Expiration timestamp of the risk advisory validity")
    methodology: AssessmentMethodology = Field(
        ...,
        description="Method used: MODEL_GENERATED, RULE_BASED, EXPERT_ASSESSED, or HYBRID_ENSEMBLE",
    )
    location: LocationReference = Field(..., description="Target administrative unit (District/Block/Village)")
    target_crop_id: Optional[str] = Field(
        default=None,
        description="Crop identifier if assessment is crop-specific; None if regional general risk",
    )
    growth_stage: Optional[GrowthStageName] = Field(
        default=None,
        description="Associated crop phenological stage if crop-specific",
    )
    primary_risk: RiskCategory = Field(..., description="Dominant primary risk category")
    severity: RiskSeverityLevel = Field(..., description="Assessed severity level")
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Normalized aggregate risk score from 0.0 (negligible) to 100.0 (catastrophic)",
    )
    is_verified: bool = Field(
        default=False,
        description="True if an agricultural officer has physically ground-truthed this prediction",
    )
    verification_notes: Optional[str] = Field(
        default=None,
        description="Field ground-truthing observations or officer notes",
    )
    contributing_factors: List[RiskFactorContribution] = Field(
        default_factory=list,
        description="Decomposition of driving risk parameters",
    )
    mitigation_advisory_en: str = Field(
        ...,
        description="Actionable mitigation advisory for farmers and district authorities in English",
    )
    mitigation_advisory_ta: Optional[str] = Field(
        default=None,
        description="Actionable mitigation advisory translated in Tamil (e.g., நீர் மேலாண்மை ஆலோசனை)",
    )
    source: DataSourceMetadata = Field(
        ...,
        description="Provenance identifying the issuing pipeline, model version, or department",
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_validity_window(self) -> "AgriculturalRiskAssessment":
        if self.valid_until <= self.assessment_timestamp:
            raise ValueError(
                f"valid_until ({self.valid_until}) must be strictly later than assessment_timestamp ({self.assessment_timestamp})"
            )
        return self
