"""Build aggregate comparison and dashboard from the Stats NZ source CSV."""
import argparse
import csv
import html
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def calculate(path):
    with sqlite3.connect(":memory:") as db, open(path, encoding="utf-8-sig", newline="") as f:
        db.execute("""CREATE TABLE daily (
            yr INTEGER, month_day TEXT, country TEXT, commodity TEXT,
            mode TEXT, nzd INTEGER,
            PRIMARY KEY (yr, month_day, country, commodity, mode))""")
        def rows():
            for r in csv.DictReader(f):
                if r["Direction"] == "Exports" and r["Measure"] == "$" and r["Year"] in {"2019", "2020", "2021"}:
                    date = datetime.strptime(r["Date"], "%d/%m/%Y")
                    assert date.year == int(r["Year"])
                    yield date.year, date.strftime("%m-%d"), r["Country"], r["Commodity"], r["Transport_Mode"], int(r["Value"])
        db.executemany("INSERT INTO daily VALUES (?, ?, ?, ?, ?, ?)", rows())
        results = db.execute((ROOT / "analysis.sql").read_text()).fetchall()
    assert results and all(n == 243 for *_, n in results), "Missing or duplicate observations in a reporting series"
    annual = {(kind, label, yr): value for kind, label, yr, value, days in results}
    totals = [annual["Total", "All", yr] for yr in (2019, 2020, 2021)]
    commodities = sorted({name for typ, name, *_ in results if typ == "Commodity"})
    residual = [total - sum(annual["Commodity", name, yr] for name in commodities)
                for yr, total in zip((2019, 2020, 2021), totals)]
    out = []
    for kind, label in sorted({(k, l) for k, l, *_ in results}):
        values = [annual[kind, label, y] for y in (2019, 2020, 2021)]
        out.append((kind, label, *values, values[2]-values[0]))
    out.append(("Commodity residual", "All other commodities / rounding", *residual, residual[2]-residual[0]))
    assert sum(r[-1] for r in out if r[0].startswith("Commodity")) == totals[2] - totals[0]
    return totals, out


def make_svg(totals, rows):
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 675" role="img" aria-labelledby="title desc">',
         '<title id="title">New Zealand Goods Export Recovery</title>',
         '<desc id="desc">January to August exports in 2019, 2020 and 2021, with commodity contributions to the 2021 change versus 2019.</desc>']

    def rect(x,y,w,h,c,r=0):
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}"/>')

    def txt(x,y,v,n=14,c="#173448",w=400):
        s.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{n}" fill="{c}" font-weight="{w}">{html.escape(str(v))}</text>')

    rect(0,0,1100,675,"#eef4f6")
    rect(0,0,1100,143,"#142f43")
    txt(34,32,"PORTFOLIO CASE STUDY  /  SUPPLY CHAIN ANALYTICS",13,"#87e0ce",700)
    txt(34,76,"New Zealand Goods Export Recovery",38,"#ffffff",700)
    txt(34,113,"January–August comparison  |  2019 baseline  |  NZD, nominal",17,"#d8eaf4")
    for i,(year,total) in enumerate(zip((2019,2020,2021),totals)):
        x=34+i*349
        rect(x,160,334,78,"#ffffff",10)
        txt(x+15,184,f"{year} goods exports",13,"#45647a",700)
        txt(x+15,218,f"NZ${total/1e9:.2f}B",26,w=700)
    rect(34,256,1032,296,"#ffffff",10)
    txt(51,285,"What drove the change from 2019 to 2021?",20,w=700)
    txt(51,308,"Change in export value, NZ$ millions  |  each commodity at the national level",13,"#45647a")
    diffs=sorted([(r[1],r[-1]) for r in rows if r[0].startswith("Commodity")],key=lambda p:-p[1])
    maxabs=max(abs(v) for _,v in diffs)
    rect(590,325,1,212,"#b7cad6")
    for i,(label,v) in enumerate(diffs):
        y=337+i*30
        txt(51,y+6,label,13,w=700)
        width=abs(v)*360/maxabs
        rect(590 if v>=0 else 590-width,y-6,width,14,"#147d74" if v>=0 else "#ba6246",3)
        txt(966,y+6,f"{v/1e6:+,.0f}M",13,w=700)
    delta=totals[2]-totals[0]
    rect(34,568,1032,63,"#d9ebee",10)
    txt(51,593,f"2021 vs 2019: {delta/1e9:+.2f}B NZD ({delta/totals[0]:+.1%})",16,w=700)
    txt(51,614,"Commodity movements are uneven. Nominal values combine price and volume effects.",13)
    txt(34,655,"Danish Syed  /  Source: Stats NZ, Effects of COVID-19 on trade, 1 September 2021 (provisional)",12,"#45647a")
    s.append("</svg>")
    return "\n".join(s)+"\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("csv",help="Stats NZ 1 September 2021 provisional CSV")
    totals,rows=calculate(p.parse_args().csv)
    with (ROOT/"export_comparison.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(["series","label","nzd_2019","nzd_2020","nzd_2021","delta_nzd_2021_vs_2019"])
        w.writerows(rows)
    (ROOT/"dashboard.svg").write_text(make_svg(totals,rows),encoding="utf-8")
    print(totals)

if __name__=="__main__":
    main()
