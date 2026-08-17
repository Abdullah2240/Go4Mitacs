# Globalink Public Project Sample - 10 Records

Retrieved 2026-08-17 from the public Globalink paging endpoint. Request body:

```json
{
  "HostProvinceName": null,
  "HostUniversityID": null,
  "HostCampusID": null,
  "LanguageUsed": null,
  "keyword": null,
  "FirstName": null,
  "LastName": null,
  "AcademicDiscipline": null,
  "PreferredBackgroundCollection": null,
  "offset": 0,
  "limit": 10
}
```

The endpoint reported 3,359 public projects. This is a deliberately small validation sample, not a ranking or shortlist.

| ID | Project | Institution / supervisor | Language | Focus |
| --- | --- | --- | --- | --- |
| 51146 | HYDRO-WASTE: Hydroponic Systems for Water Treatment and Sustainable Nutrient Recovery | Western University - Domenico Santoro | English | Hydroponic wastewater treatment, nutrient recovery, water-quality analysis, modelling, and process optimization. |
| 51147 | CLEAN-CARB: Carbon-Based Solutions for Efficient Nutrient Management in Wastewater | Western University - Domenico Santoro | English | Biochar/activated-carbon nutrient management, adsorption, wastewater experiments, and modelling. |
| 51148 | QUICK-PATH: Quaternary Innovative Control of Pathogens and Micropollutants in Wastewater | Western University - Domenico Santoro | English | Advanced oxidation, ozonation and UV treatment; analytical chemistry and treatment-process modelling. |
| 51149 | La pratique du jardinage alimentaire domestique des personnes immigrantes de la ville de Moncton : objectifs et potentiel d’intégration | Université de Moncton - Jessica Andriamasinoro | French | Community study of immigrant household food gardening and its integration potential. |
| 51150 | AI-Enabled Edge Microwave Sensor for Harsh Environment Applications | University of British Columbia, Okanagan - Mohammad Zarifi | English | Microwave/RF sensing, edge AI, embedded systems, sensor fusion, simulation, and prototyping. |
| 51151 | Applied Economics Using Big Data and LLMs | HEC Montréal - decio coviello | English | Big data, LLMs, applied econometrics, policy-relevant economic questions, and data analysis. |
| 51152 | Mapping Disasters, Displacement and Development to build Community Resilient Futures | Thompson Rivers University - Bala Nikku | English | Disaster/displacement mapping, social-media data, GIS, research methods, and resilient-community planning. |
| 51154 | Predicting the energy performance and energy use of urban buildings in Vancouver | University of British Columbia, Vancouver - Haibo Feng | English | Geospatial techniques, urban building data, 3D models, energy simulation, and climate analysis. |
| 51155 | Use of Non-destructive evaluation techniques for Civil infrastructure | University of Victoria - Rishi Gupta | English | Non-destructive testing, sensors/data acquisition, sustainable composites, computational analysis, and image analysis. |
| 51156 | Insurgent Feminism: Community History-Making and Sex Worker Activism in the Global South | York University - Amanda De Lisio | English | Brazilian literature/translation and community history research in urban geography and feminist/decolonial methods. |

## Fields verified in the returned records

The public response includes: project ID, bilingual title/description variants where available, research-area description, student roles, student skills, preferred academic-background IDs, start-date information, city/province, language, university/campus, and supervisor details. The eventual importer should preserve these raw fields alongside normalized fields and the retrieval timestamp.
