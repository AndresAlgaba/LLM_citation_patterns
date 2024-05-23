import os
import pandas as pd

from config import CONFERENCES
from utils.utils import extract_single_numbers


base_dir = os.path.abspath(".")
results_dir = os.path.join(base_dir, "..", "results")
data_dir = os.path.join(base_dir, "..", "data")

gen_results = pd.read_csv(
    os.path.join(results_dir, f"merged_gen_refs_vanilla_gpt-4.csv")
)
intro_results = pd.read_csv(
    os.path.join(results_dir, f"merged_intro_refs_vanilla_gpt-4.csv")
)
gen_iterative_results = pd.read_csv(
    os.path.join(results_dir, f"merged_gen_refs_vanilla_gpt-4_iterative.csv")
)
intro_iterative_results = pd.read_csv(
    os.path.join(results_dir, f"merged_intro_refs_vanilla_gpt-4_iterative.csv")
)

gen_results["Unique"] = 0
intro_results["Unique"] = 0
gen_iterative_results["Unique"] = 0
intro_iterative_results["Unique"] = 0

for conference in CONFERENCES:
    conference_dir = os.path.join(data_dir, conference)

    for paper in [
        p for p in os.listdir(conference_dir) if not p.startswith(".")
    ]:
        with open(
            os.path.join(
                conference_dir, paper, f"{paper}.txt"
            ),
            'r',
            errors="ignore"
        ) as file:
            text = file.read()

        numbers = extract_single_numbers(text)

        gen_results.loc[
            (gen_results["Conference"] == conference)
            & (gen_results["Paper"] == paper)
            & (gen_results["Citation Number"].isin(numbers)),
            "Unique",
        ] = 1.0

        intro_results.loc[
            (intro_results["Conference"] == conference)
            & (intro_results["Paper"] == paper)
            & (intro_results["Citation Number"].isin(numbers)),
            "Unique",
        ] = 1.0

        gen_iterative_results.loc[
            (gen_iterative_results["Conference"] == conference)
            & (gen_iterative_results["Paper"] == paper)
            & (gen_iterative_results["Citation Number"].isin(numbers)),
            "Unique",
        ] = 1.0

        intro_iterative_results.loc[
            (intro_iterative_results["Conference"] == conference)
            & (intro_iterative_results["Paper"] == paper)
            & (intro_iterative_results["Citation Number"].isin(numbers)),
            "Unique",
        ] = 1.0

# fix order
intro_results["order"] = intro_results["identifier"] + intro_results["strategy"]
gen_results["order"] = gen_results["identifier"] + gen_results["strategy"]
intro_iterative_results["order"] = intro_iterative_results["identifier"] + intro_iterative_results["strategy"]
gen_iterative_results["order"] = gen_iterative_results["identifier"] + gen_iterative_results["strategy"]

order = intro_results["order"].to_list()
gen_results.sort_values(by="order", key=lambda column: column.map(lambda e: order.index(e)), inplace=True)
gen_results.reset_index(drop=True, inplace=True)

order_iterative = intro_iterative_results["order"].to_list()
gen_iterative_results.sort_values(by="order", key=lambda column: column.map(lambda e: order_iterative.index(e)), inplace=True)
gen_iterative_results.reset_index(drop=True, inplace=True)

gen_results.to_csv(
    os.path.join(results_dir, f"merged_gen_refs_vanilla_gpt-4_unique.csv"),
    index=False,
)

intro_results.to_csv(
    os.path.join(results_dir, f"merged_intro_refs_vanilla_gpt-4_unique.csv"),
    index=False,
)

gen_iterative_results.to_csv(
    os.path.join(
        results_dir, f"merged_gen_refs_vanilla_gpt-4_iterative_unique.csv"
    ),
    index=False,
)

intro_iterative_results.to_csv(
    os.path.join(
        results_dir, f"merged_intro_refs_vanilla_gpt-4_iterative_unique.csv"
    ),
    index=False,
)
