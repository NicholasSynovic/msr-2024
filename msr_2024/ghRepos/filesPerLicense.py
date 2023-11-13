from json import load
from pathlib import Path
from typing import Any

import pandas
from pandas import DataFrame
from progress.bar import Bar


def loadJSONFile(filepath: Path) -> DataFrame:
    with open(
        file="../../data/ghLicenses/facebookresearch_DisCo.json", mode="r"
    ) as jsonFile:
        json: dict[str, Any] = load(jsonFile)
        jsonFile.close()

    relevantJSON: dict[str, Any] = json["files"]
    df: DataFrame = DataFrame.from_records(data=relevantJSON)

    df.drop(
        columns=df.columns.difference(
            other=[
                "path",
                "detected_license_expression",
                "percentage_of_license_text",
            ]
        ),
        axis=1,
        inplace=True,
    )

    df: DataFrame = df[df["path"].str.contains(".py|.sh") == False,].reset_index(
        drop=True
    )

    return df


def main() -> None:
    pass


if __name__ == "__main__":
    main()
