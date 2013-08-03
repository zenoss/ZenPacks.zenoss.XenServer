#!/usr/bin/env zendmd

"""
Build monitoring templates based on a YAML input file.

Look at monitoring_templates.yml in the same directory for an example of what
the YAML schema should be.

WARNING: This will delete and recreated the named monitoring templates. So it
         can potentially be very destructive.
"""

import re
import sys
import types

import yaml
import yaml.constructor

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

# TODO: Support other types of graph points.
from Products.ZenModel.GraphPoint import GraphPoint
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def main():
    # sys.argv[0] is zendmd. Pop it so the script can use normal conventions.
    sys.argv.pop(0)

    if len(sys.argv) < 2:
        data = yaml.load(sys.stdin.read(), OrderedDictYAMLLoader)
    else:
        with open(sys.argv[1], 'r') as yaml_file:
            data = yaml.load(yaml_file, OrderedDictYAMLLoader)

    for template_path, template_cfg in data.items():
        add_template(template_path, template_cfg)

    # commit comes from the zendmd interpreter.
    commit()


def die(msg, *args):
    print >> sys.stderr, msg % args
    sys.exit(1)


def add_template(path, cfg):
    if '/' not in path:
        die("%s is not a path. Include device class and template name", path)

    path_parts = path.split('/')
    id_ = path_parts[-1]
    cfg['deviceClass'] = '/'.join(path_parts[:-1])

    try:
        # dmd comes from the zendmd interpreter.
        device_class = dmd.Devices.getOrganizer(cfg['deviceClass'])
    except KeyError:
        die("%s is not a valid deviceClass.", cfg['deviceClass'])

    existing_template = device_class.rrdTemplates._getOb(id_, None)
    if existing_template:
        device_class.rrdTemplates._delObject(id_)

    device_class.manage_addRRDTemplate(id_)
    template = device_class.rrdTemplates._getOb(id_)

    if 'targetPythonClass' in cfg:
        template.targetPythonClass = cfg['targetPythonClass']

    if 'description' in cfg:
        template.description = cfg['description']

    if 'datasources' in cfg:
        for datasource_id, datasource_cfg in cfg['datasources'].items():
            add_datasource(template, datasource_id, datasource_cfg)

    if 'graphs' in cfg:
        for graph_id, graph_cfg in cfg['graphs'].items():
            add_graph(template, graph_id, graph_cfg)


def add_datasource(template, id_, cfg):
    if 'type' not in cfg:
        die('No type for %s/%s.', template.id, id_)

    datasource_types = dict(template.getDataSourceOptions())
    type_ = datasource_types.get(cfg['type'])
    if not type_:
        die('%s datasource type is not one of %s.',
            cfg['type'], ', '.join(datasource_types.keys()))

    datasource = template.manage_addRRDDataSource(id_, type_)

    # Map severity names to values.
    if 'severity' in cfg:
        cfg['severity'] = {
            'critical': 5,
            'error': 4,
            'warning': 3,
            'info': 2,
            'debug': 1,
            'clear': 0,
        }.get(cfg['severity'].lower(), cfg['severity'])

    # TODO: Detect property type and do conversion.

    # Apply cfg items directly to datasource attributes.
    for k, v in cfg.items():
        if k not in ('type', 'datapoints'):
            setattr(datasource, k, v)

    if 'datapoints' in cfg:
        for datapoint_id, datapoint_cfg in cfg['datapoints'].items():
            add_datapoint(datasource, datapoint_id, datapoint_cfg)


def add_datapoint(datasource, id_, cfg):
    datapoint = datasource.manage_addRRDDataPoint(id_)

    if isinstance(cfg, dict):
        for k, v in cfg.items():
            setattr(datapoint, k, v)

    # Handle cfg shortcuts like DERIVE_MIN_0 and GAUGE_MIN_0_MAX_100.
    elif isinstance(cfg, types.StringTypes):
        if 'DERIVE' in cfg.upper():
            datapoint.rrdtype = 'DERIVE'

        min_match = re.search(r'MIN_(\d+)', cfg, re.IGNORECASE)
        if min_match:
            datapoint.rrdmin = min_match.group(1)

        max_match = re.search(r'MAX_(\d+)', cfg, re.IGNORECASE)
        if max_match:
            datapoint.rrdmax = max_match.group(1)


def add_graph(template, id_, cfg):
    graph = template.manage_addGraphDefinition(id_)

    # Apply cfg items directly to graph attributes.
    for k, v in cfg.items():
        if k not in ('graphpoints'):
            setattr(graph, k, v)

    if 'graphpoints' in cfg:
        for graphpoint_id, graphpoint_cfg in cfg['graphpoints'].items():
            add_graphpoint(graph, graphpoint_id, graphpoint_cfg)


def add_graphpoint(graph, id_, cfg):
    graphpoint = graph.createGraphPoint(DataPointGraphPoint, id_)

    # Validate lineType.
    if 'lineType' in cfg:
        VALID_LINETYPES = ('DONTDRAW', 'LINE', 'AREA')

        if cfg['lineType'].upper() in VALID_LINETYPES:
            cfg['lineType'] = cfg['lineType'].upper()
        else:
            die('%s graphpoint lineType is not one of %s.',
                cfg['lineType'], ', '.join(VALID_LINETYPES))

    # Allow color to be specified by color_index instead of directly. This is
    # useful when you want to keep the normal progression of colors, but need
    # to add some DONTDRAW graphpoints for calculations.
    if 'colorindex' in cfg:
        try:
            colorindex = int(cfg['colorindex']) % len(GraphPoint.colors)
        except (TypeError, ValueError):
            die("graphpoint colorindex must be numeric.")

        cfg['color'] = GraphPoint.colors[colorindex].lstrip('#')

    # Apply cfg items directly to graphpoint attributes.
    for k, v in cfg.items():
        if k not in ('colorindex', 'graphpoints'):
            setattr(graphpoint, k, v)


if __name__ == '__main__':
    main()
