from typing import Hashable, List

import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

GOOD_COLUMNS: List[str] = ["domain", "task_name", "reuse_repository_id"]


def main() -> None:
    projectPairings: DataFrame = pandas.read_json(
        path_or_buf="../../data/ptmProjectPairs.json"
    ).T
    ptmTasks: DataFrame = pandas.read_json(
        path_or_buf="../../data/ptmProjectTasks.json"
    ).T

    df: DataFrame = ptmTasks.merge(
        right=projectPairings,
        how="left",
        on="model_id",
    )
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df.drop(
        labels=df.columns.difference(other=GOOD_COLUMNS),
        axis=1,
        inplace=True,
    )

    dfs: DataFrameGroupBy = df.groupby(by="task_name")

    dfList: List[DataFrame] = []
    foo: tuple[Hashable, DataFrame]
    for foo in dfs:
        bar: DataFrame = foo[1]
        bar.rename(columns={"reuse_repository_id": "project_count"}, inplace=True)
        projectCount: int = bar["project_count"].count()

        data: dict[str, List[str | int]] = {
            "domain": [bar["domain"].to_list()[0]],
            "project_count": [projectCount],
            "task_name": bar["task_name"].to_list()[0],
        }
        dfList.append(DataFrame(data=data))

    pandas.concat(objs=dfList, ignore_index=True).T.to_json(
        path_or_buf="ghProjectsPerPTMTask.json",
        indent=4,
    )


if __name__ == "__main__":
    main()
