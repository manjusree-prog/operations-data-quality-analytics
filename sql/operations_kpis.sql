-- SQLite dialect. Grain: one accepted order. Rejected rows never enter this table.
-- On-time denominator: delivered orders only. Cancelled orders have no delivery SLA.
-- Net sales: delivered order value only; refunds/taxes/costs are not modeled.
WITH hub_summary AS (
 SELECT hub,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN status='delivered' AND delivered_at <= promised_at THEN 1 ELSE 0 END) AS on_time_orders,
        SUM(CASE WHEN status='delivered' THEN revenue_eur ELSE 0 END) AS delivered_sales_eur,
        AVG(CASE WHEN status='delivered' THEN (julianday(delivered_at)-julianday(placed_at))*1440 END) AS avg_delivery_minutes
 FROM orders GROUP BY hub
)
SELECT hub, total_orders, delivered_orders, cancelled_orders,
 ROUND(100.0*on_time_orders / NULLIF(delivered_orders,0),2) AS on_time_pct,
 ROUND(100.0*cancelled_orders / NULLIF(total_orders,0),2) AS cancellation_pct,
 ROUND(delivered_sales_eur,2) AS delivered_sales_eur,
 ROUND(avg_delivery_minutes,2) AS avg_delivery_minutes,
 DENSE_RANK() OVER (ORDER BY 1.0*on_time_orders/NULLIF(delivered_orders,0) DESC) AS on_time_rank
FROM hub_summary ORDER BY on_time_rank, hub;
