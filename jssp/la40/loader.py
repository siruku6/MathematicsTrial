def read_benchmark_task_data(benchmark_data_path: str) -> tuple[list[str], list[str]]:
    with open(benchmark_data_path, "r") as f:
        la40_data: list = [line.rstrip("\n").split("\t") for line in f.readlines()]

    num_machines: str
    num_jobs: str
    num_jobs, num_machines = la40_data[0]
    # print(la40_data[0], num_machines)

    processing_time_per_job: list[str] = la40_data[1 : 1 + int(num_jobs)]
    machine_sequence_per_job: list[str] = la40_data[
        1 + int(num_jobs) : 1 + int(num_jobs) * 2
    ]
    return processing_time_per_job, machine_sequence_per_job
