import sqlite3
import unittest
from pathlib import Path


class KpiTests(unittest.TestCase):
    def test_denominator_boundary_and_zero_delivery(self):
        with sqlite3.connect(':memory:') as conn:
            conn.row_factory = sqlite3.Row
            conn.execute('CREATE TABLE orders (hub TEXT, placed_at TEXT, promised_at TEXT, delivered_at TEXT, status TEXT, revenue_eur REAL)')
            conn.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', [
                ('Essen', '2026-01-01T12:00:00', '2026-01-01T12:30:00', '2026-01-01T12:30:00', 'delivered', 20),
                ('Essen', '2026-01-01T12:00:00', '2026-01-01T12:30:00', '2026-01-01T12:31:00', 'delivered', 30),
                ('Essen', '2026-01-01T12:00:00', '2026-01-01T12:30:00', '', 'cancelled', 99),
                ('Berlin', '2026-01-01T12:00:00', '2026-01-01T12:30:00', '', 'cancelled', 40),
            ])
            query = (Path(__file__).resolve().parents[1] / 'sql/operations_kpis.sql').read_text()
            result = {r['hub']: dict(r) for r in conn.execute(query)}
            self.assertEqual(result['Essen']['on_time_pct'], 50.0)
            self.assertEqual(result['Essen']['cancellation_pct'], 33.33)
            self.assertEqual(result['Essen']['delivered_sales_eur'], 50.0)
            self.assertIsNone(result['Berlin']['on_time_pct'])
            self.assertIsNone(result['Berlin']['avg_delivery_minutes'])
