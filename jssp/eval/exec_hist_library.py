"""
各マシンへのジョブ割り当て履歴を管理する
(個体の遺伝子から表現型を作成する)

スコア評価において、
SetupTime や Open なジョブを割り当てるために必要
"""

from typing import Optional, TypedDict


class ExecHist(TypedDict):
    # job_series_num: int
    tool_type_id: str
    task_no: int
    operation_type_id: int
    job_make_span: Optional[int]
    start_time: int
    end_time: int


class MarginCandidate(TypedDict):
    tool_id: str
    index: int
    margin_time: int
    start_time: int


class ToolTypeInfo(TypedDict):
    setup_time: int


class ToolInfo(TypedDict):
    tool_id: int
    tool_type_id: int
    setup_time: int


class ExecHistLibrary:
    def __init__(self, tool_type_info: dict[str, ToolTypeInfo]) -> None:
        self.hist: dict[str, list[ExecHist]] = {}  # 表現型
        # setup_time 情報が入っている
        self.tool_type_info: dict[str, ToolTypeInfo] = tool_type_info

    def clear(self) -> None:
        self.hist = {}

    def add(
        self,
        tool_id: str,
        hist_dict: ExecHist,
    ) -> None:
        if tool_id not in self.hist:
            self.hist[tool_id] = []

        self.hist[tool_id].append(hist_dict)

    def insert(self, tool_id: str, index: int, target_hist: ExecHist) -> None:
        if tool_id not in self.hist:
            self.hist[tool_id] = [target_hist]
            return

        self.hist[tool_id].insert(index, target_hist)

    def search_available_margin_time(
        self,
        tool_type_id: str,
        operation_type_id: int,
        job_make_span: int,
    ) -> Optional[MarginCandidate]:
        """
        Parameters
        ------
        tool_type_id: str
            マシン種別ID ("tool_1", "tool_2", ...)
        operation_type_id: int
            ジョブの種別ID (1("A"), 2("B"), ...)
        job_make_span: int
            ジョブの所要時間

        Returns
        ------
        margin_candidate: Optional[MarginCandidate]
            猶予時間が最小のマシンの情報
        """
        margin_candidates: list[MarginCandidate] = []

        # 全てのマシンの動作履歴から、空き時間を探索する
        for tool_id, hists in self.hist.items():
            target_tool_type_id: str = "_".join(tool_id.split("_")[:-1])
            if not tool_type_id == target_tool_type_id:
                continue

            for index, hist in enumerate(hists[:-1]):
                prev_end_time: int = hist["end_time"]
                next_start_time: int = hists[index + 1]["start_time"]
                prev_tool_type_id: str = hist["tool_type_id"]
                prev_operation_type_id: int = hist["operation_type_id"]
                next_operation_type_id: int = hists[index + 1]["operation_type_id"]

                prev_setup_time: int = 0
                setup_time: int = 0
                # operation_type_id が異なる場合
                if not prev_operation_type_id == operation_type_id:
                    prev_setup_time = self.tool_type_info[prev_tool_type_id][
                        "setup_time"
                    ]
                if not operation_type_id == next_operation_type_id:
                    setup_time = self.tool_type_info[tool_type_id]["setup_time"]

                # 猶予時間
                margin_time: int = (
                    next_start_time - setup_time - prev_setup_time - prev_end_time
                    # next_start_time - prev_end_time
                )
                if job_make_span < margin_time:
                    margin_candidates.append(
                        {
                            "tool_id": tool_id,
                            "index": index + 1,  # insert する場合の位置
                            "margin_time": margin_time,
                            "start_time": prev_end_time + prev_setup_time,
                        }
                    )

        # 猶予時間が最小のものを返す
        if len(margin_candidates) == 0:
            return None

        min_margin: MarginCandidate = min(
            margin_candidates,  # type: ignore
            key=lambda margin: margin["margin_time"],
        )
        return min_margin
