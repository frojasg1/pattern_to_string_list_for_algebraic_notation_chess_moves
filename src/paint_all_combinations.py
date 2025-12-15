#!/usr/bin/python3

import sys
import argparse

import xml.etree.cElementTree as ET


def create_argsparse(program_name: str) -> argparse.ArgumentParser:
    result: argparse.ArgumentParser = argparse.ArgumentParser(prog=program_name)
    result.add_argument('-patterns_xml', nargs='?', required=True, type=str, help='patterns_xml: one file with pattern configurations')
    result.add_argument('-block_values_xmls', nargs='+', required=True, type=str, help='block_values_xmls: one or more files with the configuration of block values')

    return result


class MyIterator(object):

    def __init__(self, is_optional: bool):
        self._is_optional_: bool = is_optional
        self._optional_applies_now_: bool = is_optional
        self._current_: str = None

    def _has_next_internal_(self) -> bool:
        pass

    def has_next(self) -> bool:
        result = None
        if self._optional_applies_now_:
            result = True
        else:
            result = self._has_next_internal_()

        return result

    def _next_internal_(self) -> str:
        pass

    def next(self) -> str:
        if not self.has_next():
            raise RuntimeError("Error, asked for next, when iterator did not have any next value")

        result = None
        if self._optional_applies_now_:
            result = ""
            self._optional_applies_now_ = False
        else:
            result = self._next_internal_()

        self._current_ = result

        return result

    def _reset_internal_(self):
        pass

    def reset(self):
        self._optional_applies_now_ = self._is_optional_
        self._current_ = None
        self._reset_internal_()

    def get_current(self) -> str:
        result = self._current_
        if result is None:
            result = self.next()
            self._current_ = result
        
        return result

class MyCompoundIterator(MyIterator):

    def __init__(self, my_iterators: list, is_optional: bool=False):
        super().__init__(is_optional)
        self._my_iterators_: list = my_iterators
    
    def _has_next_internal_(self) -> bool:
        result = False

        if len(self._my_iterators_) > 0:
            for my_iterator in self._my_iterators_:
                result = my_iterator.has_next()
                if result:
                    break

        return result

    def _next_internal_(self) -> str:
        result_list = []
        my_iterator_iter = iter(self._my_iterators_)
        my_iterator: MyIterator = next(my_iterator_iter, None)
        next_done = False
        while my_iterator is not None:
            if not next_done:
                if my_iterator.has_next():
                    result_list.append(my_iterator.next())
                    next_done = True
                else:
                    my_iterator.reset()
                    result_list.append(my_iterator.get_current())
            else:
                result_list.append(my_iterator.get_current())
            
            my_iterator = next(my_iterator_iter, None)

        return "".join(result_list)
    
    def _reset_internal_(self):
        for my_iterator in self._my_iterators_:
            my_iterator.reset()


class MySimpleBlockIterator(MyIterator):

    def __init__(self, my_values: list, is_optional: bool=False):
        super().__init__(is_optional)

        self._my_values_: list = my_values
        self._my_index_: int = 0

    def _has_next_internal_(self) -> bool:
        return self._my_index_ < len(self._my_values_)

    def _next_internal_(self) -> str:
        result = self._my_values_[self._my_index_]
        self._my_index_ += 1

        return result

    def _reset_internal_(self):
        self._my_index_ = 0


def parse_xml_and_get_root_node(xml_filename: str):
    try:
        tree = ET.parse(xml_filename, ET.XMLParser(encoding='utf8'))
        root = tree.getroot()
    except:
        raise RuntimeError(f'Error when parsing "{xml_filename}"')

    return root


def parse_block_values_xml(xml_filename: str) -> dict:
    result: dict = {}
    
    root = parse_xml_and_get_root_node(xml_filename)

    if root.tag != 'config':
        raise RuntimeError(f'Expected root tag: <config> but found: <{root.tag}> in file: {xml_filename}')

    for block_node in root.findall('block'):
        block_name: str = block_node.get('name')
        if block_name is None:
            raise RuntimeError(f'Not found param "name" in <block> at file: {xml_filename}')

        values_list: list = []
        for value_node in block_node.findall('value'):
            if value_node.get("every_char", "False") == "True":
                for my_char in value_node.text:
                    values_list.append(my_char)
            else:
                values_list.append(value_node.text)

        result[block_name] = values_list

    return result


def parse_block_values_xmls(block_values_xml_names: list) -> dict:
    result: dict = {}

    for xml_filename in block_values_xml_names:
        tmp_result : dict = parse_block_values_xml(xml_filename)

        for block_name, values_list in tmp_result.items():
            result[block_name] = values_list

    return result


def get_matching_closing_brace_pos(pattern_str: str, my_pos: int, braces_to_close: int) -> int:
    if braces_to_close <= 0:
        raise RuntimeError(f'braces_to_close should be greater than or equal to zero, but was: {braces_to_close}')

    result = None
    for ind, my_char in enumerate(pattern_str[my_pos:]):
        if my_char == "{":
            braces_to_close += 1
        elif my_char == "}":
            braces_to_close -= 1
        
        if braces_to_close == 0:
            result = my_pos + ind
            break

    return result


