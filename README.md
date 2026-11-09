# Danish Ali Syed | Data & Analytics Portfolio

**Senior Advanced Analytics Engineer · Finance & Supply Chain Analytics**

I build data products, dashboards, and reproducible analyses that help teams understand performance and decide what to investigate next. My work spans SQL, Python, PySpark, Snowflake, Power BI, and Tableau.

**[Visit the portfolio website ↗](https://danishalisyed.github.io/Danish_Profile/)** · [Explore all projects](projects/README.md) · [LinkedIn](https://www.linkedin.com/in/consultant-danishsyed/)

## Featured work

| Project | What to look at |
| --- | --- |
| [Loan Portfolio Analysis](projects/loan-portfolio-power-bi/README.md) | Original Power BI dashboard export and a separate synthetic walkthrough of the lending funnel. |
| [Retail Profitability](projects/retail-profitability-tableau/README.md) | Tableau dashboard previews and workbook. See where higher sales did not translate into higher profit. |
| [Order Fulfilment Analysis](projects/supply-chain-sql/README.md) | SQL that measures late shipments and sales without double counting orders, using synthetic data. |
| [Bitcoin Network Activity](projects/bitcoin-network-activity/README.md) | PySpark and public block data showing how fees and confirmed transaction counts moved differently. |

## Project catalog

| Project | Focus |
|---|---|
| [Bitcoin Network Activity \| PySpark](projects/bitcoin-network-activity/README.md) | Confirmations, fees and block-space pricing across 718 public Bitcoin blocks |
| [Media Viewership Forecasting](projects/media-viewership-forecasting/README.md) | Chronological one-day forecast evaluation against daily and weekly baselines, using synthetic data. |
| [Telecom Churn \| Retention Prioritization](projects/telecom-churn/README.md) | Logistic regression and a contact-capacity decision using public telecom data. |
| [Retail Order Analytics \| Spark SQL](projects/retail-orders-spark/README.md) | Profitability and repeat-customer queries at the correct reporting grain, using synthetic orders. |
| [Credit Card Default \| Risk Model Evaluation](projects/credit-default/README.md) | Holdout evaluation of ranking and probability calibration on public UCI data. |
| [Customer Retention \| A/B Test Analysis](projects/customer-retention-ab-test/README.md) | Synthetic renewal reminder experiment with SQL, a confidence interval in Python, and a rollout decision. |
| [Retail Profitability \| Tableau](projects/retail-profitability-tableau/README.md) | Original Tableau dashboard previews, workbook, and a sales-versus-profit analysis using Sample Superstore. |
| [New Zealand Goods Export Recovery](projects/nz-export-recovery/README.md) | Matched-period export comparison, commodity contributions, and Power BI setup using public Stats NZ data. |
| [Bank Campaign Analytics](projects/bank-campaign-analytics/README.md) | SQL dashboard comparing term-deposit subscription rates by campaign history and contact count on public UCI data. |
| [Loan Portfolio Analysis \| Power BI](projects/loan-portfolio-power-bi/README.md) | Loan funnel, monthly trends, and product and channel breakdowns, with the original Power BI PDF export. |
| [Namma Yatri Ride Operations \| Power BI](projects/namma-yatri-power-bi/README.md) | Ride demand, revenue, conversion, and cancellation analysis, with a three-page dashboard export. |
| [Crop Insurance Coverage & Premiums \| MySQL](projects/crop-insurance-mysql/README.md) | Weighted coverage rates and premium contributions, demonstrated with synthetic data. |
| [Order Fulfilment Analysis \| SQL](projects/supply-chain-sql/README.md) | Order-grain sales and late shipment metrics, demonstrated with synthetic orders. |
| [NYC Taxi Operations Analysis](projects/nyc-taxi-analysis/README.md) | Exploratory analysis of 2023 NYC yellow taxi trips, including data cleaning, hourly sampling, demand patterns, fare analysis, and geographic visualisation. |
| [Employee Retention Modelling](projects/employee-retention/README.md) | Logistic regression exploring employee retention, with data cleaning, feature engineering, scaling, feature selection, and validation metrics. |
| [Delivery Time Estimation](projects/delivery-time-estimation/README.md) | Regression analysis examining delivery duration through timestamp processing, feature engineering, exploratory analysis, model building, and residual diagnostics. |
| [Customer Behaviour Analysis with Spark](projects/customer-behaviour-spark/README.md) | An Apache Spark implementation covering transaction preparation, joins, cleaning, exploratory analysis, customer segmentation, and RFM analysis.  |
| [Retail Customer Segmentation](projects/retail-customer-clustering/README.md) | A lab demonstrating RFM feature preparation, scaling, K-means, silhouette analysis, and hierarchical clustering on online retail transactions. |
| [Multiple Linear Regression](projects/multiple-linear-regression/README.md) | A notebook covering multiple linear regression, feature preparation, model diagnostics, and interpretation. |
| [Simple Linear Regression](projects/simple-linear-regression/README.md) | A notebook exploring the relationship between advertising spend and sales, with regression examples and additional practice exercises. |
| [Spark SQL Exploration](projects/spark-sql/README.md) | A compact notebook demonstrating Spark sessions, CSV loading, temporary SQL views, filtering, sorting, and row-to-dictionary conversion. |

The catalog includes standalone demonstrations and coursework. Each project explains its data source and limitations.

## Website source

The portfolio site lives in [`docs/`](docs/). It reads the project catalog above from [`projects/README.md`](projects/README.md), with a [local fallback](docs/project-index.md) for when GitHub’s raw file endpoint is unavailable. Add new projects to the index and refresh the fallback with `cp projects/README.md docs/project-index.md`. GitHub Pages publishes the site from the `/docs` folder on `master`. Optional topic labels, tools, and previews are defined in [`docs/catalog.js`](docs/catalog.js).
