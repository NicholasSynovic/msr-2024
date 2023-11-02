from typing import Any, List

import click
import pandas
from pandas import DataFrame
from plotly import graph_objects as go


def createFigure(data: dict[str, List[Any]]) -> None:
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=data["label"],
                ),
                link=data,
            )
        ]
    )

    fig.update_layout(title_text="HF License to GH License Mapping", font_size=10)
    fig.show()


def preprocessData(df: DataFrame) -> dict[str, List[Any]]:
    df.dropna(inplace=True, ignore_index=True)
    hfLicenses: List[str] = df["HF License"].to_list()
    ghLicenses: List[str] = df["GH License"].to_list()

    uniqueHFLicenses: List[str] = list(set(hfLicenses))
    uniqueGHLicenses: List[str] = list(set(ghLicenses))

    hfLicenseIndices: List[int] = [
        uniqueHFLicenses.index(hfLicense) for hfLicense in hfLicenses
    ]
    ghLicenseIndices: List[int] = [
        uniqueGHLicenses.index(ghLicense) for ghLicense in ghLicenses
    ]
    ghLicenseIndices = [
        i + len(uniqueHFLicenses) for i in ghLicenseIndices
    ]  # TODO: What does this do?

    labels: List[str] = uniqueHFLicenses + uniqueGHLicenses
    source: List[int] = hfLicenseIndices
    target: List[int] = ghLicenseIndices
    value: List[int] = [1] * len(source)

    data: dict[str, List[Any]] = {
        "label": labels,
        "source": source,
        "target": target,
        "value": value,
    }

    return data


@click.command()
@click.option(
    "-d",
    "--data-filepath",
    required=True,
    type=str,
    help="Path to JSON data file to plot",
)
def main(data_filepath: str) -> None:
    df: DataFrame = pandas.read_json(path_or_buf=data_filepath).T

    data: dict[str, List[Any]] = preprocessData(df=df)

    createFigure(data=data)


if __name__ == "__main__":
    main()
