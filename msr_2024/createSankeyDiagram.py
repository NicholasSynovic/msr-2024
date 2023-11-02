import click
import pandas
from pandas import DataFrame


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
    print(df)


if __name__ == "__main__":
    main()
