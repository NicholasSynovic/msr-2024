from typing import List

import pandas
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

GOOD_COLUMNS: List[str] = ["task_name", "reuse_repository_id"]


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
    dfs.count().rename(
        columns={"reuse_repository_id": "project_count"}
    ).reset_index().T.to_json(
        path_or_buf="ghProjectsPerPTMTask.json",
        indent=4,
    )


if __name__ == "__main__":
    main()
