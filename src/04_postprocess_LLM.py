import os

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

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_API_ORG"),
    )

    for conference in CONFERENCES:
        conference_dir = os.path.join(data_dir, conference)

        for paper in [
            p for p in os.listdir(conference_dir) if not p.startswith(".")
        ]:
            print(paper)

            if os.path.exists(
                os.path.join(
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.csv"
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
                        f"{STRATEGY}_result_{ENGINE}.txt",
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

            with open(
                os.path.join(
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.csv"
                ),
                "w",
                encoding="utf-8",
            ) as file:
                file.write(csv_string_quoted)


if __name__ == "__main__":
    main()
