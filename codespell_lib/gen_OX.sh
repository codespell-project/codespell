#!/bin/bash

one_of() {
   LIST="$*"
   echo '\(\('"${LIST// /\\)\\|\\(}"'\)\)'
}

SUFFIXES=(
   "ize"
   "izes"
   "izer"
   "izable"
   "ized"
   "izing"
   "izement"
   "ization"
   "izations"
)
PAT1="$(one_of "${SUFFIXES[@]}")$"

# choose US for these ones
EXCEPTIONS=(
   'defenc'
   'focuss'
)
PAT2="^$(one_of "${EXCEPTIONS[@]}")"

# these one should be left out
IGNORE=(
   'storey'
   'practise'
   'programme'
   'licence'
)
PAT3="^$(one_of "${IGNORE[@]}")"

(
   grep -e "$PAT1" -e "$PAT2" "$1" | grep -v "$PAT3" | grep -v '^\(colouris\)\|\(favouris\)'
   for i in e es ed ing ation ations er able; do
      echo "colouris$i->colouriz$i"
      echo "coloriz$i->colouriz$i"
   done
   for i in e es ed ing able; do
      echo "favouris$i->favouriz$i"
      echo "favoriz$i->favouriz$i"
   done
   grep -v -e "$PAT1" -e "$PAT2" "$1" | grep -v "$PAT3" | sed 's/^\(.*\)->\(.*\)$/\2->\1/'
) | sort -f -t- -k 1b,1
