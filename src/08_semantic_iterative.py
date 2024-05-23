import json
import os
import time

import numpy as np
import pandas as pd
from thefuzz import fuzz

from config import AUTHORS_SCORE, CONFERENCES, ENGINE, STRATEGY, TITLE_SCORE
from utils.utils import ensure_directory_exists, semantic_scholar_request


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    results_dir = os.path.join(base_dir, "..", "results")

    summary_stats = pd.read_csv(os.path.join(results_dir, f"summary_statistics_{STRATEGY}_{ENGINE}.csv"))

    merged_gen_refs = pd.DataFrame()
    merged_refs_of_refs = {}

    summary_statistics = pd.DataFrame(
        columns=[
            "Conference",
            "Paper",
            "Intro",
            "Gen",
            "Miss Intro",
            "Miss Gen",
        ]
    )

    for conference in CONFERENCES:
        conference_dir = os.path.join(data_dir, conference)

        for paper in [
            p for p in os.listdir(conference_dir) if not p.startswith(".")
        ]:
            print(paper)

            if summary_stats.loc[summary_stats["Paper"] == paper, "Miss Intro"].values[0] > 3:
                print("skipping")
                continue

            gen_refs = pd.read_csv(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_iterative.csv",
                )
            )
            gen_refs.columns = [
                "Citation Number",
                "Authors",
                "Number of Authors",
                "Title",
                "Publication Year",
                "Publication Venue",
            ]

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

            intro_cit_num = intro_refs["Citation Number"].astype(str)
            gen_cit_num = gen_refs["Citation Number"].astype(str)

            missing_intro = intro_cit_num[~intro_cit_num.isin(gen_cit_num)]
            missing_gen = gen_cit_num[~gen_cit_num.isin(intro_cit_num)]

            new_row = pd.DataFrame(
                [
                    {
                        "Conference": conference,
                        "Paper": paper,
                        "Intro": len(intro_refs),
                        "Gen": len(gen_refs),
                        "Miss Intro": len(missing_intro),
                        "Miss Gen": len(missing_gen),
                    }
                ]
            )

            summary_statistics = pd.concat(
                [summary_statistics, new_row],
                ignore_index=True,
            )

            if len(missing_intro) > 3:
                print("Missing too many intro references")
                continue

            gen_refs = gen_refs[~gen_refs["Citation Number"].isin(missing_gen)]

            merged_refs_of_refs.update({paper: {}})

            if os.path.exists(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_enriched_iterative.csv",
                )
            ) and os.path.exists(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_refs_of_refs_{ENGINE}_iterative.json",
                )
            ):
                print("file exists")
                gen_refs = pd.read_csv(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_result_{ENGINE}_enriched_iterative.csv",
                    )
                )

                with open(
                    os.path.join(
                        conference_dir,
                        paper,
                        f"{STRATEGY}_refs_of_refs_{ENGINE}_iterative.json",
                    )
                ) as json_file:
                    refs_of_refs = json.load(json_file)

                merged_gen_refs = pd.concat([merged_gen_refs, gen_refs])
                merged_refs_of_refs[paper].update(refs_of_refs)

                continue         

            gen_refs.insert(0, "Conference", len(gen_refs) * [conference])
            gen_refs.insert(0, "Paper", len(gen_refs) * [paper])

            gen_refs["Id"] = None
            gen_refs["Title_sch"] = None
            gen_refs["Venue_sch"] = None
            gen_refs["Publication Venue_sch"] = None
            gen_refs["Publication Year_sch"] = None
            gen_refs["Authors_sch"] = None
            gen_refs["Number Authors_sch"] = None
            gen_refs["Citation Count_sch"] = None
            gen_refs["Influential Citation Count_sch"] = None
            gen_refs["Reference Count_sch"] = None
            gen_refs["Open Access_sch"] = None
            gen_refs["Field of Study_sch"] = None
            gen_refs["Field of Study s2_sch"] = None

            for i, row in gen_refs.iterrows():
                if not isinstance(row["Title"], str) or not isinstance(
                    row["Authors"], str
                ):
                    gen_refs.at[i, "Exists"] = 0.0
                    gen_refs.at[i, "In Paper"] = 0.0
                    gen_refs.at[i, "In Intro"] = 0.0
                    gen_refs.at[i, "Not Found"] = 0.0
                    print("next")
                    continue

                if len(row["Title"]) == 0 or len(row["Authors"]) == 0:
                    gen_refs.at[i, "Exists"] = 0.0
                    gen_refs.at[i, "In Paper"] = 0.0
                    gen_refs.at[i, "In Intro"] = 0.0
                    gen_refs.at[i, "Not Found"] = 0.0
                    print("next")
                    continue

                results = semantic_scholar_request(
                    query=row["Title"], fields="title,authors", limit=3
                )

                scores_title = []
                scores_authors = []

                if results:
                    for result in results:
                        scores_title.append(
                            fuzz.partial_ratio(
                                result["title"].lower(), row["Title"].lower()
                            )
                        )

                        if len(result["authors"]) == 0:
                            scores_authors.append(0)

                        elif "et al." in row["Authors"] or "..." in row["Authors"]:
                            scores_authors.append(
                                fuzz.token_set_ratio(
                                    result["authors"][0]["name"].lower(),
                                    row["Authors"].lower(),
                                )
                            )

                        else:
                            joined_authors = ", ".join(
                                [
                                    author["name"]
                                    for author in result["authors"]
                                ]
                            )
                            scores_authors.append(
                                fuzz.token_set_ratio(
                                    joined_authors.lower(),
                                    row["Authors"].lower(),
                                )
                            )

                    scores = [
                        0.5 * a + 0.5 * b
                        for a, b in zip(scores_title, scores_authors)
                    ]

                    max_score_index = scores.index(max(scores))

                    exists = (scores_title[max_score_index] >= TITLE_SCORE) * (
                        scores_authors[max_score_index] >= AUTHORS_SCORE
                    )

                    gen_refs.at[i, "Score title"] = max(scores)

                    gen_refs.at[i, "Score title"] = scores_title[
                        max_score_index
                    ]
                    gen_refs.at[i, "Score author"] = scores_authors[
                        max_score_index
                    ]
                    gen_refs.at[i, "Exists"] = exists

                    if exists:
                        id = results[max_score_index]["paperId"]
                        gen_refs.at[i, "Id"] = id

                        time.sleep(1.5)
                        info = semantic_scholar_request(
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

                        gen_refs.at[i, "Title_sch"] = info["title"]
                        gen_refs.at[i, "Venue_sch"] = info["venue"]

                        publication_venue = info["publicationVenue"]
                        gen_refs.at[i, "Publication Venue_sch"] = (
                            publication_venue["name"]
                            if (
                                isinstance(publication_venue, dict)
                                and "name" in publication_venue
                            )
                            else None
                        )

                        gen_refs.at[i, "Publication Year_sch"] = info["year"]
                        gen_refs.at[i, "Authors_sch"] = ", ".join(
                            [author["name"] for author in info["authors"]]
                        )
                        gen_refs.at[i, "Number Authors_sch"] = len(
                            info["authors"]
                        )
                        gen_refs.at[i, "Citation Count_sch"] = info[
                            "citationCount"
                        ]
                        gen_refs.at[
                            i, "Influential Citation Count_sch"
                        ] = info["influentialCitationCount"]
                        gen_refs.at[i, "Reference Count_sch"] = info[
                            "referenceCount"
                        ]
                        gen_refs.at[i, "Open Access_sch"] = info[
                            "isOpenAccess"
                        ]

                        gen_refs.at[i, "Field of Study_sch"] = info[
                            "fieldsOfStudy"
                        ]
                        gen_refs.at[i, "Field of Study s2_sch"] = info[
                            "s2FieldsOfStudy"
                        ]

                        references = pd.read_csv(
                            os.path.join(
                                conference_dir, paper, "references.csv"
                            )
                        )
                        enriched_intro = pd.read_csv(
                            os.path.join(
                                conference_dir, paper, "intro_references_enriched.csv"
                            )
                        )
                        if id in references["paperId"].values:
                            gen_refs.at[i, "In Paper"] = 1.0
                        else:
                            gen_refs.at[i, "In Paper"] = 0.0

                        if id in enriched_intro["Id"].values:
                            gen_refs.at[i, "In Intro"] = 1.0
                        else:
                            gen_refs.at[i, "In Intro"] = 0.0
                        
                        gen_refs.at[i, "Not Found"] = 0.0

                        refs_of_refs = {
                            info["title"]: {
                                item["title"]: item["paperId"]
                                for item in info["references"]
                            }
                        }

                        merged_refs_of_refs[paper].update(refs_of_refs)

                else:
                    gen_refs.at[i, "Exists"] = 0.0
                    gen_refs.at[i, "In Paper"] = 0.0
                    gen_refs.at[i, "In Intro"] = 0.0
                    gen_refs.at[i, "Not Found"] = 1.0

            # add missing references from intro
            gen_refs = pd.concat(
                [
                    gen_refs,
                    pd.DataFrame(
                        {
                            "Paper": len(missing_intro) * [paper],
                            "Conference": len(missing_intro) * [conference],
                            "Citation Number": missing_intro,
                        }
                    ),
                ],
                ignore_index=True,
            )

            merged_gen_refs = pd.concat([merged_gen_refs, gen_refs])

            gen_refs.to_csv(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_result_{ENGINE}_enriched_iterative.csv",
                )
            )

            with open(
                os.path.join(
                    conference_dir,
                    paper,
                    f"{STRATEGY}_refs_of_refs_{ENGINE}_iterative.json",
                ),
                "w",
            ) as json_file:
                json.dump(merged_refs_of_refs[paper], json_file)

    merged_intro_refs = pd.read_csv(os.path.join(results_dir, "merged_intro_refs.csv"))
    merged_intro_refs = merged_intro_refs[merged_intro_refs["Paper"].isin(merged_gen_refs["Paper"])]

    merged_intro_refs["identifier"] = merged_intro_refs["Paper"] + merged_intro_refs["Citation Number"].astype(str)
    merged_gen_refs["identifier"] = merged_gen_refs["Paper"] + merged_gen_refs["Citation Number"].astype(str)

    merged_gen_refs = merged_gen_refs[merged_gen_refs["identifier"].isin(merged_intro_refs["identifier"])]

    merged_intro_refs = merged_intro_refs[~merged_intro_refs["identifier"].duplicated()]
    merged_gen_refs = merged_gen_refs[~merged_gen_refs["identifier"].duplicated()]

    merged_gen_refs.to_csv(
        os.path.join(results_dir, f"merged_gen_refs_{STRATEGY}_{ENGINE}_iterative.csv"),
        index=False,
    )

    summary_statistics.to_csv(
        os.path.join(
            results_dir, f"summary_statistics_{STRATEGY}_{ENGINE}_iterative.csv"
        ), index=False
    )

    with open(
        os.path.join(
            results_dir, f"merged_gen_refs_of_refs_{STRATEGY}_{ENGINE}_iterative.json"
        ),
        "w",
    ) as json_file:
        json.dump(merged_refs_of_refs, json_file)

    merged_intro_refs.to_csv(
        os.path.join(results_dir, f"merged_intro_refs_{STRATEGY}_{ENGINE}_iterative.csv"),
        index=False,
    )

    with open(os.path.join(results_dir, "merged_intro_refs_of_refs.json")) as json_file:
        merged_intro_refs_of_refs = json.load(json_file)

    merged_intro_refs_of_refs = {
        key: merged_intro_refs_of_refs[key] 
        for key in merged_intro_refs_of_refs 
        if key in merged_refs_of_refs
    }

    with open(os.path.join(results_dir, f"merged_intro_refs_of_refs_{STRATEGY}_{ENGINE}_iterative.json"), "w") as json_file:
        json.dump(merged_intro_refs_of_refs, json_file)


if __name__ == "__main__":
    main()
