from json import load
from os import listdir
from pathlib import Path
from pprint import pprint
from typing import Any, List

import pandas
from pandas import DataFrame
from progress.bar import Bar

# IGNORE_FILE_PATTERNS: str = ".py|.sh|.html|.js|.pdf|Dockerfile|.tex|.pkl|.tar"
CONDIENCE_THRESHOLD: int = 98


def loadJSONFile(filepath: Path) -> DataFrame | None:
    with open(file=filepath, mode="r") as jsonFile:
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

    df["project"] = filepath.stem

    try:
        df: DataFrame = df[
            df["percentage_of_license_text"] >= CONDIENCE_THRESHOLD
        ].reset_index(drop=True)
    except KeyError:
        return None

    return df


def printFilenames(df: DataFrame) -> None:
    pathStrs: List[str] = df["path"].to_list()
    paths: List[Path] = [Path(p) for p in pathStrs]

    filenames: List[str] = [p.name for p in paths]

    pprint(filenames)


def main() -> None:
    dfs: List[DataFrame] = []
    files: List[Path] = [
        Path("../../data/ghLicenses", file)
        for file in listdir(path="../../data/ghLicenses")
    ]

    with Bar(message="Loading JSON data... ", max=len(files)) as bar:
        file: Path
        for file in files:
            dfs.append(loadJSONFile(filepath=file))
            bar.next()

    df: DataFrame = pandas.concat(objs=dfs, ignore_index=True)
    df.sort_values(by="project", axis=0, inplace=True, ignore_index=True)

    df.T.to_json(path_or_buf="ghProjectLicense.json", indent=4)


if __name__ == "__main__":
    main()
