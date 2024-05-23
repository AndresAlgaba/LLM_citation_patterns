import os

from openai import OpenAI

from config import CONFERENCES, ENGINE, STRATEGY, SYSTEM_PROMPT, USER_PROMPT


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
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.txt"
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

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            for _ in range(5):
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
                    conference_dir, paper, f"{STRATEGY}_result_{ENGINE}.txt"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(result)


if __name__ == "__main__":
    main()
