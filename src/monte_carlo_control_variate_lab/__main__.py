from __future__ import annotations

from pathlib import Path

from .black_scholes import BlackScholesScenario
from .experiments import DEFAULT_SCENARIO, reference_estimate, write_results_bundle


def main() -> None:
    output_root = Path(__file__).resolve().parents[2] / "results"
    records = write_results_bundle(output_root=output_root, scenario=DEFAULT_SCENARIO)
    reference = reference_estimate(DEFAULT_SCENARIO)

    print("Analytic geometric Asian call:", f"{DEFAULT_SCENARIO.analytic_geometric_asian_call():.6f}")
    print("Reference arithmetic Asian estimate (control variate):")
    print(
        f"  price={reference.control_variate.price:.6f}, se={reference.control_variate.standard_error:.6f}, "
        f"variance_reduction={reference.variance_reduction_ratio:.2f}x"
    )
    print("\nPath-count study:")
    for record in records:
        print(
            f"  n={record.number_of_paths:>6,d} | "
            f"plain_se={record.plain_standard_error:.6f} | "
            f"cv_se={record.control_variate_standard_error:.6f} | "
            f"vr={record.variance_reduction_ratio:.2f}x"
        )
    print(f"\nResults written to: {output_root}")


if __name__ == "__main__":
    main()