# for parsing block elements  "${xxxxxxxxxxx}?", or literals
def get_next_sub_pattern_start(pattern_str: str, my_pos: int) -> int:
    result: int = my_pos

    next_block_pos = pattern_str.find("{", my_pos)
    if next_block_pos != -1 and (next_block_pos < my_pos + 1 or pattern_str[next_block_pos - 1] != "$"):
        raise RuntimeError('Opening brace "{" was not the start of a block. "$" expected before.' + f'at pattern "{pattern_str}", at pos: {next_block_pos}')
    next_block_pos -= 1   # at the dollar part

    pattern_str_len = len(pattern_str)
    if next_block_pos == my_pos: # just starting a block
        matching_closing_brace_pos = get_matching_closing_brace_pos(pattern_str, my_pos + 2, 1)

        if matching_closing_brace_pos is None:
            raise RuntimeError(f'Closing block brace not found at pattern_str: "{pattern_str}", starting at pos: {my_pos}')
        
        result = matching_closing_brace_pos

        if result + 1 < pattern_str_len and pattern_str[result + 1] == "?":
            result += 1

        result += 1 # pointing to the next element
    else:
        if next_block_pos < 0:
            result = pattern_str_len
        else:
            result = next_block_pos

    return result


def split_into_sub_patterns(pattern_str: str) -> list:
    result: list = []

    my_pos: int = 0
    while my_pos < len(pattern_str):
        next_sub_pattern_start: int = get_next_sub_pattern_start(pattern_str, my_pos)

        sub_pattern_str: str = pattern_str[my_pos:next_sub_pattern_start]
        result.append(sub_pattern_str)

        my_pos = next_sub_pattern_start
    
    return result


def parse_single_pattern(single_pattern_str: str, my_blocks_values_dict: dict, parse_pattern_func) -> MyIterator:
    result: MyIterator = None

    is_optional = False
    single_pattern_str_len = len(single_pattern_str)
    if single_pattern_str.startswith("${"): # is a block
        end_pos = -1
        if single_pattern_str.endswith("?"):
            is_optional = True
            end_pos = -2

        str_inside_block = single_pattern_str[2:end_pos]

        # 3 < single_pattern_str_len is granted for the previous processing
        if single_pattern_str.find("{", 2) != -1: # compound block

            compound_pattern_str = str_inside_block
            result = parse_pattern_func(is_optional, compound_pattern_str, my_blocks_values_dict)
        else:
            block_name = str_inside_block
            my_block_values = my_blocks_values_dict.get(block_name, None)

            if my_block_values is None:
                raise RuntimeError(f'Values not found for block_name: "{block_name}"')

            result = MySimpleBlockIterator(my_block_values, is_optional)

    else: # is a literal
        literal = single_pattern_str
        result = MySimpleBlockIterator([literal], is_optional)
    
    return result


def parse_pattern(is_optional: bool, pattern_str: str, my_blocks_values_dict: dict) -> MyIterator:
    result: MyIterator = None

    sub_patterns_str_list: list = split_into_sub_patterns(pattern_str)

    if len(sub_patterns_str_list) == 1:
        my_iterator = parse_single_pattern(sub_patterns_str_list[0], my_blocks_values_dict, parse_pattern)
        my_sub_patterns_list = [my_iterator]
    else:
        child_is_optional = False
        my_sub_patterns_list = [parse_pattern(child_is_optional, sub_pattern_str, my_blocks_values_dict) for sub_pattern_str in sub_patterns_str_list]

    result = MyCompoundIterator(my_sub_patterns_list, is_optional=is_optional)
    
    return result


def parse_patterns(xml_filename: str, my_blocks_values_dict: dict) -> list:
    result: list = []

    root = parse_xml_and_get_root_node(xml_filename)

    if root.tag != 'config':
        raise RuntimeError(f'Expected root tag: <config> but found: <{root.tag}> in file: {xml_filename}')

    for pattern_node in root.findall('pattern'):
        try:
            is_optional = False
            my_iterator: MyIterator = parse_pattern(is_optional, pattern_node.text, my_blocks_values_dict)
        except Exception as ex:
            raise RuntimeError(f'An exception has been produced when parsing pattern: "{pattern_node.text}" at xml file: "{xml_filename}"')

        result.append(my_iterator)

    return result


def main(args: list):
    sys.stdout.reconfigure(encoding='utf8')

    program_name = sys.argv[0]
    my_args = create_argsparse(program_name).parse_known_args(args)[0]

    my_blocks_values_dict: dict = parse_block_values_xmls(my_args.block_values_xmls)

    my_pattern_iterators: list = parse_patterns(my_args.patterns_xml, my_blocks_values_dict)

    my_pattern_iterator : MyIterator = None
    for my_pattern_iterator in my_pattern_iterators:
        while my_pattern_iterator.has_next():
            print(my_pattern_iterator.next())


if __name__ == "__main__":
    args = sys.argv
#    args = [
#        "-patterns_xml", r"J:\N\java\Aplicaciones\_new.github\20251214.chess_moves_word_list\chess_moves_word_list\conf\patterns.xml",
#        "-block_values_xmls", r"J:\N\java\Aplicaciones\_new.github\20251214.chess_moves_word_list\chess_moves_word_list\conf\default_values.xml",
#            r"J:\N\java\Aplicaciones\_new.github\20251214.chess_moves_word_list\chess_moves_word_list\conf\figurine_letters_spanish_example.xml"
#    ]
    args = [
        "-patterns_xml", r"J:\N\java\Aplicaciones\_new.github\20251214.chess_moves_word_list\test1\conf\patterns.xml",
        "-block_values_xmls", r"J:\N\java\Aplicaciones\_new.github\20251214.chess_moves_word_list\test1\conf\default_values.xml"
    ]
    main(args)

