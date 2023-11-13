from json import load
from typing import Any

import pandas
from pandas import DataFrame


def main() -> None:
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

    df2: DataFrame = df[df["path"].str.contains(".py|.sh") == False].reset_index(
        drop=True
    )

    print(df)


if __name__ == "__main__":
    main()
