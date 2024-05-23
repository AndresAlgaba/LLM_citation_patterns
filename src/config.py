from datetime import datetime

import pytz

ENGINE = "gpt-4"
SYSTEM_PROMPT = "You are a helpful assistant."

STRATEGY = "vanilla_1"
USER_PROMPT = (
    "Below, we share with you a written introduction to a paper and have omitted the references. "
    "Numbers between square brackets indicate citations. "
    "Can you give us a suggestion for an explicit reference associated with each number? "
    "Do not return anything except the citation number between square brackets and the corresponding reference. "
    "==="
)

POSTPROCESS_ENGINE = "gpt-4"
POSTPROCESS_PROMPT = (
    "Below, we share with you a list of references with their corresponding citation number "
    "between square brackets. Could you for each reference extract the authors, the number of authors, "
    "title, publication year, and publication venue? Please only return the extracted information in a "
    "markdown table with the citation number (without brackets), authors, number of authors, title, "
    "publication year, and publication venue as columns. "
    "==="
)

TITLE_SCORE = 90
AUTHORS_SCORE = 50

CONFERENCES = {
    "AAAI": 'cat:cs.LG AND (jr:"AAAI Conference on Artificial Intelligence" OR jr:"AAAI 2022" OR jr:"AAAI 2023")',
    "NeurIPS": "cat:cs.LG AND jr:NeurIPS",
    "ICLR": "cat:cs.LG AND jr:ICLR",
    "ICML": "cat:cs.LG AND jr:ICML",
}
MIN_DATE = datetime(2022, 3, 1, tzinfo=pytz.UTC)
MAX_DATE = datetime(2023, 10, 31, tzinfo=pytz.UTC)
SKIP_PAPERS = [
    "workshop",
    "tiny paper",
    "2020",
    "2021",
    "track on datasets and benchmarks",
    "bridge",
]
REMOVE_PAPERS = [
    # AAAI
    "Neuro-symbolic Rule Learning in Real-world Classification Tasks",  # compilation error
    "Generalization Bounds for Inductive Matrix Completion in Low-noise Settings",  # bibtex error
    # NeurIPS
    "A General Framework for Robust G-Invariance in G-Equivariant Networks",  # bibtex error
    "CLIFT: Analysing Natural Distribution Shift on Question Answering Models in Clinical Domain",  # bibtex error
    "Partial Counterfactual Identification of Continuous Outcomes with a Curvature Sensitivity Model",  # compilation error
    "Attacks on Online Learners: a Teacher-Student Analysis",  # bibtex error
    "Learning Feynman Diagrams using Graph Neural Networks",  # bibtex error
    "Function Classes for Identifiable Nonlinear Independent Component Analysis",  # compilation error
    "Blackbox Attacks via Surrogate Ensemble Search",  # bibtex error
    "Censored Quantile Regression Neural Networks for Distribution-Free Survival Analysis",  # bibtex error
    "Semi-Discrete Normalizing Flows through Differentiable Tessellation",  # bibtex error
    "Online Decision Mediation",  # bibtex error
    "Exact Generalization Guarantees for (Regularized) Wasserstein Distributionally Robust Models",  # bibtex error
    "Deep Learning with Kernels through RKHM and the Perron-Frobenius Operator",  # bibtex error
    "Bridging RL Theory and Practice with the Effective Horizon",  # Input inside Figure
    "Reliable learning in challenging environments",  # wrong cite style
    # "Contrast Everything/ A Hierarchical Contrastive Framework for Medical Time-Series",  # appendix references
    # ICLR
    "Brain-like representational straightening of natural movies in robust feedforward neural networks", # bibtex error
    "Broken Neural Scaling Laws", # bibtex error
    "Parametrizing Product Shape Manifolds by Composite Networks", # bibtex error and no refs in intro
    "Tier Balancing: Towards Dynamic Fairness over Underlying Causal Factors", # bibunit problem
    "Guiding continuous operator learning through Physics-based boundary constraints", # printbiblio problem
    "Scaling Laws For Deep Learning Based Image Reconstruction", # problem with setcitestyle
    "Probabilistically Robust Recourse: Navigating the Trade-offs between Costs and Robustness in Algorithmic Recourse", # processing problem with intro
    "Domain Adaptation via Minimax Entropy for Real/Bogus Classification of Astronomical Alerts", # problem with naming
    # ICML
    "Why Target Networks Stabilise Temporal Difference Methods", # bibtex error
    "Nonlinear Advantage: Trained Networks Might Not Be As Complex as You Think", # bibtex error
    "HyperImpute: Generalized Iterative Imputation with Automatic Model Selection" # problem wit setcitestyle
]
