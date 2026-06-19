from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
from pathlib import Path

from .black_scholes import BlackScholesScenario
from .charts import write_bar_chart_svg, write_line_chart_svg
from .estimators import ControlVariateSummary, summarize_with_control_variate


DEFAULT_SCENARIO = BlackScholesScenario(
    initial_spot=100.0,
    risk_free_rate=0.05,
    volatility=0.30,
    maturity=1.0,
    strike=100.0,
    averaging_times=(0.25, 0.50, 0.75, 1.00),
)


@dataclass(frozen=True)
class PathCountRecord:
    number_of_paths: int
    plain_price: float
    plain_standard_error: float
    control_variate_price: float
    control_variate_standard_error: float
    beta: float
    variance_reduction_ratio: float


def path_count_study(
    scenario: BlackScholesScenario = DEFAULT_SCENARIO,
    *,
    path_counts: tuple[int, ...] = (2_000, 5_000, 10_000, 25_000, 50_000, 100_000),
    seed_base: int = 200,
) -> list[PathCountRecord]:
    records: list[PathCountRecord] = []
    analytic_geometric = scenario.analytic_geometric_asian_call()

    for index, number_of_paths in enumerate(path_counts):
        arithmetic, geometric = scenario.simulate_payoffs(number_of_paths=number_of_paths, seed=seed_base + index)
        summary = summarize_with_control_variate(
            arithmetic_payoffs=arithmetic,
            geometric_payoffs=geometric,
            analytic_geometric_price=analytic_geometric,
        )
        records.append(
            PathCountRecord(
                number_of_paths=number_of_paths,
                plain_price=summary.plain.price,
                plain_standard_error=summary.plain.standard_error,
                control_variate_price=summary.control_variate.price,
                control_variate_standard_error=summary.control_variate.standard_error,
                beta=summary.beta,
                variance_reduction_ratio=summary.variance_reduction_ratio,
            )
        )

    return records


def reference_estimate(
    scenario: BlackScholesScenario = DEFAULT_SCENARIO,
    *,
    number_of_paths: int = 300_000,
    seed: int = 999,
) -> ControlVariateSummary:
    arithmetic, geometric = scenario.simulate_payoffs(number_of_paths=number_of_paths, seed=seed)
    return summarize_with_control_variate(
        arithmetic_payoffs=arithmetic,
        geometric_payoffs=geometric,
        analytic_geometric_price=scenario.analytic_geometric_asian_call(),
    )


def write_results_bundle(
    *,
    output_root: Path,
    scenario: BlackScholesScenario = DEFAULT_SCENARIO,
) -> list[PathCountRecord]:
    output_root.mkdir(parents=True, exist_ok=True)
    records = path_count_study(scenario)
    reference = reference_estimate(scenario)

    _write_csv(
        output_root / "path_count_study.csv",
        rows=[
            {
                "number_of_paths": str(record.number_of_paths),
                "plain_price": f"{record.plain_price:.8f}",
                "plain_standard_error": f"{record.plain_standard_error:.8f}",
                "control_variate_price": f"{record.control_variate_price:.8f}",
                "control_variate_standard_error": f"{record.control_variate_standard_error:.8f}",
                "beta": f"{record.beta:.8f}",
                "variance_reduction_ratio": f"{record.variance_reduction_ratio:.4f}",
            }
            for record in records
        ],
    )
    (output_root / "path_count_study.json").write_text(
        json.dumps([asdict(record) for record in records], indent=2),
        encoding="utf-8",
    )
    (output_root / "reference_estimate.json").write_text(
        json.dumps(
            {
                "plain_price": reference.plain.price,
                "plain_standard_error": reference.plain.standard_error,
                "control_variate_price": reference.control_variate.price,
                "control_variate_standard_error": reference.control_variate.standard_error,
                "beta": reference.beta,
                "variance_reduction_ratio": reference.variance_reduction_ratio,
                "analytic_geometric_price": scenario.analytic_geometric_asian_call(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    write_line_chart_svg(
        title="Monte Carlo Standard Error By Path Count",
        subtitle="The control variate tracks the same arithmetic Asian payoff while materially reducing estimator noise.",
        x_values=[float(record.number_of_paths) for record in records],
        left_values=[record.plain_standard_error for record in records],
        right_values=[record.control_variate_standard_error for record in records],
        left_label="Plain Monte Carlo",
        right_label="Control Variate",
        output_path=output_root / "standard_error_comparison.svg",
    )
    write_bar_chart_svg(
        title="Variance Reduction Factor",
        subtitle="Variance-reduction ratio = plain-variance / control-variate-variance for the same number of paths.",
        categories=[f"{record.number_of_paths // 1000}k" if record.number_of_paths >= 1000 else str(record.number_of_paths) for record in records],
        values=[record.variance_reduction_ratio for record in records],
        output_path=output_root / "variance_reduction_ratio.svg",
    )
    return records


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
