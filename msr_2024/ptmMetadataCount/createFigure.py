from typing import Hashable, List

import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import XKCD_COLORS
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

FONTSIZE: int = 12


def main() -> None:
    modelTasks: List[str] = []
    counts: List[int] = []
    data: dict[str, List[str | int]] = {}

    df: DataFrame = pandas.read_json(
        path_or_buf="../../data/countMetadataPerPTM.json"
    ).T

    print(df.columns)

    dfs: DataFrameGroupBy = df.groupby(by="task")

    foo: tuple[Hashable, DataFrame]
    for foo in dfs:
        foo[1].drop(columns=["task", "modelID"], inplace=True)
        count: float = foo[1].sum(axis=1).sum()

        modelTasks.append(str(foo[0]))
        counts.append(int(count))

    data["tasks"] = modelTasks
    data["count"] = counts

    df: DataFrame = DataFrame(data=data)
    print(df)
    quit()

    plt.figure(figsize=(18, 9))
    for idx, value in enumerate(df["project_count"]):
        plt.bar(
            df["task_name"][idx],
            value,
            color=list(XKCD_COLORS.values())[idx],
            label=f'{df["task_name"][idx]}',
        )
        plt.text(
            df["task_name"][idx],
            value,
            str(value),
            ha="center",
            va="bottom",
            fontsize=FONTSIZE - 4,
        )

    plt.bar(df["task_name"], df["project_count"], color=XKCD_COLORS.values())
    plt.xlabel("PTM Task", fontsize=FONTSIZE)
    plt.ylabel("Application Count", fontsize=FONTSIZE)
    plt.xticks([])
    plt.yscale("log")
    # plt.legend(loc="upper left", ncol=len(df["task_name"])//5, fontsize=FONTSIZE, bbox_to_anchor=(1,1))
    plt.legend(loc="upper left", ncol=2, fontsize=FONTSIZE, bbox_to_anchor=(1, 1))
    plt.title("Frequency of Applications per PTM Task")
    plt.tight_layout()
    plt.savefig("frequencyOfApplicationsPerPTMTask.pdf")


if __name__ == "__main__":
    main()
