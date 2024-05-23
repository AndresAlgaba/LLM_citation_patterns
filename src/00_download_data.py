import os
import shutil
import time

import arxiv
from thefuzz import fuzz

from config import CONFERENCES, MAX_DATE, MIN_DATE, REMOVE_PAPERS, SKIP_PAPERS
from utils.arxiv import save_paper_info
from utils.pdf import (
    clean_txt,
    extract_intro_references,
    split_text_and_references,
    transform_pdf_to_txt,
)
from utils.tex import (
    clean_tex_file,
    compile_latex,
    find_main_tex_file,
    remove_extra_tex,
)
from utils.utils import (
    check_for_file_extension,
    ensure_directory_exists,
    extract_tar_gz,
    semantic_scholar_request,
)


def download_arxiv_paper(paper, directory):
    """Download a single paper (tex files) from arXiv.

    We skip papers that are too old or too new, that are in the
    REMOVE_PAPERS and SKIP_PAPERS list, or that cannot be found
    on semantic scholar. We save metadata from arxiv and semantic
    scholar and extract the tar.gz file (and remove it).
    """
    if (
        paper.published < MIN_DATE
        or paper.published > MAX_DATE
        or paper.title in REMOVE_PAPERS
    ):
        print("removing paper")
        return False

    paper.download_source(
        dirpath=directory,
        filename=f"{paper.title}.tar.gz",
    )

    if any(word in paper.journal_ref.lower() for word in SKIP_PAPERS):
        os.remove(f"{directory}/{paper.title}.tar.gz")
        print("skipping paper")
        return False

    time.sleep(1.1)
    results = semantic_scholar_request(
        query=paper.title,
        fields="title,authors,publicationDate,venue,references",
    )
    results = results[0] if results else None

    if results is None:
        os.remove(f"{directory}/{paper.title}.tar.gz")
        print("not found on semantic scholar")
        return False

    if "references" not in results or not results["references"]:
        os.remove(f"{directory}/{paper.title}.tar.gz")
        print("no references found on semantic scholar")
        return False

    similarity = fuzz.partial_ratio(
        paper.title.lower(), results["title"].lower()
    )

    if similarity < 90:
        os.remove(f"{directory}/{paper.title}.tar.gz")
        print("title not similar on semantic scholar")
        return False

    extract_tar_gz(f"{directory}/{paper.title}")
    save_paper_info(paper, directory, results)

    os.remove(f"{directory}/{paper.title}.tar.gz")

    return True


def compile_tex_paper(paper, directory, base_dir, conference):
    """Compile the tex paper.

    We first clean the tex file, then compile it. If there is a bib file,
    we compile with bibtex. We rename the resulting pdf to the paper title.
    """
    tex_file = find_main_tex_file(f"{directory}/{paper.title}")
    bib_flag = check_for_file_extension(f"{directory}/{paper.title}", ".bib")

    if tex_file:
        intro_found = clean_tex_file(
            f"{directory}/{paper.title}/{tex_file}",
            citestyle=conference,
        )

        if intro_found:
            remove_extra_tex(f"{directory}/{paper.title}/{tex_file}")
        else:
            shutil.rmtree(f"{directory}/{paper.title}")
            print("no intro found")
            return False
    else:
        shutil.rmtree(f"{directory}/{paper.title}")
        print("no main tex file found")
        return False

    os.chdir(f"{directory}/{paper.title}")

    if bib_flag:
        compiled = compile_latex(f"{tex_file}", bib=True)
    else:
        if check_for_file_extension(".", ".bbl"):
            compiled = compile_latex(f"{tex_file}")
        else:
            os.chdir(base_dir)
            shutil.rmtree(f"{directory}/{paper.title}")
            print("no bbl or bib found")
            return False

    os.rename(f"{tex_file.replace('.tex', '.pdf')}", f"{paper.title}.pdf")
    os.chdir(base_dir)

    return True


def process_pdf_paper(paper, directory):
    """Process the pdf paper.

    We first transform the pdf to txt, then clean the txt. We then split
    the text into main content and references. We then extract the
    references from the main content. We then save the main content and
    the intro references in a txt file and a csv file, respectively.
    """
    pdf_text = transform_pdf_to_txt(
        f"{directory}/{paper.title}/{paper.title}.pdf"
    )

    cleaned_txt = clean_txt(pdf_text)
    main_content, references = split_text_and_references(cleaned_txt)

    filtered_reference_items = extract_intro_references(
        main_content, references
    )

    main_content_file_path = f"{directory}/{paper.title}/{paper.title}.txt"
    with open(main_content_file_path, "w") as file:
        file.write(main_content)

    filtered_references_csv_file_path = (
        f"{directory}/{paper.title}/intro_references.txt"
    )
    with open(filtered_references_csv_file_path, "w", newline="") as file:
        file.write("\n\n".join(filtered_reference_items))


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = base_dir + "/../data"

    ensure_directory_exists(data_dir)

    for conference, query in CONFERENCES.items():
        conference_dir = data_dir + "/" + conference
        ensure_directory_exists(conference_dir)

        search = arxiv.Search(
            query=query,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        for paper in search.results():
            print(paper.title)

            paper.title = paper.title.replace("/", " ")

            if os.path.exists(os.path.join(conference_dir, paper.title)):
                print("paper exists")
                continue

            downloaded = download_arxiv_paper(paper, conference_dir)

            if downloaded:
                compiled = compile_tex_paper(
                    paper, conference_dir, base_dir, conference
                )

            if downloaded and compiled:
                process_pdf_paper(paper, conference_dir)


if __name__ == "__main__":
    main()
