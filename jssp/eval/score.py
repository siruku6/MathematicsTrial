import datetime
from typing import Optional, TypedDict

from eval.exec_hist_library import ExecHist, ExecHistLibrary, MarginCandidate

# 100 個の int 型要素を持つ配列
Chromosome = list[int]


class FreeTime(TypedDict):
    start_time: int
    end_time: int
    interval: int
    tool_type_id: int
    tool_id: int


def calc_time4job(
    tool_num_per_type: list[int],
    proc_time: list[list[int]],
    tool_type_seq: list[list[int]],
    num_job: int,
    num_tool_types: int,
    target_chromosome: Chromosome,
    OperationTypeMapping: Optional[dict] = None,
    hist_lib: Optional[ExecHistLibrary] = None,
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

    # 1個体の染色体を一つずつ処理
    for gene in target_chromosome:
        # 次に処理すべきタスクのID
        task_no: int = done_count_in_job[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])
        # ジョブ内タスクを担当する機械タイプのID
        m_type_id: int = int(tool_type_seq[gene][task_no])

        # 遊休時間がある機械にタスクを割り当てることを試みる
        available_margin: Optional[MarginCandidate] = None
        if (
            (hist_lib is not None)
            and (OperationTypeMapping is not None)
            and (OperationTypeMapping[gene] == "open")
        ):
            available_margin = hist_lib.search_available_margin_time(
                tool_type_id=f"tool_{m_type_id}",
                operation_type_id=gene,
                job_make_span=gen_t,
            )

        if available_margin is not None:
            start_time: int = available_margin["start_time"]
            hist_lib.insert(
                available_margin["tool_id"],
                index=available_margin["index"],
                target_hist={
                    "tool_type_id": f"tool_{m_type_id}",
                    "operation_type_id": gene,
                    "task_no": task_no,
                    "start_time": start_time,
                    "end_time": start_time + gen_t,
                },
            )

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
                time4tool[m_type_id][tool_id] = time4job[gene]
            elif time4tool[m_type_id][tool_id] > time4job[gene]:
                time4job[gene] = time4tool[m_type_id][tool_id]

            if hist_lib is not None:
                # ジョブの実行履歴を記録
                hist: ExecHist = {
                    "tool_type_id": f"tool_{m_type_id}",
                    "operation_type_id": gene,
                    "task_no": task_no,
                    "start_time": time4tool[m_type_id][tool_id] - gen_t,
                    "end_time": time4tool[m_type_id][tool_id],
                }
                hist_lib.add(tool_id=f"tool_{m_type_id}_{tool_id}", hist_dict=hist)

        done_count_in_job[gene] = done_count_in_job[gene] + 1

    if hist_lib is not None:
        hist_lib.clear()

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
    target_chromosome: Chromosome,
    OperationTypeMapping: Optional[dict] = None,
    hist_lib: Optional[ExecHistLibrary] = None,
    clear: bool = True,
) -> tuple[dict, dict, ExecHistLibrary]:
    """
    対象個体の遺伝子をスケジュールにしたときに、実際にどのくらい時間がかかるかを計算し、
    ガントチャートのデータを作成する
    """
    # カウンター類の初期化
    j_keys: list[int] = [j for j in range(num_job)]
    m_keys: list[int] = [j for j in range(0, num_tool_types)]
    # 初期化: key 番目 job のタスクが処理された回数をカウントする
    done_count_in_job = {key: 0 for key in j_keys}
    # 初期化: 各 job 内の処理済みタスクの最も遅い終了時間を格納するための辞書
    time4job = {key: 0 for key in j_keys}
    # 初期化: 各機械にかかる時間を格納するための辞書
    time4tool: dict[int, dict[int, int]] = {}
    for tool_type_id in m_keys:
        time4tool[tool_type_id + 1] = {}
        for _tool_id in range(0, tool_num_per_type[tool_type_id]):
            time4tool[tool_type_id + 1][_tool_id] = 0

    j_record: dict = {}
    # 1個体の染色体を1遺伝子ずつ処理
    for gene in target_chromosome:
        # 次に処理すべきタスクのID
        task_no: int = done_count_in_job[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])

        # ジョブ内タスクを担当する機械タイプのID
        m_type_id: int = int(tool_type_seq[gene][task_no])

        # 遊休時間がある機械にタスクを割り当てることを試みる
        available_margin: Optional[MarginCandidate] = None
        if (
            (hist_lib is not None)
            and (OperationTypeMapping is not None)
            and (OperationTypeMapping[gene] == "open")
        ):
            available_margin = hist_lib.search_available_margin_time(
                tool_type_id=f"tool_{m_type_id}",
                operation_type_id=gene,
                job_make_span=gen_t,
            )

        if available_margin is not None:
            start_time: int = available_margin["start_time"]
            hist_lib.insert(
                available_margin["tool_id"],
                index=available_margin["index"],
                target_hist={
                    "tool_type_id": f"tool_{m_type_id}",
                    "operation_type_id": gene,
                    "task_no": task_no,
                    "start_time": start_time,
                    "end_time": start_time + gen_t,
                },
            )
            tool_id: int = available_margin["tool_id"].split("_")[-1]
            end_time_sec: int = start_time + gen_t

        else:
            # タスクを担当する機械IDをここで決める (今まで処理時間が最も短い機械)
            # OPTIMIZE: ここでは、余計な待機時間が少なくて済む機械を選びたいが、暫定で単純な処理とした
            tool_id = min(time4tool[m_type_id], key=time4tool[m_type_id].get)

            # gene番目のジョブ内のタスク実行にかかった時間合計
            time4job[gene] = time4job[gene] + gen_t
            # m_type_id 番目の機械における処理時間合計
            time4tool[m_type_id][tool_id] = time4tool[m_type_id][tool_id] + gen_t

            # ジョブ毎にかかった時間、もしくは機械毎にかかった時間のうち、小さい方を、大きい方の値で上書きする
            if time4tool[m_type_id][tool_id] < time4job[gene]:
                time4tool[m_type_id][tool_id] = time4job[gene]
            elif time4tool[m_type_id][tool_id] > time4job[gene]:
                time4job[gene] = time4tool[m_type_id][tool_id]
            end_time_sec = time4job[gene]

            if hist_lib is not None:
                # ジョブの実行履歴を記録
                hist: ExecHist = {
                    "tool_type_id": f"tool_{m_type_id}",
                    "operation_type_id": gene,
                    "task_no": task_no,
                    "start_time": time4tool[m_type_id][tool_id] - gen_t,
                    "end_time": time4tool[m_type_id][tool_id],
                }
                hist_lib.add(tool_id=f"tool_{m_type_id}_{tool_id}", hist_dict=hist)

        # TODO: j_record, hist_lib の役割は似ているので、統合できるはず
        # ガントチャート集計用の記録を残す
        j_record = j_record | make_job_record(
            end_time_sec, gene, gen_t, m_type_id, tool_id, j_record
        )
        done_count_in_job[gene] = done_count_in_job[gene] + 1

    if (hist_lib is not None) and clear:
        hist_lib.clear()

    return time4job, j_record, hist_lib
