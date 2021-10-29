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