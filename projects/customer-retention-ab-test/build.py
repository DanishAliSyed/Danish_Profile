"""Build the results and chart for a synthetic retention experiment."""
import csv
import html
import math
import random
import sqlite3
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parent
MIN_LIFT = 0.02


def analyse():
    # Predetermined synthetic counts, shuffled within each arm for the row-level fixture.
    rng = random.Random(42)
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE experiment(
            subscriber_id INTEGER PRIMARY KEY,
            arm TEXT NOT NULL CHECK(arm IN ('control','reminder')),
            renewed_30d INTEGER NOT NULL CHECK(renewed_30d IN (0,1)))""")
        offset = 0
        for arm, n, k in [('control', 2400, 1440), ('reminder', 2400, 1548)]:
            outcomes = [1] * k + [0] * (n - k)
            rng.shuffle(outcomes)
            db.executemany("INSERT INTO experiment VALUES (?,?,?)", (
                (offset + i, arm, outcome) for i, outcome in enumerate(outcomes, 1)
            ))
            offset += n
        rows = db.execute((ROOT / 'analysis.sql').read_text()).fetchall()
    (_, n0, k0, p0), (_, n1, k1, p1) = rows
    lift = p1 - p0
    se = math.sqrt(p0*(1-p0)/n0 + p1*(1-p1)/n1)
    critical = NormalDist().inv_cdf(0.975)
    lo, hi = lift - critical*se, lift + critical*se
    return rows, lift, lo, hi


def dashboard(rows, lift, lo, hi):
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 625" role="img" aria-labelledby="title desc">',
         '<title id="title">Renewal Reminder A/B Test</title>',
         '<desc id="desc">Synthetic retention experiment: 60 percent control renewal, 64.5 percent reminder renewal, and a 4.5 percentage point lift with a confidence interval that crosses the 2 point rollout threshold.</desc>']

    def rect(x, y, w, h, fill, rx=0):
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>')

    def line(x1, y1, x2, y2, c, w=1):
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')

    def txt(x, y, v, n=14, c="#183247", w=400):
        s.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{n}" fill="{c}" font-weight="{w}">{html.escape(str(v))}</text>')

    rect(0,0,1000,625,"#eef4f7")
    rect(0,0,1000,150,"#142e43")
    txt(34,34,"PRODUCT ANALYTICS  /  SYNTHETIC EXPERIMENT",13,"#89e0cf",700)
    txt(34,81,"Does a renewal reminder improve retention?",33,"#ffffff",700)
    txt(34,118,"Primary outcome: renewed by 30 days after the scheduled expiry date",16,"#d6e7f2")
    for i,(arm,n,k,p) in enumerate(rows):
        x=34+i*312
        rect(x,169,300,90,"#ffffff",10)
        txt(x+14,193,arm.capitalize(),13,"#426278",700)
        txt(x+14,223,f"{p:.1%}",25,w=700)
        txt(x+14,246,f"{k:,} renewals / {n:,} assigned",12,"#426278")
    rect(658,169,308,90,"#ffffff",10)
    txt(672,193,"Absolute lift",13,"#426278",700)
    txt(672,223,f"{lift*100:+.1f} pp",25,w=700)
    txt(672,246,"Reminder minus control",12,"#426278")

    rect(34,278,932,192,"#ffffff",10)
    txt(51,308,"The lift is positive, but the rollout bar is still in doubt",19,w=700)
    txt(51,331,"Estimated lift with 95% confidence interval  |  percentage points",13,"#426278")
    x=lambda p: 87 + 100*p
    line(x(0),410,x(8),410,"#9fb3c4")
    for p in (0,2,4,6,8):
        line(x(p),406,x(p),416,"#9fb3c4")
        txt(x(p)-6,436,p,12,"#426278")
    line(x(2),358,x(2),410,"#b05235",2)
    txt(x(2)+8,367,"+2 pp rollout threshold",12,"#9b432c",700)
    line(x(100*lo),389,x(100*hi),389,"#167c72",5)
    for p in (lo,hi):
        line(x(100*p),382,x(100*p),397,"#167c72",2)
    s.append(f'<circle cx="{x(100*lift)}" cy="389" r="7" fill="#167c72"/>')
    txt(51,457,f"95% CI: {100*lo:+.2f} to {100*hi:+.2f} pp",13,"#426278",700)

    rect(34,488,932,92,"#daedef",10)
    txt(51,517,"Decision: run a confirmatory test before a full rollout",17,w=700)
    txt(51,542,"The lower bound is below +2 pp. Measure opt-outs and complaints in the next test.",14)
    txt(51,562,"These are simulated outcomes, not evidence about a real campaign.",13,"#426278")
    txt(34,605,"Danish Syed  /  SQL & Python  /  Synthetic data",12,"#426278")
    s.append("</svg>")
    return "\n".join(s)+"\n"


def main():
    rows,lift,lo,hi=analyse()
    with (ROOT/'results.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n')
        w.writerow(['arm','assigned_subscribers','renewals_30d','renewal_rate'])
        w.writerows(rows)
    with (ROOT/'lift.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n')
        w.writerow(['lift_pp','ci95_lower_pp','ci95_upper_pp','rollout_threshold_pp','meets_threshold'])
        w.writerow([f'{100*lift:.2f}',f'{100*lo:.2f}',f'{100*hi:.2f}',f'{100*MIN_LIFT:.2f}',str(lo >= MIN_LIFT).lower()])
    (ROOT/'dashboard.svg').write_text(dashboard(rows,lift,lo,hi),encoding='utf-8')
    print(rows)
    print(f"Lift {100*lift:+.2f} pp; 95% CI {100*lo:+.2f} to {100*hi:+.2f} pp")

if __name__ == '__main__':
    main()
