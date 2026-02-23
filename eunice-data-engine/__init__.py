"""eunice data engine - real gitlab data analysis for technical debt"""

__version__ = "1.0.0"

from .gitlab_client import EuniceGitLabClient
from .cost_calculator import (
    EuniceConfig,
    calculate_annual_velocity_cost,
    calculate_time_savings_only,
    calculate_carbon_footprint,
    calculate_roi,
    estimate_fix_effort
)
from .fingerprint import generate_fingerprint, deduplicate_findings

__all__ = [
    'EuniceGitLabClient',
    'EuniceConfig',
    'calculate_annual_velocity_cost',
    'calculate_time_savings_only',
    'calculate_carbon_footprint',
    'calculate_roi',
    'estimate_fix_effort',
    'generate_fingerprint',
    'deduplicate_findings',
]
