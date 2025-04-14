def read_benchmark_task_data(
    benchmark_data_path: str,
) -> tuple[list[list[int]], list[list[str]]]:
    with open(benchmark_data_path, "r") as f:
        la40_data: list = [line.rstrip("\n").split("\t") for line in f.readlines()]

    num_machines: str
    num_jobs: str
    num_jobs, num_machines = la40_data[0]
    # print(la40_data[0], num_machines)

    raw_processing_time_per_job: list[list[str]] = la40_data[1 : 1 + int(num_jobs)]
    # processing_time_per_job (2次元配列) の値を int に変換
    processing_time_per_job: list[list[int]] = [
        [int(processing_time) for processing_time in processing_times]
        for processing_times in raw_processing_time_per_job
    ]

    machine_sequence_per_job: list[list[str]] = la40_data[
        1 + int(num_jobs) : 1 + int(num_jobs) * 2
    ]
    # machine_sequence_per_job (2次元配列) の値を int に変換
    machine_sequence_per_job: list[list[int]] = [
        [int(machine_sequence) for machine_sequence in machine_sequences]
        for machine_sequences in machine_sequence_per_job
    ]

    return processing_time_per_job, machine_sequence_per_job
