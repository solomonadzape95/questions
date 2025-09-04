# app/prompts.py

PROMPT_TEMPLATES = {
    "applied_math": """
    Generate {n} multiple choice questions for Applied Mathematics.
    Focus on these topics: 
    - Calculus (derivatives, integrals, optimization, accumulation)
    - Linear Algebra (vectors, matrices, systems of equations, eigenvalues)
    - Financial Mathematics (interest, present/future value, risk assessment)
    - Number Theory (primes, divisibility, modular arithmetic)
    - Probability & Combinatorics (counting, permutations, probability rules)
    """,

    "statistics": """
    Generate {n} multiple choice questions for Statistics & Data Analysis.
    Focus on these topics:
    - Hypothesis Testing (t-tests, chi-square, confidence intervals)
    - Regression Analysis (linear regression, correlation, forecasting)
    - Data Visualization (charts, graphs, scatter plots, histograms)
    - Sampling Methods (random, stratified, cluster, biases)
    - Central Tendency & Spread (mean, median, variance, standard deviation)
    """,

    "verbal_reasoning": """
    Generate {n} multiple choice questions for Verbal Reasoning.
    Focus on these topics:
    - Critical Reading (author’s tone, inference, arguments)
    - Analogies (relationships between words or ideas)
    - Logic Puzzles (deductive reasoning problems, elimination grids)
    - Sentence Completion (context, vocabulary usage)
    - Reading Comprehension (short passages with inference questions)
    """,

    "general_knowledge": """
    Generate {n} multiple choice questions for General Knowledge.
    Focus on these topics:
    - World Politics & Government (systems, leaders, global relations)
    - Economics (supply/demand, inflation, markets)
    - Science & Technology (major theories, discoveries, inventions)
    - Art & Literature (artists, authors, works from different cultures)
    - Geography (countries, capitals, physical landmarks)
    """,

    "specialized": """
    Generate {n} multiple choice questions for Specialized Fields.
    Focus on these topics:
    - Medicine: ECG interpretation (R-R interval conversion, arrhythmia basics)
    - Biology: Genetics (Mendelian, molecular, population genetics)
    - Computer Science: algorithms, data structures, internet basics, AI
    """
}
