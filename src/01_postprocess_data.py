import os

import openai

from config import CONFERENCES, POSTPROCESS_ENGINE, POSTPROCESS_PROMPT
from utils.utils import to_csv_field

openai.organization = os.getenv("OPENAI_API_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = "You are a helpful assistant."


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "..", "data")

    for conference in CONFERENCES:
        conference_dir = os.path.join(data_dir, conference)

        for paper in [
            p for p in os.listdir(conference_dir) if not p.startswith(".")
        ]:
            print(paper)

            if os.path.exists(
                os.path.join(conference_dir, paper, "intro_references.csv")
            ):
                print("file exists")
                continue

            prompt = (
                POSTPROCESS_PROMPT
                + open(
                    os.path.join(
                        conference_dir, paper, "intro_references.txt"
                    ),
                    errors="ignore",
                ).read()
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            response = openai.ChatCompletion.create(
                model=POSTPROCESS_ENGINE, messages=messages
            )

            if response.choices[0].finish_reason != "stop":
                print("WARNING: chat did not finish successfully")

            result = response.choices[0].message["content"]

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

            if len(csv_string_quoted) == 0:
                print("WARNING: empty csv string")

            with open(
                os.path.join(conference_dir, paper, "intro_references.csv"),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(csv_string_quoted)


if __name__ == "__main__":
    main()
