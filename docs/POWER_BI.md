# Optional Power BI build guide
This is a build specification, not a completed Power BI dashboard.

Import `outputs/clean_orders.csv` as `Orders`. Set revenue to decimal, timestamps to date/time, and IDs/status/hub to text. Blank delivered_at values belong to cancelled orders and should become null. Each accepted row represents one unique order.

Create these measures (table name `Orders`):
```dax
Total Orders = COUNTROWS(Orders)
Delivered Orders = CALCULATE([Total Orders], Orders[status] = "delivered")
Cancelled Orders = CALCULATE([Total Orders], Orders[status] = "cancelled")
On Time Orders = COUNTROWS(FILTER(Orders, Orders[status] = "delivered" && NOT ISBLANK(Orders[delivered_at]) && Orders[delivered_at] <= Orders[promised_at]))
On Time Rate = DIVIDE([On Time Orders], [Delivered Orders])
Cancellation Rate = DIVIDE([Cancelled Orders], [Total Orders])
Delivered Sales EUR = CALCULATE(SUM(Orders[revenue_eur]), Orders[status] = "delivered")
```
Format rates as percentages and sales as EUR. Add cards for orders, sales, on-time rate and cancellation rate. Add a hub bar chart and a date trend. Create an order-date column from placed_at for a calendar relationship; mark the calendar as the date table. Do not average precomputed daily percentages: divide the summed on-time counts by summed delivered counts.

Reconcile hub rates and sales against `outputs/operations_kpis.csv` before adding filters. Keep the synthetic-data label visible. Save your own `.pbix` and add screenshots only after building and checking it.
