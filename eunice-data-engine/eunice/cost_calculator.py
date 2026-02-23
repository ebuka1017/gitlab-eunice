"""cost calculations with transparent assumptions"""
import yaml
from pathlib import Path
from typing import Dict, Optional


class EuniceConfig:
    """load and expose configuration assumptions"""
    
    def __init__(self, config_path: str = "eunice.yml"):
        self.config_path = config_path
        
        if Path(config_path).exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            # use defaults if config missing
            self.config = self._get_defaults()
    
    def _get_defaults(self) -> Dict:
        """default configuration if file missing"""
        return {
            'cost_assumptions': {
                'dev_hourly_rate': 75,
                'source': 'industry average',
                'compute_cost_per_minute': 0.02,
                'runner_type': 'gitlab-saas-linux',
                'kwh_per_compute_minute': 0.000195,
                'co2_per_kwh': 0.475,
                'grid_region': 'us-east'
            },
            'effort_assumptions': {
                'avg_bug_fix_hours': 3,
                'avg_ci_failure_debug_hours': 1,
                'avg_refactor_hours_per_100_loc': 2,
                'source': 'industry benchmarks'
            },
            'thresholds': {
                'create_issue_annual_cost': 5000,
                'create_issue_roi': 50,
                'severity_threshold': 7
            }
        }
    
    @property
    def dev_rate(self) -> float:
        return self.config['cost_assumptions']['dev_hourly_rate']
    
    @property
    def compute_cost_per_min(self) -> float:
        return self.config['cost_assumptions']['compute_cost_per_minute']
    
    @property
    def avg_bug_fix_hours(self) -> float:
        return self.config['effort_assumptions']['avg_bug_fix_hours']
    
    @property
    def avg_ci_failure_hours(self) -> float:
        return self.config['effort_assumptions']['avg_ci_failure_debug_hours']
    
    @property
    def assumptions_metadata(self) -> Dict:
        """return all assumptions with sources"""
        return {
            'cost_assumptions': self.config['cost_assumptions'],
            'effort_assumptions': self.config['effort_assumptions']
        }
    
    def should_create_issue(self, annual_cost: float, roi: float) -> bool:
        """check if issue should be created based on thresholds"""
        cost_threshold = self.config['thresholds']['create_issue_annual_cost']
        roi_threshold = self.config['thresholds']['create_issue_roi']
        
        return annual_cost >= cost_threshold or roi >= roi_threshold


def calculate_annual_velocity_cost(
    commit_count_monthly: int,
    avg_review_time_minutes: float,
    bug_hours_tracked: float,
    ci_failure_count_monthly: int,
    config: EuniceConfig,
    bug_hours_window_days: int = 30
) -> Dict:
    """
    calculate annual velocity cost
    
    measured inputs (gitlab):
    - commit_count_monthly: actual commits from api
    - avg_review_time_minutes: mr.merged_at - mr.created_at
    - bug_hours_tracked: sum of time_stats.total_time_spent
    - ci_failure_count_monthly: count of failed pipelines
    
    assumptions (config):
    - dev_hourly_rate: from eunice.yml
    - avg_ci_failure_debug_hours: from eunice.yml
    """
    
    # review overhead (measured activity × config rate)
    monthly_review_hours = (commit_count_monthly * avg_review_time_minutes) / 60
    monthly_review_cost = monthly_review_hours * config.dev_rate
    
    # bug fix cost (annualize measured window to match annualized review/ci metrics)
    if bug_hours_window_days <= 0:
        bug_hours_window_days = 30
    annualized_bug_hours = bug_hours_tracked * (365 / bug_hours_window_days)
    annual_bug_cost = annualized_bug_hours * config.dev_rate
    
    # ci failure debugging (measured failures × config estimate × rate)
    monthly_ci_hours = ci_failure_count_monthly * config.avg_ci_failure_hours
    monthly_ci_cost = monthly_ci_hours * config.dev_rate
    
    # totals
    annual_cost = (
        (monthly_review_cost * 12) +
        annual_bug_cost +
        (monthly_ci_cost * 12)
    )
    
    return {
        'annual_cost_usd': round(annual_cost, 2),
        'breakdown_usd': {
            'review_overhead': round(monthly_review_cost * 12, 2),
            'bug_fixes': round(annual_bug_cost, 2),
            'ci_failures': round(monthly_ci_cost * 12, 2)
        },
        'measured_inputs': {
            'commits_per_month': commit_count_monthly,
            'avg_review_minutes': round(avg_review_time_minutes, 2),
            'bug_hours_tracked': round(bug_hours_tracked, 2),
            'ci_failures_per_month': ci_failure_count_monthly
        },
        'assumptions_used': {
            'dev_hourly_rate_usd': config.dev_rate,
            'avg_ci_failure_debug_hours': config.avg_ci_failure_hours,
            'bug_hours_window_days': bug_hours_window_days,
            'source': config.config['cost_assumptions']['source']
        }
    }


