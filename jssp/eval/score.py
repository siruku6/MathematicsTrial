import datetime
from typing import Optional, TypedDict, Union

# 100 個の int 型要素を持つ配列
Chromosome = list[int]


class FreeTime(TypedDict):
    start_time: int
    end_time: int
    interval: int
    tool_type_id: int
    tool_id: int


def assign_task_to_free_time(
    gene: int,
    free_times: list,
    m_type_id: int,
    gen_t: int,
    OperationTypeMapping: Optional[dict] = None,
) -> dict[str, Union[bool, list, Optional[int], FreeTime]]:
    occupied_free_time: Optional[FreeTime] = {}

    if (OperationTypeMapping is not None) and (OperationTypeMapping[gene] == "open"):
        # タスク実行可能な空き時間を抽出
        available_free_times: list = [
            free_time
            for free_time in free_times
            if (
                (free_time["tool_type_id"] == m_type_id)
                and (free_time["interval"] >= gen_t)
            )
        ].copy()

        tool_id: Optional[int] = None
        if len(available_free_times) > 0:
            # タスクを処理させる空き時間、担当する機械IDを決める
            occupied_free_time = sorted(
                available_free_times,
                key=lambda free_time: free_time["interval"],
            )[0]  # interval が最も短いものを選ぶ
            tool_id = occupied_free_time["tool_id"]
            # 占められた空き時間を、 free_times から削除
            free_times.remove(occupied_free_time)

    else:
        available_free_times = []
        tool_id = None

    return {
        "success": len(available_free_times) > 0,
        "remained_free_times": free_times,
        "tool_id": tool_id,
        "occupied_free_time": occupied_free_time,
    }


def calc_time4job(
    tool_num_per_type: list[int],
    proc_time: list[list[int]],
    tool_type_seq: list[list[int]],
    num_job: int,
    num_tool_types: int,
    target_chromosome: Chromosome,
    OperationTypeMapping: Optional[dict] = None,
) -> dict[int, int]:
    """
    対象個体の遺伝子をスケジュールにしたときに、実際にどのくらい時間がかかるかを計算する

    len(target_chromosome) => num_job * num_tool_types
    """
    j_keys: list[int] = [j for j in range(num_job)]
    m_keys: list[int] = [j for j in range(0, num_tool_types)]

    # 初期化: key 番目 job のタスクが処理された回数をカウントする
    done_count_in_job: dict[int, int] = {job: 0 for job in j_keys}

    # 初期化: 各 job 内の処理済みタスクの最も遅い終了時間を格納するための辞書
    time4job: dict[int, int] = {job: 0 for job in j_keys}

    # 初期化: 各機械にかかる時間を格納するための辞書
    time4tool: dict[int, dict[int, int]] = {}
    for tool_type_id in m_keys:
        time4tool[tool_type_id + 1] = {}
        for _tool_id in range(0, tool_num_per_type[tool_type_id]):
            time4tool[tool_type_id + 1][_tool_id] = 0

    # いずれかの機械が空いている時間を格納しておく辞書
    free_times: list[FreeTime] = []
    # 1個体の染色体を一つずつ処理
    for gene in target_chromosome:
        # 次に処理すべきタスクのID
        task_no: int = done_count_in_job[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])
        # ジョブ内タスクを担当する機械タイプのID
        m_type_id: int = int(tool_type_seq[gene][task_no])

        # 遊休時間がある機械にタスクを割り当てることを試みる
        assign_result: dict = assign_task_to_free_time(
            gene,
            free_times=free_times,
            m_type_id=m_type_id,
            gen_t=gen_t,
            OperationTypeMapping=OperationTypeMapping,
        )

        if assign_result["success"]:
            free_times = assign_result["remained_free_times"]
            tool_id = assign_result["tool_id"]
        # タスクを担当する機械ID決める (今まで処理時間が最も短い機械)
        else:
            # OPTIMIZE: ここでは、余計な待機時間が少なくて済む機械を選びたいが、暫定で単純な処理とした
            tool_id = min(time4tool[m_type_id], key=time4tool[m_type_id].get)

            # gene番目のジョブ内のタスク実行にかかった時間合計
            time4job[gene] = time4job[gene] + gen_t

            # m_type_id 番目の機械における処理時間合計
            time4tool[m_type_id][tool_id] = time4tool[m_type_id][tool_id] + gen_t

            # ジョブ毎にかかった時間、もしくは機械毎にかかった時間のうち、小さい方を、大きい方の値で上書きする
            if time4tool[m_type_id][tool_id] < time4job[gene]:
                # 空き時間を記録しておく
                free_times.append(
                    {
                        "start_time": time4tool[m_type_id][tool_id],
                        "end_time": time4job[gene],
                        "interval": time4job[gene] - time4tool[m_type_id][tool_id],
                        "tool_type_id": m_type_id,
                        "tool_id": tool_id,
                    }
                )
                time4tool[m_type_id][tool_id] = time4job[gene]
            elif time4tool[m_type_id][tool_id] > time4job[gene]:
                time4job[gene] = time4tool[m_type_id][tool_id]

        done_count_in_job[gene] = done_count_in_job[gene] + 1

    return time4job


