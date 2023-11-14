import sqlite3
from sqlite3 import Connection
from typing import List

import pandas
from pandas import DataFrame

TASK_NAMES: List[str] = list(
    set(
        [
            "text-generation",
            "text-to-text-generation",
            "image-classification",
            "text-classification",
            "fill-mask",
            "feature-extraction",
            "token-classification",
            "conversational",
            "text-to-image",
            "translation",
            "summarization",
            "automatic-speech-recognition",
            "sentence-similarity",
            "question-answering",
            "image-segmentation",
            "image-to-text",
            "zero-shot-classification",
            "image-to-image",
            "audio-classification",
            "text-to-speech",
            "audio-to-audio",
            "object-detection",
            "visual-question-answering",
            "table-question-answering",
            "zero-shot-image-classification",
            "unconditional-image-generation",
            "document-question-answering",
            "video-classification",
            "reinforcement-learning",
            "image-super-resolution",
            "text-to-video",
            "voice-activity-detection",
            "image-text-matching",
            "audio-captioning",
            "text-to-audio",
            "image-text-retrieval",
            "speaker-diarization",
            "dense-passage-retrieval",
            "graph-machine-learning",
            "information-extraction",
            "sentence-embeddings",
            "time-series-forecasting",
            "depth-estimation",
            "audio-generation",
            "none",
            "feature-extraction",
            "text-to-image",
            "image-to-text",
            "text-to-video",
            "visual-question-answering",
            "document-question-answering",
            "graph neural networks" "depth-estimation",
            "image-classification",
            "object-detection",
            "image-segmentation",
            "image-to-image",
            "unconditional-image-generation",
            "video-classification",
            "zero-shot-image-classification",
            "text-classification",
            "token-classification",
            "table-question-answering",
            "question-answering",
            "zero-shot-classification",
            "translation",
            "summarization",
            "conversational",
            "text-generation",
            "text2text-generation",
            "fill-mask",
            "sentence-similarity",
            "text-to-speech",
            "text-to-audio",
            "automatic-speech-recognition",
            "audio-to-audio",
            "audio-classification",
            "voice-activity-detection",
            "tabular-classification",
            "tabular-regression",
            "reinforcement-learning",
            "robotics",
        ]
    )
)


def loadTable(table: str, con: Connection) -> DataFrame:
    query: str = "SELECT * FROM {}"
    df: DataFrame = pandas.read_sql_query(sql=query.format(table), con=con)
    return df


def mergeTables(tags: DataFrame, modelTags: DataFrame, models: DataFrame) -> DataFrame:
    tags.rename(columns={"id": "tag_id"}, inplace=True)
    models.rename(columns={"id": "model_id"}, inplace=True)

    foo: DataFrame = modelTags.merge(right=tags, how="left", on="tag_id")
    foo.drop(labels="tag_id", axis=1, inplace=True)

    bar: DataFrame = foo.merge(right=models, how="left", on="model_id")

    bar.rename(columns={"name": "task_name"}, inplace=True)

    return bar


def postProcess(df: DataFrame) -> DataFrame:
    badColumns: List[str] = [
        "model_hub_id",
        "sha",
        "downloads",
        "likes",
        "has_snapshot",
        "ptm_issues_id",
        "ptm_pull_requests_id",
    ]

    df.drop(labels=badColumns, axis=1, inplace=True)

    foo: DataFrame = df[df["task_name"].isin(TASK_NAMES)].reset_index(drop=True)

    return foo


def main() -> None:
    con: Connection = sqlite3.connect(database="../../data/PeaTMOSS.db")

    tags: DataFrame = loadTable(table="tag", con=con)
    modelTags: DataFrame = loadTable(table="model_to_tag", con=con)
    models: DataFrame = loadTable(table="model", con=con)

    con.close()

    df: DataFrame = mergeTables(tags=tags, modelTags=modelTags, models=models)

    postProcess(df=df).T.to_json(path_or_buf="projectTasks.json", indent=4)


if __name__ == "__main__":
    main()
