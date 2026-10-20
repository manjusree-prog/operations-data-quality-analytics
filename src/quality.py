"""Row-level quality rules; retain every failed rule for auditability."""
from collections import Counter
from datetime import datetime

def audit(rows):
    counts = Counter(r['order_id'] for r in rows)
    issues = []
    for index, row in enumerate(rows, 2):
        rules = []
        if not row['order_id'].strip(): rules.append('missing_order_id')
        elif counts[row['order_id']] > 1: rules.append('duplicate_order_id')
        if row['hub'] not in {'Essen', 'Berlin', 'Hamburg'}: rules.append('invalid_hub')
        if row['status'] not in {'delivered', 'cancelled'}: rules.append('invalid_status')
        try:
            amount = float(row['revenue_eur'])
            import math
            if not math.isfinite(amount) or amount < 0: raise ValueError
        except (ValueError, TypeError): rules.append('invalid_revenue')
        try:
            placed = datetime.fromisoformat(row['placed_at'])
            promised = datetime.fromisoformat(row['promised_at'])
            if promised < placed: rules.append('promise_before_order')
            delivered = datetime.fromisoformat(row['delivered_at']) if row['delivered_at'] else None
            if row['status'] == 'delivered' and delivered is None: rules.append('missing_delivery_time')
            if row['status'] == 'cancelled' and delivered is not None: rules.append('cancelled_with_delivery')
            if delivered is not None and delivered < placed: rules.append('delivery_before_order')
        except (ValueError, TypeError): rules.append('invalid_timestamp')
        for rule in rules:
            issues.append({'source_row': index, 'order_id': row['order_id'], 'rule': rule})
    return issues
