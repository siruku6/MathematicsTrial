import numpy as np
from jssp.algorithms.genetic_algorithm import crossover_by_order


class TestCrossoverByOrder:
    def test_default(self) -> None:
        np.random.seed(0)

        population_list = np.array(
            [
                [1, 2, 3, 4, 5, 6, 2, 3, 1],
                [6, 5, 3, 2, 4, 1, 3, 2, 1],
                [5, 6, 4, 2, 3, 1, 3, 2, 1],
                [1, 2, 3, 1, 2, 3, 4, 5, 6],
            ]
        )
        num_job = 6
        crossover_rate = 0.5
        parent_list, offspring_list = crossover_by_order(
            population_list=population_list,
            num_jobs=num_job,
            crossover_rate=crossover_rate,
        )

        # seed 固定しているので一致する
        expected_offsprings: np.ndarray = np.array(
            [
                [5, 2, 3, 4, 1, 6, 2, 3, 1],
                [6, 5, 3, 2, 4, 1, 3, 2, 1],
                [5, 6, 4, 2, 3, 1, 3, 2, 1],
                [2, 1, 3, 2, 1, 3, 4, 5, 6],
            ]
        )

        assert np.array_equal(parent_list, population_list)
        assert not np.array_equal(offspring_list, population_list)
        assert np.array_equal(offspring_list, expected_offsprings)
