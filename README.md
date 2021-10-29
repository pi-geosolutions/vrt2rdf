# vrt2rdf
**Generate a RDF geographic thesaurus from a VRT file**

*The simplest way to transform a bunch of geospatial resources into an RDF thesaurus for use in GeoNetwork*

---
## Install

Create a virtual env and install the requirements

        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt

You will need the gdal library. You will probably have to adjust the version in the requirements.txt file
The simplest way:
- install gdal and libgdal1-dev packages on your computer
- install pygdal using
     
        pip install pygdal=="`gdal-config --version`.*"
        
### Compatibility
This code has been tested under python 3.7. It will probably work with an older version of python3, but with no garanties.

## Run it
```
python3 vrt2rdf.py data/limites.vrt
```
### Use a different template
By default, it will use the templates/territoires.rdf.j2 jinja2 template. You can use a different one. Just use the option `--template`:
```
python3 vrt2rdf.py --template mytpl.rdf.j2 data/limites.vrt
```
### Output file
By default, it will extract the name of the output file from the template name: it removes the path and the jinja extension. To set a different path/name, use the -o option
```
python3 vrt2rdf.py -o /tmp/myrdf.rdf data/limites.vrt
```

## How it works

### VRT for the input
A GDAL/OGR VRT file allows to abstract from the original source and prepare the data to make it suitable for this script. 
Thanks to the VRT intermediate file, the script can be kept simple and tidy: most of the configuration/transformation is done in the VRT file.

To know more about VRT format, you can [read its documentation](https://gdal.org/drivers/vector/vrt.html).

To see a working example, inspect [data/limites.vrt](data/limites.vrt)

#### Expected fields
It is expected that your VRT file exposes the following fields:
- `id`: identifier. It will be used in the rdf:about attribute
- `name`: the label to use. For now, the script doesn't support multilingual
- a geometry in EPSG:4326 (the envelope will be computed by the script)

Some additional fields will be used if provided:
- `admin_type`: will be appended to the name, in parenthesis (useful when combining several administrative levels)
- `narrower_ids`: a comma-separated list of identifiers for narrower entries. It will add skos:narrower resources
- `narrower_prefix`: the prefix will be added before the id. Ex. `DEP_` with an id 60 will produce `DEP_60` 
- `broader_ids`: a comma-separated list of identifiers for broader entries. It will add skos:broader resources
- `broader_prefix`: the prefix will be added before the id. Ex. `DEP_` with an id 60 will produce `DEP_60` 

### Connect any data source using the VRT
The VRT format is able to connect to many sources, so you're not limited to using only one file. You can combine in a single VRT file sources from a gpkg, a shapefile and a WFS service, it will still work.  

For instance, to read the PNR data from WFS, you could use the following source definition
```xml
  <OGRVRTLayer name="pnr2">
    <SrcDataSource>WFS:https://www.geo2france.fr/geoserver/spld/ows?request=GetCapabilities&service=WFS</SrcDataSource>
    <SrcSql dialect="sqlite">SELECT id_mnhn, nom, 'PNR' AS admin_type, 'PNR_' AS skos_prefix, Envelope(Transform(geom,4326)) AS geom FROM "spld:pnr"</SrcSql>
    <SrcLayer>spld:pnr</SrcLayer>
    <LayerSRS>EPSG:4326</LayerSRS>
    <Field name="id" type="String" src="id_mnhn" width="30"/>
    <Field name="name" type="String" src="nom" width="254"/>
    <Field name="admin_type" type="String" src="admin_type" width="20"/>
    <Field name="skos_prefix" type="String" src="skos_prefix" width="10"/>
  </OGRVRTLayer>
```
Additionnally, don't forget you can use /vsicurl/ and /vsizip/ to configure online direct access to zipped data.

### Python OGR to collect the features
The script scans through the layers and collects all the features in memory. For convenience, the OGR features are converted to an internal `SkosFeature` object to make it easier to use later.

### Jinja2 template
The features collection is fed to a jinja2 templates to generate the final output. This way, it is easy to change the output by simply using a different template.
