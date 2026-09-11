# B2660 — Bader Villa: drawing set review

Source file: `B2660-REV02- ( GROUND & BASEMENT).pdf`

## Sheet / file facts

| Property | Value |
|---|---|
| Pages | 2 (Ground Floor Plan, Basement Floor Plan) |
| Sheet size | 420 x 297 mm (A3 landscape), page rotation 270 |
| Producer | AutoCAD 2023 (English) via pdfplot16.hdi |
| PDF created | 31 Aug 2026 |
| Content | Pure vector, no raster images (49,724 paths on p1; 12,977 on p2) |
| Text | Labels are AutoCAD SHX Text annotations, not page text |

The file was assembled from two separate exports (`1.pdf` and `2.pdf`); both
AutoCAD layer sets survive as PDF optional-content groups (`WALLS`, `A-DOOR`,
`A-GLAZING`, `A-DIMN-100`, `P-FIXT`, `CAR`, `Railing`, `stair_Pen_No__3`,
`TRESS_Pen_No__64`, and others), so layers can still be toggled in a viewer.

## Title block

| Field | Value |
|---|---|
| Project owner | (blank) |
| Project type | Residential villa |
| Designer / reviewer | Arena Engineering Consultants (arenaarch.sa) |
| Location | Riyadh |
| Scale | N.T.S |
| Project code | B2660 |
| Date | June 2026 |
| Sheet no. | 001 |

## Site and areas

Total lot area 472.40 sqm. Slightly trapezoidal: 24010 mm on the street
frontage, 23210 mm at the rear, 20010 mm on one side and 20025 mm on the other.

| Level | Area | Coverage |
|---|---|---|
| Ground floor | 292.1 sqm | 61.83 % |
| Basement floor | 369.1 sqm | 78.13 % |
| First floor | (blank) | (blank) |
| Roof floor | (blank) | (blank) |

The first-floor and roof rows are empty, so this set is partial. The plans
themselves reference an upper level (`OPEN TO ABOVE` over the living area),
which is not drawn here.

The basement is larger than the ground floor because it extends under the
front and side yards. The hatched zone on the basement plan (roughly
12910 x 6710 to 11195 mm) is the unexcavated remainder of the lot, and its
area matches the 472.4 - 369.1 = 103.3 sqm difference.

## Orientation

Boundary labels read: street on one long side marked `NORTH STREET 15 M`,
`SOUTH NEIGHBOR` opposite, `EAST NEIGHBOR` and `WEST NEIGHBOR` on the short
sides. Those four labels are self-consistent and put north at the bottom of
the sheet.

The title-block north arrow points to the sheet's left, which is the edge
labelled `EAST NEIGHBOR`. The compass and the written labels disagree by
90 degrees. Worth confirming with the designer before using this set for
sun or setback studies.

## Ground floor

No bedrooms on this level. It is the reception and service floor, with the
guest wing and the family wing given separate wet blocks.

Guest and family spaces:

- **Majlis** 6600 x 5510 (about 36 sqm), on the street side, with its own
  adjacent wash 2400 x 1800 and toilet 1700 x 1800.
- **Sitting area** 5800 x 4300 (about 25 sqm), the family lounge, served by a
  second wash 2000 x 1800 and toilet 1700 x 1800.
- **Dining** 6000 x 5500 (33 sqm) and **living area** 6000 x 5500 (33 sqm) share
  a 12000 mm run along the rear wall. The living area is double height, tagged
  `OPEN TO ABOVE`, with a 4000 mm void.
- **Entrance** lobby with a 600 mm deep abayah cabinet.

Service spaces:

- **Kitchen** 3800 x 5000 (19 sqm) with a counter and sliding door to the dining room.
- **Storage** 2200 x 5000 (11 sqm).
- **Maid room** 2000 x 3600 with private bath 2000 x 1200.

Circulation:

- Main stair in the lobby, 26 risers, 4300 x 5500 flight.
- Second stair near the entrance, marked `DN`, descending to the basement.
- Elevator 1800 x 1800, serving both drawn levels.

Outdoor:

- Two-car open parking, bays about 3700 mm wide, yard 12910 x 6330.
- Planters along the facade, a row of six tree pits in the street setback,
  a 2500 mm double-leaf pedestrian gate and a 3000 mm vehicle entry with steps.

## Basement

Treated as a full second living floor rather than storage, and daylit by
sunken courtyards. Four `OPEN ABOVE` voids on this plan match the
`OPEN BELOW` voids on the ground floor.

- **Sitting area**, the largest room, 11400 x 5500 within a 16000 mm run
  (about 63 sqm).
- **Dining** with a 10 to 12 seat table, in a 7100 x 8300 zone.
- **Open kitchen** with a 4600 mm island and three stools.
- **Gym** 6400 x 7510 (about 48 sqm) with equipment laid out, entered through a
  sliding door, and backed by a **locker** 2100 x 1800 and **bath** 2600 x 1800.
- **Office** 4800 x 4300 (about 21 sqm).
- **Kids playing room** 4200 x 3900 (about 16 sqm).
- **Storage** 2800 x 2200, **wash** 2400 x 2200, **toilet** 1600 x 2200.
- Two **outdoor sitting** terraces, 3300 x 3710 and 9800 x 2510.
- Stair of 24 risers matching the ground-floor `DN`, plus the same elevator.

## Open questions

1. The compass and the boundary labels disagree, as noted above.
2. First floor and roof are referenced but not drawn, and their area rows are blank.
3. Scale is marked N.T.S on an A3 sheet, so nothing here should be measured
   off the paper. Every figure above is read from a dimension string.
4. The project owner field is blank.
