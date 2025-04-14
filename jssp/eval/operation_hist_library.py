"""
各マシンへのジョブ割り当て履歴を管理する
(個体の遺伝子から表現型を作成する)

異なるジョブであれば、マシンの空いている時間帯に割り当てられるように、
各マシンのジョブ割り当て履歴を管理する
"""

from typing import Optional, TypedDict


class OperationHist(TypedDict):
    operation_id: int
    operation_make_span: Optional[int]
    start_time: int
    end_time: int


class MarginCandidate(TypedDict):
    tool_id: str
    index: int
    margin_time: int
    start_time: int


class OperationHistLibrary:
    def __init__(self) -> None:
        self.operation_hist: dict[str, list[OperationHist]] = {}  # 表現型

    def clear(self) -> None:
        self.operation_hist = {}  # deepcopy(self.maintenance_dict)

    def add(
        self,
        tool_id: str,
        hist_dict: OperationHist,
    ) -> None:
        if tool_id not in self.operation_hist:
            self.operation_hist[tool_id] = []

        self.operation_hist[tool_id].append(hist_dict)

    def insert(self, tool_id: str, index: int, target_hist: OperationHist) -> None:
        if tool_id not in self.operation_hist:
            self.operation_hist[tool_id] = [target_hist]
            return

        self.operation_hist[tool_id].insert(index, target_hist)

    # def get_last_hist_ope_type(self, tool_id: str) -> int:
    #     if tool_id not in self.operation_hist:
    #         return -1

    #     # NOTE: メンテナンスタイムを除外
    #     target_hists: list[OperationHist] = [
    #         hist for hist in self.operation_hist[tool_id] if hist["operation_id"] != -1
    #     ]
    #     if len(self.operation_hist) == 0:
    #         return -1

    #     last_hist_ope_type: int = target_hists[-1]["operation_type_id"]
    #     return last_hist_ope_type

    def dummy_zero_hist(self) -> OperationHist:
        return OperationHist(
            start_time=0,
            end_time=0,
            operation_id=-1,
            operation_make_span=0,
        )

    def _search_available_margin_time_for_a_tool(
        self,
        hists: list[OperationHist],
        # operation_type_id: int,
        tool_id: str,
        task_make_span: int,
        margin_candidates: list[MarginCandidate],
        earliest_start_able_time: int,
    ) -> list[MarginCandidate]:

        # ある tool_id における、全てのジョブの動作履歴を探索
        for index, next_hist in enumerate(hists):
            if index == 0:
                prev_hist: OperationHist = self.dummy_zero_hist()
            else:
                prev_hist = hists[index - 1]

            prev_end_time: int = prev_hist["end_time"]
            next_start_time: int = next_hist["start_time"]

            # 猶予時間
            earliest_start_able_time = max(earliest_start_able_time, prev_end_time)
            margin_time: int = (next_start_time - earliest_start_able_time)
            if task_make_span <= margin_time:
                margin_candidates.append(
                    {
                        "tool_id": tool_id,
                        "index": index,  # insert する場合の位置
                        "margin_time": margin_time,
                        "start_time": earliest_start_able_time,
                    }
                )
        return margin_candidates

    def search_available_margin_time(
        self,
        tool_id: str,
        # operation_type_id: int,
        task_make_span: int,
        earliest_start_able_time: int,
    ) -> Optional[MarginCandidate]:
        """
        Parameters
        ------
        tool_id: str
            マシンID ("tool_1", "tool_2", ...)
        # operation_type_id: int
        #     ジョブの種別ID (1("A"), 2("B"), ...)
        task_make_span: int
            該当タスクの所要時間
        earliest_start_able_time: int
            ジョブ内該当タスクの開始可能時刻

        Returns
        ------
        margin_candidate: Optional[MarginCandidate]
            猶予時間が最小のマシンの情報
        """
        margin_candidates: list[MarginCandidate] = []

        # 該当 tool_id における、全てのジョブの動作履歴を取得
        tool_operations_hist: list[OperationHist] = self.operation_hist.get(tool_id, [])
        # 全てのマシンの動作履歴から、空き時間を探索する
        # for tool_id, hists in self.operation_hist.items():
        #     target_tool_type_id: str = "_".join(tool_id.split("_")[:-1])
        #     if not tool_type_id == target_tool_type_id:
        #         continue

        # ある tool_id における、空き時間を探索
        margin_candidates += self._search_available_margin_time_for_a_tool(
            tool_operations_hist,
            # operation_type_id,
            tool_id,
            task_make_span,
            margin_candidates,
            earliest_start_able_time,
        )

        # 猶予時間が最小のものを返す
        if len(margin_candidates) == 0:
            return None

        min_margin: MarginCandidate = min(
            margin_candidates,  # type: ignore
            key=lambda margin: margin["margin_time"],
        )
        return min_margin