def calculate_time_savings_only(
    commit_count_monthly: int,
    avg_review_time_minutes: float,
    bug_hours_tracked: float,
    ci_failure_count_monthly: int,
    config: EuniceConfig,
    bug_hours_window_days: int = 30
) -> Dict:
    """
    calculate savings in hours (no dollar conversion)
    use this if user doesn't want dollar assumptions
    """
    
    monthly_review_hours = (commit_count_monthly * avg_review_time_minutes) / 60
    monthly_ci_hours = ci_failure_count_monthly * config.avg_ci_failure_hours
    
    if bug_hours_window_days <= 0:
        bug_hours_window_days = 30
    annualized_bug_hours = bug_hours_tracked * (365 / bug_hours_window_days)

    annual_hours = (
        (monthly_review_hours * 12) + 
        annualized_bug_hours + 
        (monthly_ci_hours * 12)
    )
    
    return {
        'annual_hours_saved': round(annual_hours, 1),
        'breakdown_hours': {
            'review_overhead': round(monthly_review_hours * 12, 1),
            'bug_fixes': round(annualized_bug_hours, 1),
            'ci_failures': round(monthly_ci_hours * 12, 1)
        },
        'measured_inputs': {
            'commits_per_month': commit_count_monthly,
            'avg_review_minutes': round(avg_review_time_minutes, 2),
            'bug_hours_tracked': round(bug_hours_tracked, 2),
            'ci_failures_per_month': ci_failure_count_monthly
        },
        'assumptions_used': {
            'bug_hours_window_days': bug_hours_window_days
        }
    }


def calculate_carbon_footprint(
    avg_pipeline_duration_minutes: float,
    monthly_pipeline_count: int,
    config: EuniceConfig
) -> Dict:
    """
    calculate carbon footprint
    
    measured (gitlab):
    - avg_pipeline_duration_minutes: from pipeline.duration
    - monthly_pipeline_count: count of pipelines
    
    modeled (config):
    - kwh_per_compute_minute: from carbon model
    - co2_per_kwh: from grid region
    """
    
    monthly_compute_minutes = avg_pipeline_duration_minutes * monthly_pipeline_count
    
    kwh_per_min = config.config['cost_assumptions']['kwh_per_compute_minute']
    co2_per_kwh = config.config['cost_assumptions']['co2_per_kwh']
    
    monthly_kwh = monthly_compute_minutes * kwh_per_min
    monthly_co2_kg = monthly_kwh * co2_per_kwh
    
    return {
        'annual_co2_kg': round(monthly_co2_kg * 12, 2),
        'annual_kwh': round(monthly_kwh * 12, 2),
        'measured_inputs': {
            'avg_pipeline_minutes': round(avg_pipeline_duration_minutes, 2),
            'pipelines_per_month': monthly_pipeline_count,
            'monthly_compute_minutes': round(monthly_compute_minutes, 2)
        },
        'carbon_model_used': {
            'kwh_per_minute': kwh_per_min,
            'co2_per_kwh': co2_per_kwh,
            'grid_region': config.config['cost_assumptions']['grid_region'],
            'source': config.config['cost_assumptions']['source']
        },
        'note': 'carbon is modeled conversion, not direct measurement'
    }


def calculate_roi(
    annual_savings: float,
    effort_hours: float,
    config: EuniceConfig
) -> Dict:
    """calculate return on investment"""
    
    effort_cost = effort_hours * config.dev_rate
    roi = annual_savings / effort_cost if effort_cost > 0 else 0
    payback_days = (effort_cost / annual_savings * 365) if annual_savings > 0 else 999
    
    return {
        'roi': round(roi, 1),
        'effort_cost_usd': round(effort_cost, 2),
        'effort_hours': effort_hours,
        'annual_savings_usd': round(annual_savings, 2),
        'payback_days': round(payback_days, 1),
        'priority_score': min(10, roi / 10)  # normalize to 1-10
    }


def estimate_fix_effort(lines_of_code: int, config: EuniceConfig) -> float:
    """estimate fix effort based on lines of code"""
    hours_per_100_loc = config.config['effort_assumptions']['avg_refactor_hours_per_100_loc']
    return (lines_of_code / 100) * hours_per_100_loc
