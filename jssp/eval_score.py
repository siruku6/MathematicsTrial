import datetime


def make_job_record(
    time4job: dict,
    gene: int,
    process_time: int,
    m_type_id: int,
    machine_id: int,
    j_record: dict[tuple, list[str]],
) -> dict[tuple, list[str]]:
    # convert seconds to hours, minutes and seconds
    start_time: str = str(datetime.timedelta(seconds=time4job[gene] - process_time))
    end_time: str = str(datetime.timedelta(seconds=time4job[gene]))

    rec_key: tuple[int, str] = (gene, f"{m_type_id}_{machine_id}")

    if j_record.get(rec_key) is not None:
        print(rec_key, "is already in j_record, and updated.")

    return {rec_key: [start_time, end_time]}
