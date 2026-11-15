# jamra-continuity — keep the fire record going after Suomi NPP

Team TFC · NASA Space Apps 2026 · part of [JAMRA](https://jamra.tfs.ink).

[العربية ↓](#العربية)

## What it does
NASA stopped Suomi NPP fire data on **2 November 2026**. The harmonized record built by
[FireCal](https://github.com/qudah269-ops/firecal) is in **VIIRS S-NPP units**, so after that day it can only continue
with **NOAA-20**: the same VIIRS instrument on the same orbit, but not the same counts.

Where both satellites saw the same places (April 2018 to the end of 2025) this measures:

- the **NOAA-20 / S-NPP ratio**, by day and by night, from the last three full years (2023–2025, after NOAA-20's
  calibration settled);
- the **ratio of every year on its own**, to show whether it drifts;
- the **error per region × month** (H3 resolution 2, months with at least 20 S-NPP detections) when the record is continued
  with NOAA-20 divided by the factor, against raw NOAA-20.

Then `to_snpp_units(day, night, m)` turns new NOAA-20 counts into S-NPP-equivalent counts.

## Results
Eastern Mediterranean and Levant, FIRMS VIIRS standard-quality points (vegetation fires, `type = 0`, confidence not low):

| | value |
|---|---|
| factor, day (2023–2025) | **×1.023** |
| factor, night (2023–2025) | **×1.047** |
| region-months compared | 823 |
| median error, raw NOAA-20 | 14.7 % |
| median error, NOAA-20 ÷ factor | **13.9 %** |

The yearly ratio was 0.83 in 2018 and 0.88 in 2019, then stayed between 1.01 and 1.07 from 2021 to 2025. That is why only
the last three years set the factor. Both errors are under the 19.7 % noise floor measured between S-NPP and NOAA-20
in FireCal's validation: the switch costs less than the noise already in the data.

## Install
```bash
uv sync
uv run pytest -q
```

## Minimal example
```python
import jamra_continuity as jc

m = jc.measure(jc.table("data_real/points/**/*.parquet"))   # FireCal points
print(m["factor"], m["error"])
print(jc.to_snpp_units(n_day=120, n_night=40, m=m))         # NOAA-20 counts -> S-NPP units
```
or `uv run jamra-continuity measure --points 'data_real/points/**/*.parquet'`.

## Data
No data is committed. The points are FireCal's ingest of NASA FIRMS archive files (VIIRS S-NPP `SV-C2` and NOAA-20
`J1V-C2`); see FireCal's `scripts/download_firms.py`.

## Honest limits
- **NOAA-21** has no public yearly FIRMS archive yet (only the keyed API), so it is not measured here.
- One factor per day/night for the whole area: local differences (fire size, terrain) are averaged out.
- The factor is measured to 2025; if NOAA-20's calibration changes again, measure again.

<div dir="rtl">

## العربية

# jamra-continuity — السجل بيكمّل بعد Suomi NPP

### شو بيعمل
ناسا وقّفت بيانات Suomi NPP يوم **2 نوفمبر 2026**. السجل الموحّد اللي بيبنيه [FireCal](https://github.com/qudah269-ops/firecal)
بوحدات **VIIRS S-NPP**، فبعد هاليوم ما بيكمّل إلا بـ **NOAA-20**: نفس جهاز VIIRS ونفس المدار، بس العدّ مش نفسه.

من الأماكن اللي صوّرها القمرين مع بعض (نيسان 2018 لآخر 2025) بنقيس:
- **نسبة NOAA-20 / S-NPP** بالنهار وبالليل، من آخر 3 سنين كاملة (2023–2025، بعد ما استقرّت معايرة NOAA-20)؛
- **النسبة كل سنة لحالها**، عشان يبيّن إذا بتنجرف؛
- **الخطأ لكل منطقة × شهر** إذا كمّلنا بـ NOAA-20 مقسوم على النسبة، مقابل NOAA-20 خام.

### النتائج
النسبة: **×1.023 بالنهار** و**×1.047 بالليل**. على 823 منطقة × شهر، الخطأ الوسيط نزل من 14.7% (NOAA-20 خام)
لـ **13.9%** بعد التصحيح، وهو أقل من أرضية الضجيج بين القمرين (19.7%). النسبة كانت 0.83 سنة 2018، وصارت بين
1.01 و1.07 من 2021 لـ 2025، ولهيك بناخد آخر 3 سنين بس.

### حدود بصراحة
- **NOAA-21** ما إله أرشيف سنوي مفتوح بـ FIRMS لسّا، فمش مقاس هون.
- نسبة وحدة للنهار ووحدة لليل لكل المنطقة.
- النسبة مقاسة لحد 2025؛ إذا تغيّرت معايرة NOAA-20، لازم تنقاس من جديد.

</div>

## License
MIT, see [LICENSE](LICENSE). Data keep their own terms: NASA FIRMS (open).
