# Attribution comparison

502 conversions credited across 10 channels by six models.

![Attribution by model](attribution.svg)

| Channel | Last touch | First touch | Linear | Time decay | Position based | Markov (data-driven) |
|---|---:|---:|---:|---:|---:|---:|
| Instagram creators | 43 | 199 | 121 | 103 | 121 | 88 |
| Email | 138 | 0 | 73 | 88 | 71 | 77 |
| Google brand search | 183 | 0 | 63 | 85 | 79 | 71 |
| SEO blog | 18 | 71 | 61 | 55 | 52 | 68 |
| Meta ads | 7 | 115 | 45 | 34 | 54 | 50 |
| Meta retargeting | 30 | 0 | 41 | 44 | 27 | 42 |
| YouTube | 10 | 0 | 30 | 30 | 16 | 35 |
| TikTok | 2 | 68 | 26 | 20 | 31 | 28 |
| Direct | 66 | 0 | 22 | 30 | 28 | 26 |
| LinkedIn | 5 | 49 | 19 | 15 | 24 | 19 |

## What it means for budget

- **SEO blog** gets 68 conversions under the data-driven model but only 18 under last touch. It opens and nurtures journeys that other channels close. Cutting it on last-touch numbers would hurt total sales.
- **Instagram creators** gets 88 conversions under the data-driven model but only 43 under last touch. It opens and nurtures journeys that other channels close. Cutting it on last-touch numbers would hurt total sales.
- **Google brand search** gets 183 under last touch but 71 under the data-driven model. It mostly captures demand other channels created, so scaling it alone will hit diminishing returns.

<sub>Markov model: first-order chain, credit by removal effect. Fictional data from attribution/sample.py.</sub>