def make_job_record(
    end_time_sec: int,
    gene: int,
    process_time: int,
    m_type_id: int,
    tool_id: int,
    j_record: dict[tuple, list[str]],
) -> dict[tuple, list[str]]:
    # convert seconds to hours, minutes and seconds
    start_time: str = str(datetime.timedelta(seconds=end_time_sec - process_time))
    end_time: str = str(datetime.timedelta(seconds=end_time_sec))

    rec_key: tuple[int, str] = (gene, f"{m_type_id}_{tool_id}")

    if j_record.get(rec_key) is not None:
        print(rec_key, "is already in j_record, and updated.")

    return {rec_key: [start_time, end_time]}


def prepare_gannt_data_from(
    tool_num_per_type: list[int],  # 0~9
    proc_time: list[list[int]],
    tool_type_seq: list[list[int]],
    num_job: int,
    num_tool_types: int,
    sequence_best: Chromosome,
    OperationTypeMapping: Optional[dict] = None,
) -> tuple[dict, dict]:
    # カウンター類の初期化
    j_keys: list[int] = [j for j in range(num_job)]
    m_keys: list[int] = [j for j in range(0, num_tool_types)]

    done_count_in_job = {key: 0 for key in j_keys}
    time4job = {key: 0 for key in j_keys}
    time4tool: dict[int, dict[int, int]] = {}
    for tool_type_id in m_keys:
        time4tool[tool_type_id + 1] = {}
        for _tool_id in range(0, tool_num_per_type[tool_type_id]):
            time4tool[tool_type_id + 1][_tool_id] = 0
    free_times: list[FreeTime] = []

    j_record: dict = {}
    for gene in sequence_best:
        # 次に処理すべきタスクのID
        task_no: int = done_count_in_job[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])

        # ジョブ内タスクを担当する機械タイプのID
        m_type_id: int = int(tool_type_seq[gene][task_no])

        # 遊休時間がある機械にタスクを割り当てることを試みる
        assign_result: dict = assign_task_to_free_time(
            gene,
            free_times=free_times,
            m_type_id=m_type_id,
            gen_t=gen_t,
            OperationTypeMapping=OperationTypeMapping,
        )
        if assign_result["success"]:
            free_times = assign_result["remained_free_times"]
            tool_id: int = assign_result["tool_id"]
            end_time_sec: int = assign_result["occupied_free_time"]["end_time"]
        else:
            # タスクを担当する機械IDをここで決める (今まで処理時間が最も短い機械)
            tool_id = min(time4tool[m_type_id], key=time4tool[m_type_id].get)

            time4job[gene] = time4job[gene] + gen_t
            time4tool[m_type_id][tool_id] = time4tool[m_type_id][tool_id] + gen_t

            if time4tool[m_type_id][tool_id] < time4job[gene]:
                # 空き時間を記録しておく
                free_times.append(
                    {
                        "start_time": time4tool[m_type_id][tool_id],
                        "end_time": time4job[gene],
                        "interval": time4job[gene] - time4tool[m_type_id][tool_id],
                        "tool_type_id": m_type_id,
                        "tool_id": tool_id,
                    }
                )
                time4tool[m_type_id][tool_id] = time4job[gene]
            elif time4tool[m_type_id][tool_id] > time4job[gene]:
                time4job[gene] = time4tool[m_type_id][tool_id]
            end_time_sec = time4job[gene]

        # 記録を残す
        j_record = j_record | make_job_record(
            end_time_sec, gene, gen_t, m_type_id, tool_id, j_record
        )
        done_count_in_job[gene] = done_count_in_job[gene] + 1

    return time4job, j_record
