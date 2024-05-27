# Replication code for Large Language Models Reflect Human Citation Patterns with a Heightened Citation Bias
https://arxiv.org/abs/2405.15739

## Running the scripts and creating the figures
To run the scripts, first run:

```text
poetry install
```

then:

```text
poetry run python src/00_download_data.py
```

or open the virtual environment with:

```text
poetry shell
```

The figures and results can be replicated in the corresponding notebooks found in src/figures. 

The necessary data to run the notebooks can be found in the results folder.  

The raw data which is created in the Python scripts in the src folder is available via: https://zenodo.org/records/11299894. This data contains a new data folder and complementary files to the results folder.

## Data
We describe the steps of our automated pipeline to retrieve all the necessary information for our analysis. Our data collection resulted in $166$ papers published at AAAI ($25$), NeurIPS ($72$), ICML ($38$), and ICLR ($31$) for a total of 3,066 references (see Appendix Table \ref{tab:paper_details} for a full list of included papers). The data collection pipeline uses GPT-4 to postprocess parts of the data, which costs approximately 14 dollars for our experiment. Note that these steps only have to be carried out once for the data collection. However, steps 4 and 5 are also used to postprocess and enrich the information of the generated references and will need to be carried out for each run. The experiment was run on 4 November 2023 and each step was manually verified and tested.

### Step 1. ArXiv (src/00_download_data.py and src/utils/arxiv.py)
We search for all papers on arXiv originally posted between 1 March 2022 and 31 October 2023 in the machine learning (cs.LG) category which refer to AAAI, NeurIPS, ICLR, or ICML in their journal reference. Note that we also verify whether we can use all these arXiv papers given their data licenses and attribute their participation in Appendix Table \ref{tab:paper_details}. We use keywords (i.e., workshop, tiny paper, 2020, 2021, track on datasets and benchmarks, and bridge) to remove papers that do not appear in the conference proceedings or earlier than 2022. We download and unzip the *tar.gz* file provided by the authors to arXiv and check whether the paper exists on Semantic Scholar via title matching. We store the title, ID, and date from arXiv and Semantic Scholar. Additionally, we store all the reference titles with their corresponding ID from Semantic Scholar.

### Step 2. Tex (src/00_download_data.py and src/utils/tex.py)
We check whether there is a main *tex* file in the unzipped paper folder by looking for a single file that contains `\begin{document}` and `\end{document}`. If we find a main *tex* file we start the cleaning process, otherwise, we exclude the paper from our analysis. The cleaning process consists of three steps. First, we remove everything except for the author information, conference information, abstract, introduction, and references. Second, we remove figures, tables, references to sections and appendices, etc. Finally, we transform all citations to numbers between square brackets. After the cleaning, we look at whether there is a *bib* or *bbl* file available and compile the *tex* to *PDF*. If neither file is available or the paper has compilation errors, we exclude the paper from our analysis (Appendix Table \ref{tab:sup_1}). Note that a *bib* file allows for both *PDFLatex* and *bibtex* compilation, while only a *bbl* file does not allow for *bibtex* compilation. As a consequence, papers with only a *bbl* file may potentially contain papers in their reference list that are not cited in the introduction of the paper. We solve this issue in the next step.

### Step 3. PDF (src/00_download_data.py and src/utils/pdf.py)
We transform the *PDF* to *txt* and split the main content of the paper (author information, conference information, abstract, and introduction) from the references. We then look for all in-text citations by using a regex pattern to capture numbers in between square brackets and match them with the reference list. This approach ensures that we only keep references that are cited in the introduction. We store the main content of the paper and the references cited in the introduction in separate *txt* files.

### Step 4. Postprocessing Postprocessing (src/01_postprocess_data.py)
A large number of variations and inconsistencies in the reference lists make it difficult to structurally extract and analyze all the author information, title, publication venue, and year. We noticed that this behavior was even more pronounced in the LLM-generated references. Therefore, we examine the capabilities of GPT-4 to impose a structure on the reference list by postprocessing the data. We feed GPT-4 the reference list in *txt* accompanied by the default system message: "*You are a helpful assistant*" and the following postprocessing prompt:

\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    Below, we share with you a list of references with their corresponding citation number between square brackets. Could you for each reference extract the authors, the number of authors, title, publication year, and publication venue? Please only return the extracted information in a markdown table with the citation number (without brackets), authors, number of authors, title, publication year, and publication venue as columns. \\
    === \\
     **[GPT-4 generated reference list]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}

We then store the markdown table in a *csv*. GPT-4 successfully structures the information and makes it more consistent, for example, by removing syllable hyphens. Sometimes a small hiccup is introduced (e.g., adding a final row with "…"), but these are manually resolved in the verification process. Note that we also prompt for the number of authors. While we can easily compute the number of authors via the meta-data from Semantic Scholar, it allows us to verify the accuracy of GPT-4 on this task as we will use it later on to postprocess the generated references where a ground truth may be unavailable.

### Step 5. Semantic Scholar src/02_semantic_data.py)
We enrich the information from the introduction references by matching the extracted title from the *csv* file in the previous step with the reference titles that we extracted from Semantic Scholar in step 1. This approach provides an extra check that GPT-4 does not change the title information in Step 4. After matching, we can use the Semantic Scholar ID to retrieve the publication venue, year, authors, citation count, influential citation count, and reference count. Additionally, we store the IDs of the papers to which the introduction references themselves refer.

### Step 6. "Vanilla" prompting (src/03_call_LLM.py and src/04_postprocess_LLM.py)
We prompt GPT-4 with the main content, which includes the author information, conference information, abstract, and introduction, accompanied by the default system message: "*You are a helpful assistant*" and the following prompt:
\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    Below, we share with you a written introduction to a paper and have omitted the references. Numbers between square brackets indicate citations. Can you give us a suggestion for an explicit reference associated with each number? Do not return anything except the citation number between square brackets and the corresponding reference. \\
    === \\
     **[main content]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}
We then post-process GPT-4's response to extract the title, venue, publication year, author names, and number of authors for each generated reference using the same approach as described in step 4. We repeat this "vanilla" approach five times for all $166$ papers.

### Step 7. Existence check (src/05_semantic_LLM.py)
We determine whether the generated references exist via title and authors' names matching with Semantic Scholar entries. For titles, we measure the similarity between the Semantic Scholar match and the generated reference by comparing the best matching substring. For authors, we compare them by splitting into tokens (words), removing duplicates, and then calculating the similarity based on the best partial match of the sets of tokens. In case of "et al.," we only consider the first author. The similarity is computed by character-level comparison. We determined the thresholds for the title and authors scores by manually labeling $100$ matches as true or false and maximizing the $F_1$ score.

### Step 8. "Iterative" prompting (src/06_iterate_LLM.py, src/07_postprocess_LLM.py) and src/08_semantic_LLM.py)
We also build on our "vanilla" approach, by introducing an "iterative" approach where we prompt GPT-4 with the main content accompanied by the default system message: "*You are a helpful assistant*" and the following prompt:
\vspace{0.1cm}
\begin{tcolorbox}[mypromptbox]
\begin{center}
    **[vanilla prompt + GPT-4's response]** \\
    The following references associated with these citation numbers: \\ **[numbers of non-existent generated references]** \\ do not exist. Can you replace all these non-existent references with existing ones? Keep the other references as they are. Do not return anything except the citation number between square brackets and the corresponding reference. \\
    === \\
     **[main content]**
\end{center}
\end{tcolorbox}
\vspace{0.1cm}
We again postprocess GPT-4's response using the same approach as described in steps 4, 5, and 7. The previously existing generated and the newly generated references are then merged.
