from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import fmean, pstdev


@dataclass(frozen=True)
class EstimatorSummary:
    label: str
    price: float
    standard_error: float
    sample_std_dev: float


@dataclass(frozen=True)
class ControlVariateSummary:
    plain: EstimatorSummary
    control_variate: EstimatorSummary
    beta: float
    variance_reduction_ratio: float


def summarize_plain(payoffs: list[float], *, label: str = "Plain Monte Carlo") -> EstimatorSummary:
    mean = fmean(payoffs)
    std_dev = pstdev(payoffs)
    return EstimatorSummary(
        label=label,
        price=mean,
        standard_error=std_dev / math.sqrt(len(payoffs)),
        sample_std_dev=std_dev,
    )


def summarize_with_control_variate(
    *,
    arithmetic_payoffs: list[float],
    geometric_payoffs: list[float],
    analytic_geometric_price: float,
) -> ControlVariateSummary:
    plain_summary = summarize_plain(arithmetic_payoffs)
    mean_arithmetic = plain_summary.price
    mean_geometric = fmean(geometric_payoffs)

    covariance = fmean(
        (a - mean_arithmetic) * (g - mean_geometric)
        for a, g in zip(arithmetic_payoffs, geometric_payoffs)
    )
    geometric_variance = fmean((g - mean_geometric) ** 2 for g in geometric_payoffs)
    beta = 0.0 if geometric_variance < 1.0e-16 else covariance / geometric_variance

    adjusted_payoffs = [
        arithmetic - beta * (geometric - analytic_geometric_price)
        for arithmetic, geometric in zip(arithmetic_payoffs, geometric_payoffs)
    ]
    control_variate_summary = summarize_plain(adjusted_payoffs, label="Control Variate")
    variance_reduction = (
        float("inf")
        if control_variate_summary.sample_std_dev < 1.0e-16
        else (plain_summary.sample_std_dev ** 2) / (control_variate_summary.sample_std_dev ** 2)
    )

    return ControlVariateSummary(
        plain=plain_summary,
        control_variate=control_variate_summary,
        beta=beta,
        variance_reduction_ratio=variance_reduction,
    )
