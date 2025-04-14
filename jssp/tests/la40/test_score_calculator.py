import pytest
from la40.score_calculator import ScoreCalculator
from utils.types import Chromosome


class TestCalcTime4Job:
    @pytest.fixture
    def fixture_sda(self):
        pass

    def test_easy_jssp(self) -> None:
        processing_times = [[1, 2, 3], [6, 5, 4], [7, 8, 9]]
        machine_sequence = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]

        calculator: ScoreCalculator = ScoreCalculator(
            processing_times, machine_sequence
        )

        chromosome: Chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        job_makespans: dict[int, int] = calculator.calc_time4job(chromosome)
        excpected: dict[int, int] = {0: 6, 1: 15, 2: 24}
        assert job_makespans == excpected
        assert max(job_makespans.values()) == 24
