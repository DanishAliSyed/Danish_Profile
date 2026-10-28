# NYC Taxi Operations Analysis

Exploratory analysis of 2023 NYC yellow taxi trips, including data cleaning, hourly sampling, demand patterns, fare analysis, and geographic visualisation.

**Tools:** pandas, NumPy, Matplotlib, Seaborn, GeoPandas, PyArrow.

[View the notebook](analysis.ipynb)

## Run locally or in Colab

1. Download this project folder, or clone the repository.
2. Start Jupyter in this project folder (so `data/` resolves here). For Colab, upload the notebook and the authorised input files with the same folder structure. No Google Drive mount or cloud credentials are needed.
3. Install the relevant packages listed above.
4. Supply these inputs: 2023 monthly trip parquet files under data/trip_records/ and taxi zone shapefiles under data/taxi_zones/. The source notebook expects month files named 2023-1.parquet through 2023-12.parquet.
5. Run cells in order and review assumptions before interpreting results.

Public dataset reference: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Scope and provenance

Migrated from a Colab coursework / learning notebook held by Danish Ali Syed. Original instructional text remains where relevant; no claim is made to ownership of third-party starter material or datasets. No additional licence is granted for third-party material.

This is an educational analysis, not a production service. Raw datasets, model binaries, notebook outputs, credentials, personal Drive links, and backend configuration are excluded. Static review was performed during migration; execution and model metrics were not reproduced because the original datasets are not bundled. Any remaining assignment prompts or historical conclusions belong to the source learning work.
