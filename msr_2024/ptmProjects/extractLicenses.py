import sqlite3
from sqlite3 import Connection

import pandas
from pandas import DataFrame


def postProcess(df: DataFrame) -> DataFrame:
    df.drop(
        labels=[
            "license_id",
            "model_hub_id",
            "sha",
            "downloads",
            "likes",
            "has_snapshot",
            "ptm_issues_id",
            "ptm_pull_requests_id",
        ],
        axis=1,
        inplace=True,
    )
    return df.T


def mergeTables(
    models: DataFrame, licenses: DataFrame, modelLicensePairs: DataFrame
) -> DataFrame:
    licenses["name"].replace(to_replace="", value="None", inplace=True)
    licenses.rename(
        columns={"id": "license_id", "name": "license_name"},
        inplace=True,
    )

    models.rename(columns={"id": "model_id"}, inplace=True)

    foo: DataFrame = licenses.merge(
        right=modelLicensePairs,
        how="left",
        on="license_id",
    )
    bar: DataFrame = foo.merge(right=models, how="left", on="model_id")

    return bar


def loadTable(table: str, con: Connection) -> DataFrame:
    query: str = "SELECT * FROM {}"
    df: DataFrame = pandas.read_sql_query(sql=query.format(table), con=con)
    return df


def main() -> None:
    con: Connection = sqlite3.connect(database="../../data/PeaTMOSS.db")

    models: DataFrame = loadTable(table="model", con=con)
    licenses: DataFrame = loadTable(table="license", con=con)
    modelLicensePairs: DataFrame = loadTable(table="model_to_license", con=con)

    con.close()

    df: DataFrame = mergeTables(
        models=models,
        licenses=licenses,
        modelLicensePairs=modelLicensePairs,
    )

    postProcess(df=df).to_json(path_or_buf="ptmLicenses.json")


if __name__ == "__main__":
    main()
