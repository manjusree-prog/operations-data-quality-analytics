import unittest
from src.quality import audit

def row(**changes):
    r=dict(order_id='A1',hub='Essen',placed_at='2026-01-01T12:00:00',promised_at='2026-01-01T12:30:00',delivered_at='2026-01-01T12:25:00',status='delivered',revenue_eur='20.50')
    r.update(changes);return r
class QualityTests(unittest.TestCase):
    def rules(self, rows): return [i['rule'] for i in audit(rows)]
    def test_valid(self): self.assertEqual(audit([row()]),[])
    def test_duplicate_quarantines_both(self):
        result=audit([row(),row()]);self.assertEqual({x['source_row'] for x in result},{2,3})
    def test_negative_and_nonfinite(self):
        for value in ['-1','NaN','inf','bad']:
            self.assertIn('invalid_revenue',self.rules([row(revenue_eur=value)]))
    def test_missing_delivery(self): self.assertIn('missing_delivery_time',self.rules([row(delivered_at='')]))
    def test_cancelled_valid(self): self.assertEqual(audit([row(status='cancelled',delivered_at='')]),[])
    def test_bad_date(self): self.assertIn('invalid_timestamp',self.rules([row(placed_at='bad')]))
    def test_inverted_time(self): self.assertIn('delivery_before_order',self.rules([row(delivered_at='2026-01-01T11:59:00')]))
    def test_multiple_rules_retained(self): self.assertEqual(len(audit([row(hub='',revenue_eur='-1')])),2)
if __name__=='__main__': unittest.main()
