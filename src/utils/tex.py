import os
import re
import subprocess


def _replace_citet_and_citeauthor_with_citep(filename):
    """Replace all occurrences of \citet with \citep in your .tex file.

    Saha et al.~\citeyear{gpm}
    \citeyear we don't change because authors are given. Also it does
    not give us a [x].
    """
    with open(filename, "r") as file:
        data = file.read()

    # what about cite?
    data = re.sub(r"\\citet|\\cited|\\citeauthor", r"\\citep", data)

    with open(filename, "w") as file:
        file.write(data)


def find_main_tex_file(directory):
    """Find the main (only) .tex file in the directory.

    Returns the name if there is one, False otherwise.
    """
    main_tex_files = []

    for filename in os.listdir(directory):
        if filename.endswith(".tex"):
            with open(os.path.join(directory, filename), "r") as file:
                content = file.read()
                if (
                    "\\begin{document}" in content
                    and "\\end{document}" in content
                ):
                    main_tex_files.append(filename)
                    if len(main_tex_files) > 1:
                        return False

    return main_tex_files[0] if main_tex_files else False


def remove_extra_tex(filename):
    """Remove all references to other sections, equations,
    figures, their labels, and also all figures and equations.
    """
    env_patterns = [
        r"\\begin{figure\*?}",
        r"\\end{figure\*?}",
        r"\\begin{SCfigure\*?}",
        r"\\end{SCfigure\*?}",
        r"\\begin{equation\*?}",
        r"\\end{equation\*?}",
        r"\\begin{align\*?}",
        r"\\end{align\*?}",
        r"\\begin{table\*?}",
        r"\\end{table\*?}",
        r"\\begin{wraptable\*?}",
        r"\\end{wraptable\*?}",
        r"\\begin{wrapfigure\*?}",
        r"\\end{wrapfigure\*?}",
    ]

    ref_pattern = r"\\(ref\*?|ref|figref|secref|label|eqref|autoref|cref|appendixref)\{[^}]*\}"

    cleaned_lines = []

    with open(filename, "r") as f:
        lines = f.readlines()

    lines_iter = iter(lines)

    for line in lines_iter:
        line = re.sub(ref_pattern, "", line, flags=re.IGNORECASE)

        for i in range(0, len(env_patterns), 2):
            if re.search(
                env_patterns[i], line
            ) and not line.strip().startswith("%"):
                while not re.search(env_patterns[i + 1], line):
                    line = next(lines_iter)
                break
        else:
            cleaned_lines.append(line)

    with open(filename, "w") as f:
        f.writelines(cleaned_lines)


def clean_tex_file(filename, citestyle, main_file=True):
    """Clean the .tex file by removing everything except for
    the authors, abstract, introduction, and bibliography.
    Citestyle is the conference key.

    Returns True if an intro is found, False else.
    """
    _replace_citet_and_citeauthor_with_citep(filename)

    with open(filename, "r") as f:
        lines = f.readlines()

    pre_intro_flag = True  # keep everything before the introduction
    intro_flag = False
    biblio_flag = False
    cleaned_lines = []

    intro_exists_flag = False

    for line in lines:
        if (
            re.search(r"\\section\*?\{.*introduction.*\}", line, re.IGNORECASE)
            or re.search(r"\\input\{.*intro.*\}", line, re.IGNORECASE)
        ) and not line.strip().startswith("%"):
            intro_flag = True
            pre_intro_flag = (
                False  # once the intro starts, pre-intro content ends
            )
            intro_exists_flag = True

            # If input, already remove additional stuff from intro.tex
            if re.search(r"\\input\{.*intro.*\}", line, re.IGNORECASE):
                file = re.search(r"\\input\{([^}]*)\}", line).group(1)
                file += ".tex" if not file.endswith(".tex") else ""

                _replace_citet_and_citeauthor_with_citep(
                    f"{os.path.dirname(filename)}/{file}"
                )

                # Recursion!
                clean_tex_file(
                    f"{os.path.dirname(filename)}/{file}",
                    citestyle=citestyle,
                    main_file=False,
                )
                remove_extra_tex(f"{os.path.dirname(filename)}/{file}")

        if (
            ("\\section" in line or "\\section*" in line or "\\input{" in line)
            and not re.search(r".*intro.*", line, re.IGNORECASE)
            and not biblio_flag
        ):
            intro_flag = False

        if (
            "\\bibliography" in line
            or re.search(r"\\input\{[^}]*\.bbl\}", line)
        ) and not line.strip().startswith("%"):
            biblio_flag = True

        if (
            "\\appendix" in line
            or "\\include{appendix}" in line
            or "\\include{Appendix}" in line
            or re.search(r"\\input\{.*appendix.*\}", line, re.IGNORECASE)
        ) and not line.strip().startswith("%"):
            biblio_flag = False

        if pre_intro_flag or intro_flag or biblio_flag:
            cleaned_lines.append(line)
            biblio_flag = False

    if main_file and cleaned_lines[-1].strip() != "\\end{document}":
        cleaned_lines.append("\n\\end{document}")

    if citestyle in {"AAAI", "NeurIPS"}:
        for i, line in enumerate(cleaned_lines):
            if "\\documentclass{" in line or "\\documentclass[" in line:
                cleaned_lines.insert(
                    i + 1,
                    "\\PassOptionsToPackage{numbers,square,comma}{natbib}\n",
                )

    elif citestyle in {"ICLR", "ICML"}:
        for i, line in enumerate(cleaned_lines):
            if "\\begin{document}" in line:
                cleaned_lines.insert(
                    i,
                    "\setcitestyle{numbers,square,citesep={,},aysep={,},yysep={;}}\n",
                )
                break

    if not intro_exists_flag:
        return False

    with open(filename, "w") as f:
        f.writelines(cleaned_lines)

    return True


def compile_latex(tex_file, bib=False):
    """Make sure to be in the same directory as the tex_file."""
    if bib:
        subprocess.run(
            ["pdflatex", tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # Remove the '.tex' extension and add '.aux' extension
        aux_file = tex_file.rsplit(".", 1)[0] + ".aux"

        subprocess.run(
            ["bibtex", aux_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    for _ in range(2):
        subprocess.run(
            ["pdflatex", tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
