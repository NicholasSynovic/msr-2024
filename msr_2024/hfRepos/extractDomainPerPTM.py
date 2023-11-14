from json import load
from typing import Any, List

import pandas
from pandas import DataFrame
from progress.bar import Bar


def loadJSONData(filepath: str) -> List[dict[str, Any]]:
    data: List[dict[str, Any]] = []

    with open(file=filepath, mode="r") as jsonFile:
        jsonData: dict[str, dict[str, Any]] = load(fp=jsonFile)
        jsonFile.close()

    modelKeys: List[str] = list(jsonData.keys())

    with Bar(message="Extracting data... ", max=len(modelKeys)) as bar:
        key: str
        for key in modelKeys:
            data.append(jsonData[key])
            bar.next()

    return data


def constructDF(data: dict[str, Any], modelID: int) -> DataFrame | None:
    foo: dict[str, List[str | int]] = {}

    try:
        foo["domain"] = data["domain"]
    except TypeError:
        return None

    foo["modelID"] = [modelID] * len(foo["domain"])

    return DataFrame(data=foo)


def main() -> None:
    dfList: List[DataFrame | None] = []

    models: List[dict[str, Any]] = loadJSONData(
        filepath="../../data/result_5000_10000.json"
    )

    with Bar(message="Creating DataFrames... ", max=len(models)) as bar:
        model: dict[str, Any]
        for model in models:
            modelID: int = models.index(model)
            dfList.append(constructDF(data=model, modelID=modelID))
            bar.next()

    df: DataFrame = pandas.concat(objs=dfList, ignore_index=True)

    df.drop_duplicates(ignore_index=True).T.to_json(
        path_or_buf="ptmDomains.json", indent=4
    )


if __name__ == "__main__":
    main()
