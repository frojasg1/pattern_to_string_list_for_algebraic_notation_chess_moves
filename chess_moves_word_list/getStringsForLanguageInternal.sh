#!/bin/bash

if (( $# != 1 ))
then
    echo "Usage: $0 \"figurine_letters_xml_filename\""
    echo "Example: $0 \"conf/figurine_letters_spanish_example.xml\""
    exit 1
fi

FIGURINE_LETTERS_XML_FILENAME="$1"

SCRIPT_DIR="$( dirname "$0" )"

"$SCRIPT_DIR"/../src/paint_all_combinations.py \
    -patterns_xml "$SCRIPT_DIR"/conf/patterns.xml \
    -block_values_xmls \
        "$SCRIPT_DIR"/conf/default_values.xml \
        "$FIGURINE_LETTERS_XML_FILENAME"
