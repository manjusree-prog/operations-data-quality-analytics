"""Run from any working directory with Python 3.10+. Standard library only."""
import csv
import html
import json
import sqlite3
from collections import Counter
from pathlib import Path
from src.generate_data import generate
from src.quality import audit
ROOT=Path(__file__).resolve().parent

def export(path, rows, fields):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def main():
    output=ROOT/'outputs';output.mkdir(exist_ok=True)
    rows=generate(ROOT/'data'/'sample_orders.csv')
    issues=audit(rows)
    bad={i['source_row'] for i in issues}
    clean=[r for index,r in enumerate(rows,2) if index not in bad]
    export(output/'quality_issues.csv',issues,['source_row','order_id','rule'])
    export(output/'clean_orders.csv',clean,list(rows[0]))
    with sqlite3.connect(':memory:') as conn:
        conn.row_factory=sqlite3.Row
        conn.execute('CREATE TABLE orders (order_id TEXT PRIMARY KEY, hub TEXT, placed_at TEXT, promised_at TEXT, delivered_at TEXT, status TEXT, revenue_eur REAL)')
        conn.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?,?)',[tuple(r.values()) for r in clean])
        for name in ['operations_kpis','daily_trends']:
            result=[dict(r) for r in conn.execute((ROOT/'sql'/f'{name}.sql').read_text())]
            export(output/f'{name}.csv',result,list(result[0]))
            if name=='operations_kpis': kpis=result
    metrics={'input_rows':len(rows),'accepted_rows':len(clean),'rejected_rows':len(bad),
             'rejected_row_pct':round(100*len(bad)/len(rows),2),
             'issue_count':len(issues),'issues_by_rule':dict(Counter(i['rule'] for i in issues))}
    (output/'quality_summary.json').write_text(json.dumps(metrics,indent=2))
    bars=''.join(f"<div class='barrow'><b>{html.escape(r['hub'])}</b><div class='track'><div class='bar' style='width:{r['on_time_pct']}%'></div></div><strong>{r['on_time_pct']}%</strong></div>" for r in kpis)
    headers=['Hub','Orders','Delivered','Cancelled','On time %','Cancelled %','Sales EUR','Avg min','Rank']
    table='<tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr>'
    for r in kpis: table+='<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in r.values())+'</tr>'
    rules=''.join(f'<li>{html.escape(k)}: {v}</li>' for k,v in metrics['issues_by_rule'].items())
    document="""<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Teja | Operations & Data Quality</title>
<style>body{font:16px system-ui;background:#f2f5fa;color:#172c43;margin:0}main{max-width:1080px;margin:auto;padding:40px 24px}h1{font-size:38px;letter-spacing:-1px;margin:12px 0}.eyebrow{color:#087e88;font-weight:700;letter-spacing:2px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:28px 0}section,.card{background:white;padding:24px;border-radius:14px;box-shadow:0 3px 16px #15243808;margin-bottom:20px}.number{display:block;font-size:32px;font-weight:750}.muted{color:#53647a}.barrow{display:flex;align-items:center;gap:15px;margin:22px 0}.barrow b{width:90px}.track{background:#e4ebf4;flex:1;border-radius:6px;overflow:hidden}.bar{height:25px;background:#087e88}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:12px 8px;text-align:left;border-bottom:1px solid #e3e9f1}.scroll{overflow-x:auto}footer{font-size:14px;color:#53647a}@media(max-width:650px){.cards{grid-template-columns:1fr}h1{font-size:29px}}</style><main><div class='eyebrow'>TEJA MANJUSREE KODURU / ANALYTICS PORTFOLIO</div><h1>Delivery performance starts with trusted data.</h1><p class='muted'>Python validation → audited order data → SQL KPIs. Fictional sample, January 2026.</p>"""
    document+=f"<div class='cards'><div class='card'>Source rows<span class='number'>{len(rows):,}</span></div><div class='card'>Accepted rows<span class='number'>{len(clean):,}</span></div><div class='card'>Rejected rows<span class='number'>{len(bad)}</span>{metrics['rejected_row_pct']}% of input</div></div>"
    document+="<section><h2>On-time delivery by hub</h2><p class='muted'>Delivered orders at or before the promised time ÷ all delivered orders. Scale: 0–100%.</p>"+bars+"</section><section><h2>Operations scorecard</h2><div class='scroll'><table>"+table+"</table></div></section><section><h2>Quality audit</h2><p>Rejected rows are quarantined, never silently repaired. All occurrences of a duplicated ID are excluded because the correct record cannot be established.</p><ul>"+rules+"</ul><p>Issue counts can exceed rejected rows when one row fails multiple rules.</p></section><footer>Prepared with AI assistance for Teja's portfolio. Synthetic patterns do not describe any real company. See README for definitions, limitations and reproduction.</footer></main></html>"
    (output/'dashboard.html').write_text(document)
    worst=min(kpis,key=lambda r:r['on_time_pct'])
    (output/'findings.md').write_text(f"# Results on fictional sample data\n\n{len(rows)} input rows; {len(clean)} accepted; {len(bad)} quarantined.\n\n{worst['hub']} has the lowest on-time rate ({worst['on_time_pct']}%). This gap was deliberately introduced in the data generator; it is not a real business discovery.\n\nIn a real operation, investigate demand, staffing, inventory and route duration before recommending changes. Compare within similar hours and order profiles.\n")
    print(json.dumps(metrics,indent=2));print('Dashboard: outputs/dashboard.html')
if __name__=='__main__': main()
