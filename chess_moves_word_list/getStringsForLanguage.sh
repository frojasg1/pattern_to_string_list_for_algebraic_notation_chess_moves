#!/bin/bash

if (( $# != 1 ))
then
    echo "Usage: $0 \"figurine_letters\""
    echo "Example: $0 \"KQRBN\""
    exit 1
fi

FIGURINE_LETTERS="$1"

SCRIPT_DIR="$( dirname "$0" )"

cd "$SCRIPT_DIR"
./getStringsForLanguageInternal.sh <(./createFigurineLettersBlockValuesXml.sh "$FIGURINE_LETTERS")
