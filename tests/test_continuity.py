import pandas as pd

import jamra_continuity as jc


def synthetic(day=1.02, night=1.05):
    rows = []
    for region in range(4):
        for m in range(1, 13):
            for dn, k in (("D", day), ("N", night)):
                snpp = 100 + 10 * region + m
                rows.append({"region": region, "month": f"2024-{m:02d}-01", "year": 2024, "dn": dn,
                             "snpp": snpp, "noaa20": round(snpp * k)})
    return pd.DataFrame(rows)


def test_factor_recovered_day_and_night():
    m = jc.measure(synthetic())
    assert abs(m["factor"]["day"] - 1.02) < .01 and abs(m["factor"]["night"] - 1.05) < .01


def test_correction_beats_raw_noaa20():
    m = jc.measure(synthetic())
    assert m["error"]["corrected"] < m["error"]["raw_noaa20"]
    assert m["region_months"] == 4 * 12


def test_to_snpp_units_inverts_the_factor():
    m = jc.measure(synthetic())
    assert abs(jc.to_snpp_units(102, 105, m) - 200) < 2
