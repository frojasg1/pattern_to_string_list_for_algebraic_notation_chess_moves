#!/bin/bash

SCRIPT_DIR="$( dirname "$0" )"

"$SCRIPT_DIR"/../src/paint_all_combinations.py \
    -patterns_xml "$SCRIPT_DIR"/conf/patterns.xml \
    -block_values_xmls \
        "$SCRIPT_DIR"/conf/default_values.xml
