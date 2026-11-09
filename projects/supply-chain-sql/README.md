# Order Fulfilment Analysis | SQL

A portfolio exercise based on supply chain SQL labs. It uses synthetic orders and line items to show how late shipments and sales can be reported together without double counting orders.

[Run the SQL](analysis.sql)

Order lines are rolled up to one row per order before calculating shipment metrics. Shipping modes are then ranked within each region by late shipment rate. The result includes order counts so that readers can tell when a high rate is based on a small sample.

The script is self-contained and works with MySQL 8 and SQLite 3.25 or newer.
