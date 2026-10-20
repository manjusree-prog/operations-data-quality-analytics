"""Deterministic, fictional delivery data. No employer or customer records."""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate(path):
    rng = random.Random(42)
    rows = []
    for i in range(1, 1201):
        hub = rng.choice(['Essen', 'Berlin', 'Hamburg'])
        placed = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(31*24*60))
        promise = placed + timedelta(minutes=30)
        status = 'cancelled' if rng.random() < .05 else 'delivered'
        delay = rng.randint(-12, 10) + (8 if hub == 'Berlin' else 0)
        delivered = promise + timedelta(minutes=delay)
        rows.append(dict(order_id=f'O{i:05}',hub=hub,placed_at=placed.isoformat(),
                         promised_at=promise.isoformat(),
                         delivered_at=delivered.isoformat() if status == 'delivered' else '',
                         status=status,revenue_eur=f'{rng.uniform(8,65):.2f}'))
    rows[4]['hub'] = ''
    rows[14]['revenue_eur'] = '-12.00'
    rows[24]['placed_at'] = 'bad-date'
    rows[34]['status'] = 'unknown'
    rows[44]['delivered_at'] = ''
    rows.append(rows[100].copy())
    path = Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    return rows
