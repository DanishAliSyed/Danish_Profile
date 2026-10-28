# NYC Taxi Operations Analysis

Exploratory analysis of 2023 NYC yellow taxi trips, including data cleaning, hourly sampling, demand patterns, fare analysis, and geographic visualisation.

**Tools:** pandas, NumPy, Matplotlib, Seaborn, GeoPandas, PyArrow.

[View the notebook](analysis.ipynb)

## Run locally or in Colab

1. Download this project folder, or clone the repository.
2. Start Jupyter in this project folder (so `data/` resolves here). For Colab, upload the notebook and the authorised input files with the same folder structure. 
3. Install the relevant packages listed above.
4. Supply these inputs: 2023 monthly trip parquet files under data/trip_records/ and taxi zone shapefiles under data/taxi_zones/. The source notebook expects month files named 2023-1.parquet through 2023-12.parquet.
5. Run cells in order and review assumptions before interpreting results.

Public dataset reference: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Project notes

This educational project includes starter material and exercises. Datasets are not included; use an authorised copy of the data to run the notebook. Third-party material remains subject to its original terms. Results should be reproduced with the appropriate dataset.
