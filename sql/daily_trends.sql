-- A second view at date + hub grain, suitable for a BI date filter.
SELECT date(placed_at) AS order_date, hub, COUNT(*) AS total_orders,
 SUM(CASE WHEN status='delivered' THEN revenue_eur ELSE 0 END) AS delivered_sales_eur,
 SUM(CASE WHEN status='delivered' AND delivered_at <= promised_at THEN 1 ELSE 0 END) AS on_time_orders,
 SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) AS delivered_orders
FROM orders GROUP BY date(placed_at), hub ORDER BY order_date, hub;
