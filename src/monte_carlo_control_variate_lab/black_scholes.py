from __future__ import annotations

from dataclasses import dataclass
import math
import random


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


@dataclass(frozen=True)
class BlackScholesScenario:
    initial_spot: float
    risk_free_rate: float
    volatility: float
    maturity: float
    strike: float
    averaging_times: tuple[float, ...]

    def validate(self) -> None:
        if self.initial_spot <= 0.0 or self.volatility <= 0.0 or self.maturity <= 0.0:
            raise ValueError("Spot, volatility, and maturity must be positive.")
        if not self.averaging_times:
            raise ValueError("Averaging times must not be empty.")
        previous = 0.0
        for time in self.averaging_times:
            if time <= previous or time > self.maturity:
                raise ValueError("Averaging times must be increasing and within maturity.")
            previous = time

    @property
    def discount_factor(self) -> float:
        return math.exp(-self.risk_free_rate * self.maturity)

    def analytic_geometric_asian_call(self) -> float:
        self.validate()
        times = self.averaging_times
        count = len(times)
        average_time = sum(times) / count
        variance = 0.0
        for time_i in times:
            for time_j in times:
                variance += min(time_i, time_j)
        variance *= (self.volatility ** 2) / (count ** 2)
        mu_log_geometric = math.log(self.initial_spot) + (
            self.risk_free_rate - 0.5 * self.volatility ** 2
        ) * average_time
        std_log_geometric = math.sqrt(variance)

        if std_log_geometric < 1.0e-14:
            deterministic_average = math.exp(mu_log_geometric)
            return self.discount_factor * max(deterministic_average - self.strike, 0.0)

        d1 = (mu_log_geometric - math.log(self.strike) + variance) / std_log_geometric
        d2 = d1 - std_log_geometric
        return self.discount_factor * (
            math.exp(mu_log_geometric + 0.5 * variance) * normal_cdf(d1) - self.strike * normal_cdf(d2)
        )

    def simulate_payoffs(self, *, number_of_paths: int, seed: int) -> tuple[list[float], list[float]]:
        self.validate()
        rng = random.Random(seed)
        arithmetic_payoffs: list[float] = []
        geometric_payoffs: list[float] = []

        for _ in range(number_of_paths):
            spot_path = []
            previous_time = 0.0
            log_spot = math.log(self.initial_spot)
            for time in self.averaging_times:
                dt = time - previous_time
                z = rng.gauss(0.0, 1.0)
                log_spot += (
                    (self.risk_free_rate - 0.5 * self.volatility * self.volatility) * dt
                    + self.volatility * math.sqrt(dt) * z
                )
                spot = math.exp(log_spot)
                spot_path.append(spot)
                previous_time = time

            arithmetic_average = sum(spot_path) / len(spot_path)
            log_average = sum(math.log(spot) for spot in spot_path) / len(spot_path)
            geometric_average = math.exp(log_average)

            arithmetic_payoffs.append(self.discount_factor * max(arithmetic_average - self.strike, 0.0))
            geometric_payoffs.append(self.discount_factor * max(geometric_average - self.strike, 0.0))

        return arithmetic_payoffs, geometric_payoffs
