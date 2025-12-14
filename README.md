# pattern_to_string_list_for_algebraic_notation_chess_moves
Python script for creating a list of strings as resulting in combining blocks in string patterns, which will be applied for creating a super set of all chess algebraic notation moves


# UNDER CONSTRUCTION


## Motivation

The aim of this script, is to create all possible words for chess moves in algebraic notation.

I need that for tuning the dictionary of an OCR (pytesseract, in this case) adding those new words to the dictionary.

This will be used for helping to recognize better those "word" options when used in combination of my application ChessPdfBrowser.

The new function I am currently programming, is to create a library which will able to work with scanned Pdfs, offering similar functionality that when using pdfbox library for regular Pdfs

So the aim of this script, is to create a super set of all possible "words" in a chess game written in algebraic notation.

Those words, will be depending on the language, as the letters to dessignate chess figures might be different when using different languages

("KQRBN" for English, "RDTAC" for Spanish, ...)

So the OCR dictionaries of all supported languages, have to be tunned adding the chess moves.

I am planning to do that OCR dictionary tunning in the creation of a Docker image I am using in a server in the cloud.

That Docker will be exposing a rest api, which will accept a file with the image, and a language name to be used, and will return a json with the result of the OCR recogition.

Then, ChessPdfBrowser users (ChessPdfBrowser is a Java desktop application), will be able to use that resource, and experience a (hopefully) equivalent functionality when working with scanned Pdfs, than when using pdfbox library when working with not scanned ones.

Then, the aim of this repository, is to program a script for creating all possible "words" (or a super set of them) in a chess game written in algebraic notation for every of the supported languages.


## How the script works

The strategy will be creating a generic script, and then particularize it with configuration data for our purposes



### Processing in a nutshell

The script will take two kind of inputs:

- A file with the definitions of the patterns built of blocks, which might contain several options.

- One or more files with de list of the elements of every block. After combining all those files, all blocks used in the patterns must be defined for the script to work.

Then the idea is easy: creating all combinations of block elements of every configured pattern.

### Details

#### Format of patterns

The patterns will be made of literal strings, and blocks (${block_name}) or (${${block_name}xxx}, recursively)

Blocks can be made optional (block followed by "?"), which means that an empty string can be used as element value for combining that block

#### Format of block values

Blocks can be defined as a list of values.

Every of those values might be a literal string or, if marked with the parameter:  <value every_char="true">, then every char configured in that value will be taken as independent value for that block 


### Configuration examples

The script works taking two kind of parameters:

- pattern. A xml having a list of patterns to be applied.
  One or more patterns can be configured.
  Each pattern must follow a format.

  * Examples of patterns (applied to create a super set of all chess moves words in algebraic notation):
    <!-- normal figurine move -->
    <pattern>${figurine}${take}?${column}${row}${check_or_checkmate}?${nag}?</pattern>
    <!-- figurine move, including unambiguation (super set, some of them are illegal) -->
    <pattern>${figurine}${${column}?${row}?}?${take}?${column}${row}${check_or_checkmate}?${nag}?</pattern>
    <!-- pawn move (super set, some of them are illegal) -->
    <pattern>${${column}${take}}?${column}{row}{check_of_checkmate}?${nag}?</pattern>
    <!-- pawn promotion (super set, some of them are illegal) -->
    <pattern>${${column}${take}}?${column}${row_for_promotion}${promotion}?${figurine}${check_or_checkmate}?${nag}?</pattern>
    <!-- castling -->
    <pattern>${castle}${check_or_checkmate}?${nag}?</pattern>

- default_values, particular_values. Xmls having

  * default_values. The idea is having a xml with the default values (which are general and not particular of the language or the notation).

    * Examples:

      <!-- indicating whether is a taking move -->
      <block name="take">
        <value>x</vaue>
      </block>

      <block name="column">
        <value every_char="true">abcdefgh</value>
      </block>

      <block name="row">
        <value every_char="true">12345678</value>
      </block>

      <block name="check_or_checkmate">
        <value>+</value>
        <value>++</value>
        <value>#</value> <!-- checkmate -->
      </block>

      <block name="nag">
        <value>??</value>
        <value>?</value>
        <value>?!</value>
        <value>!?</value>
        <value>!</value>
        <value>!!</value>
      </block>

      <block name="promotion">
        <value>=</value>
      </block>

      <block name="row_for_promotion">
        <value every_char="true">18</value>
      </block>

      <block name="castle">
        <value>O-O</value>
        <value>O-O-O</value>
      </block>

    * particular_values. The idea is defining the not defined block value at default_values xml file, or defining other values which override the default_values.

      * Example-1: (for figurine algebraic notation)

        <block name="figurine">
          <value every_char="true">♔♕♖♗♘</value>
        </block>

      * Example-2: (for English algebraic notation)

        <block name="figurine">
          <value every_char="true">KQRBN</value>
        </block>

      * Example-2: (for Spanish algebraic notation)

        <block name="figurine">
          <value every_char="true">RDTAC</value>
        </block>

