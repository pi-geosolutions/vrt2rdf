import os
import logging
import argparse
from datetime import datetime
from jinja2 import Template
from osgeo import ogr


logger = logging.getLogger()
rdf_template = "templates/territoires.rdf.j2"
rdf_out_file = "territoire.rdf"


class SkosFeature():
    def __init__(self, ogr_feature):
        self.feature = ogr_feature
        self.id = self.get_field_or_null('id')
        self.name = self.get_field_or_null('name')
        self.description = self.get_field_or_null('description')
        self.admin_type = self.get_field_or_null('admin_type')
        self.skos_prefix = self.get_field_or_null('skos_prefix')
        self.narrower_prefix = self.get_field_or_null('narrower_prefix')
        self.narrower_ids = self.get_field_or_null('narrower_ids')
        self.broader_prefix = self.get_field_or_null('broader_prefix')
        self.broader_ids = self.get_field_or_null('broader_ids')
        try:
            (minX, maxX, minY, maxY) = ogr_feature.GetGeometryRef().GetEnvelope()
            self.minX = minX
            self.maxX = maxX
            self.minY = minY
            self.maxY = maxY
        except:
            pass

    def get_field_or_null(self, fid):
        try:
            return self.feature[fid]
        except:
            return None

    def get_broader_ids_as_list(self):
        if self.broader_ids:
            return self.broader_ids.split(',')
        else:
            return []

    def get_narrower_ids_as_list(self):
        if self.narrower_ids:
            return self.narrower_ids.split(',')
        else:
            return []


def main():
    # Input arguments
    parser = argparse.ArgumentParser(description='''
    Reads the input VRT, iterates through the layers and produces a RDF thesaurus suitable for GeoNetwork as a 
    geographic thesaurus. Using VRT as input, it allows you a lot of flexibility in the data sources you want to use, 
    the VRT providing an abstraction layer between your data sources and this script.
    ''')
    parser.add_argument('vrtfile', metavar='VRT file path', help='an integer for the accumulator')
    parser.add_argument('-o', '--out_file',
                        help='Output file name. Default: name of the template, without the jinja extension')
    parser.add_argument('-v', '--verbose', help='verbose output (debug loglevel)',
                        action='store_true')
    parser.add_argument('--logfile',
                        help='logfile path. Default: prints logs to the console')
    parser.add_argument('-t', '--template',
                        help='template file path. Default: templates/territoires.rdf.j2')
    args = parser.parse_args()


    # INITIALIZE LOGGER
    handler = logging.StreamHandler()
    if args.logfile:
        handler = logging.FileHandler(args.logfile)

    formatter = logging.Formatter(
            '%(asctime)s %(name)-5s %(levelname)-3s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    logger.setLevel(loglevel)

    # Initialize global vars
    if args.template:
        global rdf_template
        rdf_template = args.template

    global rdf_out_file
    if args.out_file:
        rdf_out_file = args.out_file
    else:
        # extract the output file name from the template file (removing the path and the jinja extension)
        rdf_out_file = os.path.splitext(os.path.basename(rdf_template))[0]

    vrt2rdf(args.vrtfile)


def vrt2rdf(filename):
    features = collect_features(filename)
    skos_xml = features_to_skos_xml(features)
    logger.debug(skos_xml)
    if skos_xml:
        logger.info("Writing RDF data to {}".format(rdf_out_file))
        with open(rdf_out_file, 'w') as f:
            f.write(skos_xml)


def features_to_skos_xml(features):
    logger.info("Using template file {}".format(rdf_template))
    with open(rdf_template) as file_:
        template = Template(file_.read())
        rdf_xml=template.render(date=datetime.now(), feats=features)
        return rdf_xml


def get_features_from_layer(layer):
    logger.info('Processing layer {}'.format(layer.GetName()))
    features_list = []
    layer_defn = layer.GetLayerDefn()
    fieldnames = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    layer.ResetReading()
    for feature in layer:
        f = SkosFeature(feature)
        features_list.append(f)

    logger.info("Collected {} features".format(len(features_list)))
    return features_list


def collect_features(filename):
    inDataSource = ogr.Open(filename)
    features_list = []
    for layer_id in range(inDataSource.GetLayerCount()):
    # for layer_id in range(2):
        layer = inDataSource.GetLayerByIndex(layer_id)
        feats = get_features_from_layer(layer)
        if feats:
            features_list = [*features_list, *feats]
    return features_list


if __name__ == '__main__':
    main()