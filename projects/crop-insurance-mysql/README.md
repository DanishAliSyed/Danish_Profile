# Crop Insurance Coverage & Premiums | MySQL

This small example revisits a group coursework analysis of crop insurance participation and premium contributions. The original project was completed with Praneeth Kumar and Supriya Venkatesh. This portfolio version uses fictional districts and synthetic figures.

[Run the SQL](analysis.sql) · [View the synthetic input](district_sample.csv)

The query sums covered farmers and eligible farmers before calculating the coverage rate. Averaging district rates would give a small district the same weight as a large one. The second measure shows how much of the premium was paid by state and central government combined.

In the synthetic sample, North has more covered farmers (700 vs. 600), while South has the higher coverage rate (60% vs. 46.67%). This is an example of why a count and a rate answer different questions.

The script is self-contained and works with MySQL 8 and SQLite 3.25 or newer.
