import matplotlib.pyplot as plt
import pandas
from matplotlib.axes import Axes
from matplotlib.colors import XKCD_COLORS
from matplotlib.container import BarContainer
from matplotlib.patches import Rectangle
from pandas import DataFrame

FONTSIZE: int = 12


def main() -> None:
    df: DataFrame = pandas.read_json(
        path_or_buf="../../data/ghProjectsPerPTMTask.json"
    ).T.sort_values(by="project_count", ascending=False, ignore_index=True)

    pivot: DataFrame = df.pivot(
        index="domain", columns="task_name", values="project_count"
    )

    ax = pivot.plot(kind="bar", figsize=(30, 6))

    non_zero_data = {"domain": [], "task_name": [], "project_count": []}
    for container in ax.containers:
        for bar, (domain, task_name) in zip(container, pivot.index):
            if bar.get_height() != 0:
                non_zero_data["domain"].append(domain)
                non_zero_data["task_name"].append(task_name)
                non_zero_data["project_count"].append(bar.get_height())

    # Creating New DataFrame from Non-Zero Data
    new_df = DataFrame(non_zero_data)

    # Pivot New DataFrame
    new_pivot = new_df.pivot(
        index="domain", columns="task_name", values="project_count"
    )

    # Clear the original plot and replot with new data
    ax.clear()
    new_pivot.plot(kind="bar", ax=ax)

    # Rest of the plotting code
    plt.title("Grouped Bar Chart")
    plt.xlabel("Subcategory")
    plt.ylabel("Values")
    plt.xticks(rotation=0)
    plt.legend(title="Category")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()

    plt.savefig("frequencyOfApplicationsPerPTMTask_test.pdf")


if __name__ == "__main__":
    main()
