#!/bin/bash


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
SUFF=${SUFFIXES[*]}
PAT1='\(\('"${SUFF// /\\)\\|\\(}"'\)\)$'

# choose US for these ones
EXCEPTIONS=(
   'defenc'
)
EXCEPT=${EXCEPTIONS[*]}
PAT2='^\(\('"${EXCEPT// /\\)\\|\\(}"'\)\)'

# these one should be left out
IGNORE=(
   'storey'
   'practise'
)
IGN=${IGNORE[*]}
PAT3='^\(\('"${IGN// /\\)\\|\\(}"'\)\)'

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
) | sort
