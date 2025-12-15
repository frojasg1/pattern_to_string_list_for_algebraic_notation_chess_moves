#!/usr/bin/python3

import sys

import argparse

import xml.etree.cElementTree as ET


def create_argsparse(program_name: str) -> argparse.ArgumentParser:
    result: argparse.ArgumentParser = argparse.ArgumentParser(prog=program_name)
    result.add_argument('-block_values', nargs='+', required=True, type=str, help='block_values, with format: "block_name:string_with_char_values"')

    return result


def parse_block_value_pair(block_value_pair: str) -> tuple:
    my_pos = block_value_pair.find(":")

    block_name = None
    block_value = None

    if my_pos > -1:
        block_name = block_value_pair[:my_pos]
        block_value = block_value_pair[my_pos + 1:]
    
    return block_name, block_value

def main():
    sys.stdout.reconfigure(encoding='utf8')

    program_name = sys.argv[0]
    my_args = create_argsparse(program_name).parse_known_args(sys.argv)[0]


    root = ET.Element("config")

    block_value_pairs = my_args.block_values

    for block_value_pair in block_value_pairs:
        block_name, block_values = parse_block_value_pair(block_value_pair)

        if block_name is None:
            raise RuntimeError("Cannot parse block_values for: '{block_value_pair}', expecting to be in this format: 'block_name:string_with_char_values'")

        block_node = ET.SubElement(root, "block", name=block_name)

        ET.SubElement(block_node, "value", every_char="True").text = block_values

    # https://stackoverflow.com/questions/3605680/creating-a-simple-xml-file-using-python
#    tree = ET.ElementTree(root)
#    tree.write("filename.xml", encoding='utf8')
    # https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file
#    ET.indent(tree, space="    ", level=0)
    # https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
    ET.indent(root)

    # https://stackoverflow.com/questions/15304229/convert-python-elementtree-to-string
    xmlbytes = ET.tostring(root, encoding='utf8')

    # http://stackoverflow.com/questions/606191/convert-bytes-to-a-string-in-python-3
    xmlstr = xmlbytes.decode('utf8')
 
    print(xmlstr)

if __name__ == "__main__":
    main()
