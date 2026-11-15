"""
jamra_continuity.model (JAMRA continuity.py) — حمل السجل الموحّد عبر توقّف Suomi NPP (2 نوفمبر 2026)

ناسا وقّفت بيانات S-NPP، والبديل NOAA-20 وNOAA-21: نفس جهاز VIIRS ونفس المدار.
السجل الموحّد عندنا بوحدات VIIRS S-NPP، فعشان يكمل بعد 2 نوفمبر لازم نعرف قديش NOAA-20 بيشوف
مقارنة بـ S-NPP. عنا الاثنين بنفس الأماكن من 2018-04 لآخر 2025، فبنقيس:

  · نسبة NOAA-20 / S-NPP بالنهار وبالليل، من آخر 3 سنين كاملة (بعد ما استقرّت معايرة NOAA-20)؛
  · كل سنة لحالها، عشان يبيّن إذا النسبة بتنجرف؛
  · الخطأ على مستوى المنطقة × الشهر إذا كمّلنا بـ NOAA-20 مضروب بالنسبة، مقابل NOAA-20 خام.

NOAA-21 ما إله ملفات سنوية عامة بـ FIRMS (بس API بمفتاح)، فهو مش بالقياس لسا.
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

RETIRED = "2026-11-02"
RECENT = (2023, 2025)            # آخر 3 سنين كاملة
REGION_RES = 2                   # نفس مستوى أرضية الضجيج (19.7%) بالتحقق


def table(points_glob, start="2018-04-01"):
    con = duckdb.connect()
    try:
        con.sql("LOAD h3")
    except duckdb.Error:  # first run on this machine
        con.sql("INSTALL h3 FROM community")
        con.sql("LOAD h3")
    return con.sql(f"""
        select h3_cell_to_parent(h3_fine, {REGION_RES})::bigint as region, date_trunc('month', acq_date)::date as month,
               year(acq_date) as year, daynight as dn,
               sum((satellite = 'snpp')::int) as snpp, sum((satellite = 'noaa20')::int) as noaa20
        from read_parquet('{points_glob}', hive_partitioning = 1)
        where type = 0 and conf_class <> 'low' and satellite in ('snpp', 'noaa20') and acq_date >= '{start}'
        group by 1, 2, 3, 4""").df()


def measure(t):
    """t: table() rows. Returns the factors, the yearly drift and the error with and without the factor."""
    rec = t[t["year"].between(*RECENT)]
    f = {dn: float(rec.loc[rec.dn == dn, "noaa20"].sum() / max(1, rec.loc[rec.dn == dn, "snpp"].sum())) for dn in ("D", "N")}
    yearly = t.groupby("year")[["snpp", "noaa20"]].sum()
    yearly = [{"year": int(y), "snpp": int(r.snpp), "noaa20": int(r.noaa20), "ratio": round(r.noaa20 / max(1, r.snpp), 3)}
              for y, r in yearly.iterrows()]
    # region × month, day and night corrected separately, judged on the recent years
    rec = rec.assign(pred=rec["noaa20"] / rec["dn"].map(f))
    rm = rec.groupby(["region", "month"])[["snpp", "noaa20", "pred"]].sum()
    rm = rm[rm["snpp"] >= 20]                                   # the same small-count floor as the regional checks
    err = lambda p: float(np.median(np.abs(p - rm["snpp"]) / rm["snpp"]))
    return {"retired": RETIRED, "fit_years": f"{RECENT[0]}–{RECENT[1]}",
            "factor": {"day": round(f["D"], 3), "night": round(f["N"], 3)},
            "yearly": yearly, "region_months": int(len(rm)),
            "error": {"raw_noaa20": round(err(rm["noaa20"]), 3), "corrected": round(err(rm["pred"]), 3)},
            "use": "after 2026-11-02: S-NPP units = NOAA-20 detections ÷ factor (day and night separately)"}


def to_snpp_units(n_day, n_night, m):
    """Continue the record: NOAA-20 counts → S-NPP-equivalent counts with the measured factors."""
    return n_day / m["factor"]["day"] + n_night / m["factor"]["night"]


def main(argv=None):
    """measure: read FireCal points (FIRMS VIIRS, S-NPP and NOAA-20) and print the factors and the error."""
    import argparse
    import json
    p = argparse.ArgumentParser(description=main.__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--points", required=True, help="FireCal points parquet glob, e.g. 'data_real/points/**/*.parquet'")
    m.add_argument("--start", default="2018-04-01", help="first day NOAA-20 data is used (its first full month)")
    a = p.parse_args(argv)
    print(json.dumps(measure(table(a.points, a.start)), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
