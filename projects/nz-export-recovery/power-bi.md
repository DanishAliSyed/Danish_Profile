# Build the report in Power BI

Import `export_comparison.csv` as a table named `Export Comparison`. Set the four NZD columns to Whole number.

Use three cards for the national values. Each card should use the row where `series = Total`:

```dax
National Exports 2019 =
CALCULATE(SUM('Export Comparison'[nzd_2019]), 'Export Comparison'[series] = "Total")

National Exports 2020 =
CALCULATE(SUM('Export Comparison'[nzd_2020]), 'Export Comparison'[series] = "Total")

National Exports 2021 =
CALCULATE(SUM('Export Comparison'[nzd_2021]), 'Export Comparison'[series] = "Total")

Change vs 2019 =
DIVIDE([National Exports 2021] - [National Exports 2019], [National Exports 2019])
```

For a diverging commodity bar chart, use `label` and `delta_nzd_2021_vs_2019`, with a visual filter allowing only **Commodity** and **Commodity residual**. Use a separate partner chart filtered to **Partner**, and leave grand totals off because some partner groups overlap.
