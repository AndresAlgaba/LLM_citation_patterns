import os
from io import StringIO

import pandas as pd

from openai import OpenAI

from config import (
    CONFERENCES,
    ENGINE,
    POSTPROCESS_ENGINE,
    POSTPROCESS_PROMPT,
    STRATEGY,
)
from utils.utils import to_csv_field

SYSTEM_PROMPT = "You are a helpful assistant."


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    results_dir = os.path.join(base_dir, "..", "results")

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_API_ORG"),
    )

    summary_stats = pd.read_csv(os.path.join(results_dir, f"summary_statistics_{STRATEGY}_{ENGINE}.csv"))

    for conference in CONFERENCES:
        conference_dir = os.path.join(data_dir, conference)

        for paper in [
            p for p in os.listdir(conference_dir) if not p.startswith(".")
        ]:
            print(paper)

            if summary_stats.loc[summary_stats["Paper"] == paper, "Miss Intro"].values[0] > 3:
                print("skipping")
                continue

            if os.path.exists(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_iterative.csv",
                )
            ):
                print("file exists")
                continue

            prompt = (
                POSTPROCESS_PROMPT
                + open(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_iterative.txt",
                    ),
                    errors="ignore",
                ).read()
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            for _ in range(5):
                try:
                    response = client.chat.completions.create(
                        messages=messages, model=POSTPROCESS_ENGINE
                    )
                    break
                except Exception as e:
                    print(e)

            if response.choices[0].finish_reason != "stop":
                print("WARNING: chat did not finish successfully")

            result = response.choices[0].message.content

            lines = result.strip().split("\n")
            csv_lines_quoted = []
            for line in lines:
                if "---" not in line:
                    csv_lines_quoted.append(
                        ",".join(
                            to_csv_field(cell.strip())
                            for cell in line.split("|")[1:-1]
                        )
                    )

            csv_string_quoted = "\n".join(csv_lines_quoted)

            refs = pd.read_csv(
                os.path.join(
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.csv"
                )
            )
            refs_enriched = pd.read_csv(
                os.path.join(
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}_enriched.csv"
                )
            )

            if len(csv_string_quoted) == 0 or refs_enriched.empty:
                print("There were no new references.")
                refs.to_csv(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_iterative.csv",
                    ),
                    index=False,
                )
                continue

            not_exist = refs_enriched.loc[refs_enriched["Exists"] == 0.0, "Citation Number"]

            df = pd.read_csv(StringIO(csv_string_quoted))

            refs.rename(columns={refs.columns[0]: "Citation Number"}, inplace=True)
            df.rename(columns={df.columns[0]: "Citation Number"}, inplace=True)

            df = df[df["Citation Number"].isin(not_exist)]

            df.set_index("Citation Number", inplace=True)
            refs.set_index("Citation Number", inplace=True)

            refs.update(df)
            refs.reset_index(inplace=True)

            refs.to_csv(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_iterative.csv",
                ),
                index=False,
            )


if __name__ == "__main__":
    main()
