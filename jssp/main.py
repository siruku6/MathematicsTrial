import os
import time
from pathlib import Path

import pandas as pd
import plotly.figure_factory as ff
from eval.score import prepare_gannt_data_from
from genetic_algorithm import GA
from visualize import format_gannt_data

APP_ROOT_DIR: Path = Path(os.path.abspath(__file__)).parents[1]

if __name__ == "__main__":
    processing_df = pd.read_csv(
        os.path.join(APP_ROOT_DIR, "notebooks/data/jssp/Processing_time.csv")
    )
    sequence_df = pd.read_csv(
        os.path.join(APP_ROOT_DIR, "notebooks/data/jssp/Machine_sequence.csv")
    )

    processing_df = processing_df.drop(["Job"], axis=1)
    sequence_df = sequence_df.drop(["Job"], axis=1)

    num_machine_types = processing_df.shape[0]  # number of machines
    num_job = processing_df.shape[1]  # number of jobs
    num_gene = num_machine_types * num_job  # number of genes in a chromosome

    # processing_times
    proc_time = [list(map(int, processing_df.iloc[i])) for i in range(num_job)]

    # 機械タイプ
    # machine_sequences for tasks
    machine_type_seq: list[list[int]] = [
        list(map(int, sequence_df.iloc[i])) for i in range(num_job)
    ]

    # 機械タイプごとの、機械数
    machine_num_per_type: list[int] = [3, 4, 2, 1, 2, 1, 1, 3, 3, 2]

    OperationType1 = {i: "flow" for i in range(0, 5)}
    OperationType2 = {i: "open" for i in range(5, 9)}

    OperationTypeMapping: dict[int, str] = (
        OperationType1 | OperationType2 | {8: "flow", 9: "flow"}
    )
    OperationTypeMapping

    # parameter
    population_size = 100
    # num_iteration = 300  # 0
    num_iteration = 50
    crossover_rate = 0.9
    mutation_rate = 0.1
    mutation_selection_rate = 0.1
    num_mutation_jobs = round(num_gene * mutation_selection_rate)

    start_time = time.time()

    # Genetic_Algorithm
    ga = GA(
        population_size=population_size,
        num_job=num_job,
        num_machine_types=num_machine_types,
        num_gene=num_gene,
        proc_time=proc_time,
        machine_type_seq=machine_type_seq,
        machine_num_per_type=machine_num_per_type,
        OperationTypeMapping=OperationTypeMapping,
    )

    ga.run(
        num_iteration=num_iteration,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        mutation_selection_rate=mutation_selection_rate,
    )

    """----------result----------"""
    result = ga.results[-1]
    # Genetic_Algorithm()
    print("optimal solution", result["sequence_best"])
    print("optimal makespan:", result["best_make_span"])

    # plt.plot([i for i in range(len(makespan_record))], makespan_record, "b")
    # plt.ylabel("makespan", fontsize=15)
    # plt.xlabel("iteraion", fontsize=15)
    # plt.show()

    """----------visualize----------"""
    m_keys = [j for j in range(num_machine_types)]
    j_keys = [j for j in range(num_job)]

    time4machine, j_record = prepare_gannt_data_from(
        machine_num_per_type,
        proc_time,
        machine_type_seq,
        num_job,
        num_machine_types,
        result["sequence_best"],
    )

    frame_dicts: list[dict] = format_gannt_data(
        machine_num_per_type, m_keys, j_keys, j_record
    )
    fig = ff.create_gantt(
        frame_dicts,
        index_col="Resource",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        title="Job shop Schedule",
    )
    # iplot(fig, filename="GA_job_shop_scheduling")
    fig
