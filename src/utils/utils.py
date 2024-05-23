import os
import time
import re
import tarfile

import requests


def ensure_directory_exists(directory):
    """Ensure that the given directory exists.

    ``parents=True`` allows for the creation of a directory
    and any of its missing parent directories in a single step.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def check_for_file_extension(directory, extension):
    """Check if there is a certain file extension in the directory.

    Returns True if there is, False otherwise.
    """
    for file in os.listdir(directory):
        if file.endswith(extension):
            return True
    return False


def extract_tar_gz(filename):
    """Extract the tar.gz file."""
    tar = tarfile.open(f"{filename}.tar.gz", "r:gz")
    tar.extractall(filename)
    tar.close()


def to_csv_field(content):
    """Convert content to a CSV field."""
    if "," in content:
        return f'"{content}"'
    return content


def semantic_scholar_request(
    id=None,
    query=None,
    fields="",
    limit=1,
    offset=0,
    timeout=100,
    attempts=5,
):
    """Interact with Semantic Scholar's API to either search
    for a paper by title or get a paper by ID.

    We use an API key if it is available in the environment as
    SEMANTIC_SCHOLAR_KEY.
    """
    api_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
    headers = {"x-api-key": api_key} if api_key else None

    for attempt in range(attempts):
        try:
            if query:
                query = query.replace("-", " ")
                rsp = requests.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={
                        "query": query,
                        "limit": limit,
                        "offset": offset,
                        "fields": fields,
                    },
                    headers=headers,
                    timeout=timeout,
                )

                rsp.raise_for_status()

                results = rsp.json()
                return results["data"] if results.get("total", 0) else None

            elif id:
                rsp = requests.get(
                    f"https://api.semanticscholar.org/graph/v1/paper/{id}",
                    params={"fields": fields},
                    headers=headers,
                    timeout=timeout,
                )

                rsp.raise_for_status()

                return rsp.json()

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1.6)

    return None


def extract_single_numbers(text):
    numbers = re.findall(r'\[\s*(\d+)\s*\]', text)
    return numbers
