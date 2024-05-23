import json
import os
import time

import pandas as pd
from thefuzz import process

from config import CONFERENCES
from utils.utils import ensure_directory_exists, semantic_scholar_request


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    results_dir = os.path.join(base_dir, "..", "results")

    ensure_directory_exists(results_dir)

    merged_intro_refs = pd.DataFrame()
    merged_refs_of_refs = {}

    for conference in CONFERENCES:
        conference_dir = os.path.join(data_dir, conference)

        for paper in [
            p for p in os.listdir(conference_dir) if not p.startswith(".")
        ]:
            print(paper)

            merged_refs_of_refs.update({paper: {}})

            if os.path.exists(
                os.path.join(
                    conference_dir, paper, "intro_references_enriched.csv"
                )
            ) and os.path.exists(
                os.path.join(conference_dir, paper, "intro_refs_of_refs.json")
            ):
                print("file exists")
                intro_refs = pd.read_csv(
                    os.path.join(
                        conference_dir, paper, "intro_references_enriched.csv"
                    )
                )

                with open(
                    os.path.join(
                        conference_dir, paper, "intro_refs_of_refs.json"
                    )
                ) as json_file:
                    refs_of_refs = json.load(json_file)

                merged_intro_refs = pd.concat([merged_intro_refs, intro_refs])
                merged_refs_of_refs[paper].update(refs_of_refs)

                continue

            intro_refs = pd.read_csv(
                os.path.join(conference_dir, paper, "intro_references.csv")
            )
            intro_refs.columns = [
                "Citation Number",
                "Authors",
                "Number of Authors",
                "Title",
                "Publication Year",
                "Publication Venue",
            ]

            all_refs = pd.read_csv(
                os.path.join(conference_dir, paper, "references.csv")
            )

            intro_refs.insert(0, "Conference", len(intro_refs) * [conference])
            intro_refs.insert(0, "Paper", len(intro_refs) * [paper])
            all_titles = [title.lower() for title in all_refs["title"].to_list()]

            all_refs["title"] = all_refs["title"].str.lower()

            intro_refs["Id"] = None
            intro_refs["Title_sch"] = None
            intro_refs["Venue_sch"] = None
            intro_refs["Publication Venue_sch"] = None
            intro_refs["Publication Year_sch"] = None
            intro_refs["Authors_sch"] = None
            intro_refs["Number Authors_sch"] = None
            intro_refs["Citation Count_sch"] = None
            intro_refs["Influential Citation Count_sch"] = None
            intro_refs["Reference Count_sch"] = None
            intro_refs["Open Access_sch"] = None
            intro_refs["Field of Study_sch"] = None
            intro_refs["Field of Study s2_sch"] = None

            for i, row in intro_refs.iterrows():
                title, score = process.extractOne(row["Title"].lower(), all_titles)

                intro_refs.at[i, "Score"] = score

                id = all_refs.loc[
                    all_refs["title"] == title, "paperId"
                ].values[0]

                # id may be none if not included in semantic scholar
                # will be removed later on (see below)
                if pd.isna(id) or score < 90:
                    print(f"Could not find {row['Title']}")
                    continue

                intro_refs.at[i, "Id"] = id

                time.sleep(1.5)
                results = semantic_scholar_request(
                    id=id,
                    fields="title,"
                    "venue,"
                    "publicationVenue,"
                    "year,"
                    "authors,"
                    "citationCount,"
                    "influentialCitationCount,"
                    "referenceCount,"
                    "isOpenAccess,"
                    "fieldsOfStudy,"
                    "s2FieldsOfStudy,"
                    "references",
                )

                intro_refs.at[i, "Title_sch"] = results["title"]
                intro_refs.at[i, "Venue_sch"] = results["venue"]

                publication_venue = results["publicationVenue"]
                intro_refs.at[i, "Publication Venue_sch"] = (
                    publication_venue["name"]
                    if (
                        isinstance(publication_venue, dict)
                        and "name" in publication_venue
                    )
                    else None
                )

                intro_refs.at[i, "Publication Year_sch"] = results["year"]
                intro_refs.at[i, "Authors_sch"] = ", ".join(
                    [author["name"] for author in results["authors"]]
                )
                intro_refs.at[i, "Number Authors_sch"] = len(
                    results["authors"]
                )
                intro_refs.at[i, "Citation Count_sch"] = results[
                    "citationCount"
                ]
                intro_refs.at[i, "Influential Citation Count_sch"] = results[
                    "influentialCitationCount"
                ]
                intro_refs.at[i, "Reference Count_sch"] = results[
                    "referenceCount"
                ]
                intro_refs.at[i, "Open Access_sch"] = results["isOpenAccess"]

                intro_refs.at[i, "Field of Study_sch"] = results[
                    "fieldsOfStudy"
                ]
                intro_refs.at[i, "Field of Study s2_sch"] = results[
                    "s2FieldsOfStudy"
                ]

                refs_of_refs = {
                    results["title"]: {
                        item["title"]: item["paperId"]
                        for item in results["references"]
                    }
                }

                merged_refs_of_refs[paper].update(refs_of_refs)

            merged_intro_refs = pd.concat([merged_intro_refs, intro_refs])

            intro_refs.to_csv(
                os.path.join(
                    conference_dir, paper, "intro_references_enriched.csv"
                ),
                index=False,
            )

            with open(
                os.path.join(conference_dir, paper, "intro_refs_of_refs.json"),
                "w",
            ) as json_file:
                json.dump(merged_refs_of_refs[paper], json_file)

    # remove intro_refs with no semantic scholar id
    merged_intro_refs.dropna(subset=['Id'])

    merged_intro_refs.to_csv(
        os.path.join(results_dir, "merged_intro_refs.csv"), index=False
    )

    with open(
        os.path.join(results_dir, "merged_intro_refs_of_refs.json"), "w"
    ) as json_file:
        json.dump(merged_refs_of_refs, json_file)


if __name__ == "__main__":
    main()
