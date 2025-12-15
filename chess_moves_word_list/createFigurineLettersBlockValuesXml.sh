#!/bin/bash

function errLog()
{
    echo "$@" >&2
}

function get_figurine_for_disambiguation_letters()
{
    python3 <<PYTHON
figurine_letters = "$1"
if len(figurine_letters) != 5:
    raise RuntimeError(f'The string: "{figurine_letters}" was not a list of figurine letters. Size different from 5')
rook_letter = figurine_letters[2]
knight_letter = figurine_letters[4]

print(f'{rook_letter}{knight_letter}')
PYTHON

    return $?
}

if (( $# != 1 ))
then
    echo "Usage: $0 \"figurine_letters\""
    echo "Example: $0 \"KQRBN\""
    exit 1
fi

FIGURINE_LETTERS="$1"
FIGURINE_LETTERS_FOR_DISAMBIGUATION=$( get_figurine_for_disambiguation_letters $FIGURINE_LETTERS )
if (( $? != 0 ))
then
    errLog "An error has been produced when getting figurine letters for disambiguation"
    exit 2
fi

SCRIPT_DIR="$( dirname "$0" )"


../src/block_values_xml_config_creator.py \
    -block_values \
        "figurine:$FIGURINE_LETTERS" \
        "figurine_for_disambiguation:$FIGURINE_LETTERS_FOR_DISAMBIGUATION"
