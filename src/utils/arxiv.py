import pandas as pd


def save_paper_info(paper, directory, results):
    """Save the paper info as a csv file.

    "{directory}/{paper.title}/info.csv" and
    "{directory}/{paper.title}/references.csv"
    """
    paper_info = {
        "title_arxiv": [paper.title],
        "title_sch": [results["title"]],
        "id_arxiv": [paper.get_short_id()],
        "id_sch": [results["paperId"]],
        "date_arxiv": [paper.published.strftime("%Y-%m-%d")],
        "date_sch": [results["publicationDate"]],
        "authors_arxiv": [
            ", ".join([author.name for author in paper.authors])
        ],
    }

    pd.DataFrame(paper_info).to_csv(
        f"{directory}/{paper.title}/info.csv", index=False
    )

    pd.DataFrame.from_dict(results["references"]).to_csv(
        f"{directory}/{paper.title}/references.csv",
        index=False,
    )
