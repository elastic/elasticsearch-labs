## Geospatial data ingest for ES|QL

This folder contains sample data used in the blogs:

* [Geospatial data ingest for ES|QL](https://www.elastic.co/search-labs/blog/geospatial-data-ingest)
* [Geospatial search with ES|QL](https://www.elastic.co/search-labs/blog/esql-geospatial-search-part-one)
* [Geospatial distance search with ES|QL](https://www.elastic.co/search-labs/blog/esql-geospatial-search-part-two)

The data we used for the examples in these blogs were based on data we use internally for integration tests.
This in turn was created by merging data from a few different souces with
the goal of creating datasets appropriate for testing a number of specific
ES|QL features as they were developed.

* [airports.csv](https://raw.githubusercontent.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/geospatial-data-ingest/airports/airports.csv)
  * This contains a merger of three datasets:
    * Airports (names, locations and related data) from [Natural Earth](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/airports/)
    * City locations from [SimpleMaps](https://simplemaps.com/data/world-cities)
    * Airport elevations from [The global airport database](https://www.partow.net/miscellaneous/airportdatabase/)
* [airport_city_boundaries.csv](https://raw.githubusercontent.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/geospatial-data-ingest/airports/airport_city_boundaries.csv)
  * This contains a merger of airport and city names from above with one new source:
    * City boundaries from [OpenStreetMap](https://www.openstreetmap.org/)

### Licensing and attribution

Since this data is derived from various sources, we list the license
conditions for each, some of which also require attribution:

* Natural Earth (original dataset with airport names, locations and related
  information)
  * Released in the public domain with no requirement for attribution. See
  https://www.naturalearthdata.com/about/terms-of-use/.
* SimpleMaps (city locations)
  * License: Creative Commons Attribution 4.0 license as described at: https://creativecommons.org/licenses/by/4.0/
  * Requires attribution and link to https://simplemaps.com/data/world-cities
* Global Airport Database (airport elevations)
  * Licensed under MIT license - http://www.opensource.org/licenses/MIT
  * Requires attribution: https://www.partow.net/miscellaneous/airportdatabase/
* OpenStreetMap (city boundary polygons)
  * Licensed with Open Database License (ODbL) v1.0 - https://opendatacommons.org/licenses/odbl/1-0/
  * Requires attribution
  * Requires that derived data be shared under a compatible license

The most restrictive license here is the [Open Database License (ODbL)
v1.0](https://opendatacommons.org/licenses/odbl/1-0/) because it as a
'ShareAlike' clause. For this reason we are sharing this combined dataset
using the same license.

### Changes made to the data

Several of the above licenses also require that any changes made from the
original source data are clearly indicated. This can be done by explaining
the process used to create the final results:

* The original airports name, IATA code, location, type and scalerank were
  obtained from the Natural Earth dataset. The only changes made were to
  reformat into a CSV format, with the locations expressed in WKT, since the
  original format was ESRI Shapefile.
* The city locations from SimpleMaps were download and then only the subset
  of cities reasonably identifiable as the closest major city to one of the
  existing airport locations was selected and merged into the airports.csv
  file. So the edit in question is simply a subset selection.
* The airport elevations were similarly a subset selection of airports from
  the 'global airport database' where IATA codes matched the existing set of
  airports in our dataset.
* The city boundaries were found from OpenStreetMap. The process to
  determine the boundaries was complex, for many reasons including the fact
  that OSM data is massive. We downloaded OSM.PDB files for various regions of
  the world from the Geofabrik download server at
  https://download.geofabrik.de/. For each region we imported the PDF files
  into PostGIS, and then searched for appropriate polygons surounding cities
  serving the airports of interest. This was achieved using several complex
  SQL queries. The selected polygons were further simplified using
  `ST_SimplifyPreserveTopology` calls with various resolutions to generate
  city polygons of appropriate levels of detail.
