# Globalink Sample - Complete Metadata Snapshot

This snapshot corresponds to the ten records in [`globalink-public-sample-10.md`](globalink-public-sample-10.md), retrieved 2026-08-17 from the public `sasprojectlistpaging` response. Long descriptions, research-area text, roles, and skills remain in the source response model; this file preserves the non-narrative metadata used for filtering, eligibility, and ranking.

## Identity, language, location, and timing

| ID | Language / alternate language | Start date (UTC) | Flexible? | Timing note | City | Province |
| --- | --- | --- | --- | --- | --- | --- |
| 51146 | English / null | 2027-05-03T04:00:00Z | Yes | - | london ontario | Ontario |
| 51147 | English / null | 2027-05-03T04:00:00Z | Yes | - | london ontario | Ontario |
| 51148 | English / null | 2027-05-03T04:00:00Z | Yes | - | london ontario | Ontario |
| 51149 | French / null | 2027-05-03T03:00:00Z | Yes | Ideally arrive in May, not June; fieldwork begins in early June. | Shippagan | New Brunswick |
| 51150 | English / null | 2027-05-03T07:00:00Z | Yes | - | Kelowna | British Columbia |
| 51151 | English / null | 2027-05-03T04:00:00Z | Yes | all summer | Montreal | Québec |
| 51152 | English / null | 2027-05-03T07:00:00Z | Yes | Supervisor says the start date is flexible if needed. | Kamloops | British Columbia |
| 51154 | English / null | 2027-05-03T07:00:00Z | Yes | - | Vancouver | British Columbia |
| 51155 | English / English | 2027-05-03T07:00:00Z | Yes | Supervisor says the start date is flexible. | Victoria | British Columbia |
| 51156 | English / null | 2027-06-01T04:00:00Z | Yes | - | Toronto | Ontario |

## Professor, institution, and background metadata

| ID | Professor | University | University ID | Faculty province | Campus | Preferred-background IDs |
| --- | --- | --- | ---: | --- | --- | --- |
| 51146 | Domenico Santoro | Western University | 56 | Ontario | London | [88,73,68] |
| 51147 | Domenico Santoro | Western University | 56 | Ontario | London | [88,73,68,65] |
| 51148 | Domenico Santoro | Western University | 56 | Ontario | London | [88,73,68,65] |
| 51149 | Jessica ANDRIAMASINORO | Université de Moncton | 26 | New Brunswick | Shippagan | [93,119,207] |
| 51150 | Mohammad Zarifi | University of British Columbia | 14 | British Columbia | Okanagan | [71] |
| 51151 | decio coviello | HEC Montréal | 65 | Québec | Montréal | [46,45] |
| 51152 | Bala Nikku | Thompson Rivers University | 12 | British Columbia | Kamloops | [5,8,11,31,202,40,44,42,100,118,119,159,189,205,207] |
| 51154 | Haibo Feng | University of British Columbia | 14 | British Columbia | Vancouver | [31,57,69,70,73,76,104] |
| 51155 | Rishi Gupta | University of Victoria | 17 | British Columbia | Victoria | [69,80,88] |
| 51156 | Amanda De Lisio | York University | 58 | Ontario | Toronto | [207,188,219] |

## Internship questionnaire metadata

The API returns `InternshipQ1` through `InternshipQ16` for each project. Q1-Q14 are frequency/fit signals, Q15 is a Yes/No signal, and Q16 may be null. Values are preserved below in field order `Q1,Q2,...,Q16`:

| ID | Q1-Q16 values |
| --- | --- |
| 51146 | Often, Infrequently, Infrequently, Often, Often, Infrequently, Often, Often, Very often, Often, Infrequently, Often, Very often, Very often, No, null |
| 51147 | Very often, Infrequently, Infrequently, Often, Often, Infrequently, Often, Often, Very often, Very often, Infrequently, Often, Very often, Very often, No, null |
| 51148 | Very often, Almost never, Almost never, Often, Very often, Infrequently, Infrequently, Often, Very often, Often, Infrequently, Often, Very often, Often, No, null |
| 51149 | Very often, Very often, Very often, Never, Very often, Infrequently, Never, Never, Always, Never, Never, Very often, Very often, Often, No, null |
| 51150 | Always, Never, Never, Very often, Very often, Infrequently, Infrequently, Very often, Always, Always, Always, Very often, Always, Always, No, null |
| 51151 | Very often, Occasionally, Infrequently, Very often, Very often, Never, Never, Very often, Very often, Occasionally, Never, Very often, Very often, Very often, No, null |
| 51152 | Often, Occasionally, Occasionally, Often, Often, Occasionally, Never, Occasionally, Very often, Almost never, Never, Very often, Very often, Very often, Yes, null |
| 51154 | Always, Infrequently, Infrequently, Always, Very often, Almost never, Almost never, Very often, Always, Often, Infrequently, Always, Always, Always, No, null |
| 51155 | Very often, Occasionally, Infrequently, Very often, Very often, Often, Very often, Occasionally, Very often, Often, Very often, Very often, Very often, Very often, No, null |
| 51156 | Often, Occasionally, Occasionally, Never, Often, Never, Never, Occasionally, Very often, Never, Never, Occasionally, Often, Often, No, null |

## Schema audit result

The returned record schema also includes bilingual/alternate fields (`ProjectTitle2`, `ProjectDescription2`, `ResearchAreaDescription2`, `StudentRoles2`, `StudentSkills2`), `lang1`, and a nested `Professor` object duplicating the professor/university/campus fields. The matcher should preserve these fields rather than discard them, while normalizing the duplicated values into a single searchable project record.
