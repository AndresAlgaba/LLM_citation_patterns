import os
import shutil

import pandas as pd

from openai import OpenAI

from config import CONFERENCES, ENGINE, STRATEGY, SYSTEM_PROMPT, USER_PROMPT


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
                    f"{STRATEGY}_result_{ENGINE}_iterative.txt",
                )
            ):
                print("file exists")
                continue

            prompt = (
                USER_PROMPT
                + open(
                    os.path.join(conference_dir, paper, f"{paper}.txt"),
                    errors="ignore",
                ).read()
            )

            first_iteration = open(
                os.path.join(
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.txt"
                ),
                errors="ignore",
            ).read()

            info = pd.read_csv(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_enriched.csv",
                ),
                index_col=0,
            )
            not_exist = (
                info.loc[info["Exists"] == 0, "Citation Number"]
                .to_string(index=False)
                .replace("\n", ", ")
            )

            if info.loc[info["Exists"] == 0, "Citation Number"].empty:
                shutil.copy(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}.txt",
                    ),
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_iterative.txt",
                    ),
                )
                shutil.copy(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}.csv",
                    ),
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_iterative.csv",
                    ),
                )
                shutil.copy(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_enriched.csv",
                    ),
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_enriched_iterative.csv",
                    ),
                )

                continue

            iterative_prompt = (
                "The following references associated with these citation "
                f"numbers: {not_exist} do not exist. Can you replace all these "
                "non-existent references with existing ones? Keep the other "
                "references as they are. Do not return anything except "
                "the citation number between square brackets and the corresponding "
                "reference. "
                "=== "
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": first_iteration},
                {"role": "user", "content": iterative_prompt},
            ]

            for attempt in range(5):
                try:
                    response = client.chat.completions.create(
                        messages=messages, model=ENGINE
                    )
                    break
                except Exception as e:
                    print(e)

            if response.choices[0].finish_reason != "stop":
                print("WARNING: chat did not finish successfully")

            result = response.choices[0].message.content

            with open(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_iterative.txt",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(result)


if __name__ == "__main__":
    main()
