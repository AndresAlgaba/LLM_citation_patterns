import os
import pandas as pd
import numpy as np

STRATEGIES = [
    "vanilla_1",
    "vanilla_2",
    "vanilla_3",
    "vanilla_4",
    "vanilla_5"
]

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    results_dir = os.path.join(base_dir, "..", "results")

    merged_gen_results = pd.DataFrame()
    merged_intro_results = pd.DataFrame()
    merged_gen_iterative_results = pd.DataFrame()
    merged_intro_iterative_results = pd.DataFrame()

    for strategy in STRATEGIES:
        gen_results = pd.read_csv(
            os.path.join(results_dir, f"merged_gen_refs_{strategy}_gpt-4.csv")
        )
        intro_results = pd.read_csv(
            os.path.join(results_dir, f"merged_intro_refs_{strategy}_gpt-4.csv")
        )
        gen_iterative_results = pd.read_csv(
            os.path.join(results_dir, f"merged_gen_refs_{strategy}_gpt-4_iterative.csv")
        )
        intro_iterative_results = pd.read_csv(
            os.path.join(results_dir, f"merged_intro_refs_{strategy}_gpt-4_iterative.csv")
        )

        ### Add non-exist to NAs
        gen_results.loc[gen_results["Exists"].isna(), ["Exists"]] = 0.0
        gen_iterative_results.loc[gen_iterative_results["Exists"].isna(), ["Exists"]] = 0.0

        ### Pre-process Number of Authors
        # All strings which do not correspond to numbers get converted to "et al."
        etal_mask_gen = gen_results["Number of Authors"].apply(
            lambda x: str(x).replace('.', '').isdigit() if not pd.isna(x) else True
        )
        etal_mask_intro = intro_results["Number of Authors"].apply(
            lambda x: str(x).replace('.', '').isdigit() if not pd.isna(x) else True
        )
        etal_mask_gen_iterative = gen_iterative_results["Number of Authors"].apply(
            lambda x: str(x).replace('.', '').isdigit() if not pd.isna(x) else True
        )
        etal_mask_intro_iterative = intro_iterative_results["Number of Authors"].apply(
            lambda x: str(x).replace('.', '').isdigit() if not pd.isna(x) else True
        )    

        gen_results.loc[~etal_mask_gen, "Number of Authors"] = "et al."
        intro_results.loc[~etal_mask_intro, "Number of Authors"] = "et al."
        gen_iterative_results.loc[~etal_mask_gen_iterative, "Number of Authors"] = "et al."
        intro_iterative_results.loc[~etal_mask_intro_iterative, "Number of Authors"] = "et al."

        # All strings which correspond to numbers get converted to integers
        gen_results["Number of Authors"] = gen_results["Number of Authors"].apply(
            lambda x: float(x) if str(x).replace('.', '').isdigit() else x
        )
        intro_results["Number of Authors"] = intro_results["Number of Authors"].apply(
            lambda x: float(x) if str(x).replace('.', '').isdigit() else x
        )
        gen_iterative_results["Number of Authors"] = gen_iterative_results["Number of Authors"].apply(
            lambda x: float(x) if str(x).replace('.', '').isdigit() else x
        )
        intro_iterative_results["Number of Authors"] = intro_iterative_results["Number of Authors"].apply(
            lambda x: float(x) if str(x).replace('.', '').isdigit() else x
        )

        ### Pre-process Title length
        gen_results["Title Length"] = gen_results["Title"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        intro_results["Title Length"] = intro_results["Title"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        gen_iterative_results["Title Length"] = gen_iterative_results["Title"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        intro_iterative_results["Title Length"] = intro_iterative_results["Title"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )

        ### Pre-process Title length_sch
        gen_results["Title Length_sch"] = gen_results["Title_sch"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        intro_results["Title Length_sch"] = intro_results["Title_sch"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        gen_iterative_results["Title Length_sch"] = gen_iterative_results["Title_sch"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )
        intro_iterative_results["Title Length_sch"] = intro_iterative_results["Title_sch"].apply(
            lambda x: len(x) if not pd.isna(x) else np.nan
        )

        ### Pre-process Publication Year
        year_mask_gen = gen_results["Publication Year"].apply(
            lambda x: str(x).replace(".", "", 1).isdigit() if not pd.isna(x) else True
        )
        year_mask_intro = intro_results["Publication Year"].apply(
            lambda x: str(x).replace(".", "", 1).isdigit() if not pd.isna(x) else True
        )
        year_mask_gen_iterative = gen_iterative_results["Publication Year"].apply(
            lambda x: str(x).replace(".", "", 1).isdigit() if not pd.isna(x) else True
        )
        year_mask_intro_iterative = intro_iterative_results["Publication Year"].apply(
            lambda x: str(x).replace(".", "", 1).isdigit() if not pd.isna(x) else True
        )

        gen_results.loc[~year_mask_gen, "Publication Year"] = np.nan
        intro_results.loc[~year_mask_intro, "Publication Year"] = np.nan
        gen_iterative_results.loc[~year_mask_gen_iterative, "Publication Year"] = np.nan
        intro_iterative_results.loc[~year_mask_intro_iterative, "Publication Year"] = np.nan

        gen_results["Publication Year"] = gen_results["Publication Year"].astype(float)
        intro_results["Publication Year"] = intro_results["Publication Year"].astype(float)
        gen_iterative_results["Publication Year"] = gen_iterative_results["Publication Year"].astype(float)
        intro_iterative_results["Publication Year"] = intro_iterative_results["Publication Year"].astype(float)

        ### Pre-process Publication Venue
        na_venues = ["-", "Not specified", "Unknown"]

        arxiv_patters = [
            "arxiv",
            "corr",
        ]
        NeurIPS_patters = [
            "neural information processing systems",
            "nips",
            "neurips",
        ]
        ICLR_patters = [
            "conference on learning representations",
            "iclr",
        ]
        ICML_patterns = [
            "conference on machine learning",
            "icml",
        ]
        AAAI_patterns = [
            "aaai",
        ]
        CVPR_patterns = [
            "computer vision and pattern recognition",
            "cvpr",
        ]
        JMLR_patterns = [
            "journal of machine learning research",
            "jmlr",
        ]
        nature_patters = [
            "nature",
        ]

        gen_results.loc[gen_results['Publication Venue'].isin(na_venues), 'Publication Venue'] = np.nan
        intro_results.loc[intro_results['Publication Venue'].isin(na_venues), 'Publication Venue'] = np.nan
        gen_iterative_results.loc[gen_iterative_results['Publication Venue'].isin(na_venues), 'Publication Venue'] = np.nan
        intro_iterative_results.loc[intro_iterative_results['Publication Venue'].isin(na_venues), 'Publication Venue'] = np.nan

        gen_results["Publication Venue_processed"] = gen_results["Publication Venue"]
        intro_results["Publication Venue_processed"] = intro_results["Publication Venue"]
        gen_iterative_results["Publication Venue_processed"] = gen_iterative_results["Publication Venue"]
        intro_iterative_results["Publication Venue_processed"] = intro_iterative_results["Publication Venue"]

        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'arxiv'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'NeurIPS'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICLR'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICML'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'AAAI'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'CVPR'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'JMLR'
        gen_results.loc[
            gen_results['Publication Venue'].str.contains("|".join(nature_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'Nature'

        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'arxiv'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'NeurIPS'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICLR'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICML'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'AAAI'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'CVPR'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'JMLR'
        intro_results.loc[
            intro_results['Publication Venue'].str.contains("|".join(nature_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'Nature'

        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'arxiv'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'NeurIPS'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICLR'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICML'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'AAAI'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'CVPR'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'JMLR'
        gen_iterative_results.loc[
            gen_iterative_results['Publication Venue'].str.contains("|".join(nature_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'Nature'

        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'arxiv'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'NeurIPS'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICLR'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'ICML'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'AAAI'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'CVPR'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Publication Venue_processed'
        ] = 'JMLR'
        intro_iterative_results.loc[
            intro_iterative_results['Publication Venue'].str.contains("|".join(nature_patters), case=False, na=False),
            'Publication Venue_processed'
        ] = 'Nature'

        ### Post-process Venue_sch
        gen_results["Venue_sch_processed"] = gen_results["Venue_sch"]
        intro_results["Venue_sch_processed"] = intro_results["Venue_sch"]
        gen_iterative_results["Venue_sch_processed"] = gen_iterative_results["Venue_sch"]
        intro_iterative_results["Venue_sch_processed"] = intro_iterative_results["Venue_sch"]

        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'arxiv'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'NeurIPS'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICLR'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICML'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'AAAI'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'CVPR'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'JMLR'
        gen_results.loc[
            gen_results['Venue_sch'].str.contains("|".join(nature_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'Nature'

        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'arxiv'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'NeurIPS'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICLR'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICML'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'AAAI'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'CVPR'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'JMLR'
        intro_results.loc[
            intro_results['Venue_sch'].str.contains("|".join(nature_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'Nature'

        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(arxiv_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'arxiv'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(NeurIPS_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'NeurIPS'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(ICLR_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICLR'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(ICML_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'ICML'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(AAAI_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'AAAI'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(CVPR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'CVPR'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(JMLR_patterns), case=False, na=False),
            'Venue_sch_processed'
        ] = 'JMLR'
        gen_iterative_results.loc[
            gen_iterative_results['Venue_sch'].str.contains("|".join(nature_patters), case=False, na=False),
            'Venue_sch_processed'
        ] = 'Nature'

        ### Add strategy
        gen_results["strategy"] = strategy
        intro_results["strategy"] = strategy
        gen_iterative_results["strategy"] = strategy
        intro_iterative_results["strategy"] = strategy

        merged_gen_results = pd.concat(
            [merged_gen_results, gen_results],
            ignore_index=True,
        )
        merged_intro_results = pd.concat(
            [merged_intro_results, intro_results],
            ignore_index=True,
        )
        merged_gen_iterative_results = pd.concat(
            [merged_gen_iterative_results, gen_iterative_results],
            ignore_index=True,
        )
        merged_intro_iterative_results = pd.concat(
            [merged_intro_iterative_results, intro_iterative_results],
            ignore_index=True,
        )
    
    merged_gen_results.to_csv(
        os.path.join(results_dir, f"merged_gen_refs_vanilla_gpt-4.csv"),
        index=False,
    )
    merged_intro_results.to_csv(
        os.path.join(results_dir, f"merged_intro_refs_vanilla_gpt-4.csv"),
        index=False,
    )
    merged_gen_iterative_results.to_csv(
        os.path.join(results_dir, f"merged_gen_refs_vanilla_gpt-4_iterative.csv"),
        index=False,
    )
    merged_intro_iterative_results.to_csv(
        os.path.join(results_dir, f"merged_intro_refs_vanilla_gpt-4_iterative.csv"),
        index=False,
    )


if __name__ == "__main__":
    main()
