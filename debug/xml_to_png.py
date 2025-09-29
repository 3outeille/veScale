#!/usr/bin/env python3
"""
A prettier version of xml_to_png.py that creates more visually appealing NCCL topology graphs.

Usage:
    python3 xml_to_png.py -i input_xml_file -o output_file_name
"""

import xml.etree.ElementTree as ET
from graphviz import Digraph
import os
import sys
import getopt

# Modern, visually pleasing color palette
colors = {
    'graphs': '#F8F9FA',     # Light gray background
    'graph': '#E3F2FD',      # Soft blue
    'channel': '#E0F2F1',    # Soft teal
    'gpu': '#E8F5E9',        # Soft green
    'cpu': '#F3E5F5',        # Soft purple
    'pci': '#FFEBEE',        # Soft red
    'nvlink': '#FFF3E0',     # Soft orange
    'net': '#FFE0B2',        # Soft coral
    'nic': '#FFE0B2'         # Soft coral
}

def format_attributes(attrs):
    """Format attributes into HTML-like table rows."""
    if not attrs:
        return ""
    
    rows = []
    for k, v in attrs.items():
        # Skip long attribute values
        if len(str(v)) > 30:
            v = str(v)[:27] + "..."
        rows.append(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{k}</FONT></TD>'
                   f'<TD ALIGN="LEFT"><FONT POINT-SIZE="10">{v}</FONT></TD></TR>')
    return "".join(rows)

def build_topology(graph, parent_element, parent_node=None, rank=0):
    """Build the topology with improved visual hierarchy."""
    dev = parent_element.tag
    
    # Get the identifying attribute for this device type
    attr_map = {
        'cpu': 'numaid',
        'pci': 'busid',
        'gpu': 'dev',
        'nvlink': 'target',
        'net': 'name',
        'nic': 'name',
        'graph': 'id'
    }
    
    # Get device identifier
    attr_name = attr_map.get(dev)
    res = None
    if attr_name:
        res = parent_element.get(attr_name)
        if res:
            res = res.replace(':', '_')
    
    # Create unique node name
    node_name = f"{dev}_{res}" if res else dev
    
    # Create HTML-like label
    title = dev.upper() if dev in ('gpu', 'cpu') else dev.capitalize()
    if res:
        title = f"{title} {res}"
    
    # Format attributes as a table
    attrs_html = format_attributes(parent_element.attrib)
    if attrs_html:
        label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="{colors.get(dev, 'white')}"><B>{title}</B></TD></TR>
            {attrs_html}
            </TABLE>>'''
    else:
        label = f'<<B>{title}</B>>'
    
    # Add node with styling
    graph.node(node_name,
              label=label,
              shape='box',
              style='rounded,filled',
              fillcolor=colors.get(dev, 'white'),
              penwidth='1.5')
    
    # Add edge from parent if exists
    if parent_node is not None:
        graph.edge(parent_node, node_name,
                  penwidth='1.5',
                  color='#666666',
                  arrowsize='0.7')
    
    # Process children
    for child_element in parent_element:
        build_topology(graph, child_element, node_name, rank + 1)

def main(input_file, output_file):
    print(f'Creating prettier visualization from {input_file}')
    
    # Parse XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Create directed graph
    graph = Digraph(comment='NCCL Topology Visualization')
    
    # Set global graph attributes
    graph.attr(rankdir='TB',           # Top to bottom layout
              splines='ortho',         # Orthogonal lines
              nodesep='0.5',           # Node separation
              ranksep='0.7',           # Rank separation
              concentrate='true',       # Merge edges
              bgcolor='white',         # Background color
              fontname='Helvetica')    # Default font
    
    # Set default node attributes
    graph.attr('node',
              shape='box',
              style='rounded,filled',
              fontname='Helvetica',
              margin='0.2')
    
    # Set default edge attributes
    graph.attr('edge',
              fontname='Helvetica',
              color='#666666')
    
    # Build the topology
    build_topology(graph, root)
    
    # Render the graph
    graph.render(output_file, format='png', cleanup=True)
    print(f'Created visualization at: {output_file}.png')

def usage():
    print('Usage: python3 xml_to_png_pretty.py -i input_file_name -o output_file_name')

if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
        sys.exit(1)
        
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
        input_file = None
        output_file = None
        
        for opt, arg in opts:
            if opt == '-h':
                usage()
                sys.exit()
            elif opt == '-i':
                input_file = arg
            elif opt == '-o':
                output_file = arg
        
        if input_file and output_file:
            main(input_file, output_file)
        else:
            usage()
            sys.exit(1)
            
    except getopt.GetoptError:
        usage()
        sys.exit(1)
