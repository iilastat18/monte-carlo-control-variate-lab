import unittest

from monte_carlo_control_variate_lab.black_scholes import BlackScholesScenario
from monte_carlo_control_variate_lab.experiments import DEFAULT_SCENARIO
from monte_carlo_control_variate_lab.estimators import summarize_with_control_variate


class ControlVariateTests(unittest.TestCase):
    def test_geometric_asian_analytic_matches_monte_carlo(self) -> None:
        scenario = DEFAULT_SCENARIO
        arithmetic, geometric = scenario.simulate_payoffs(number_of_paths=80_000, seed=11)
        summary = summarize_with_control_variate(
            arithmetic_payoffs=arithmetic,
            geometric_payoffs=geometric,
            analytic_geometric_price=scenario.analytic_geometric_asian_call(),
        )
        simulated_geometric_mean = sum(geometric) / len(geometric)
        self.assertLess(abs(simulated_geometric_mean - scenario.analytic_geometric_asian_call()), 0.05)
        self.assertGreater(summary.beta, 0.0)

    def test_control_variate_reduces_standard_error(self) -> None:
        arithmetic, geometric = DEFAULT_SCENARIO.simulate_payoffs(number_of_paths=20_000, seed=21)
        summary = summarize_with_control_variate(
            arithmetic_payoffs=arithmetic,
            geometric_payoffs=geometric,
            analytic_geometric_price=DEFAULT_SCENARIO.analytic_geometric_asian_call(),
        )
        self.assertLess(summary.control_variate.standard_error, summary.plain.standard_error)
        self.assertGreater(summary.variance_reduction_ratio, 2.0)


if __name__ == "__main__":
    unittest.main()
