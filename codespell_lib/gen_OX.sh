#!/bin/bash

SUFFIXES=(
   "ize"
   "izes"
   "ized"
   "izing"
   "izement"
   "ization"
   "izations"
)
SUFF=${SUFFIXES[*]}
PAT='\(\('"${SUFF// /\\)\\|\\(}"'\)\)$'

EXCEPTIONS=(
   'defenc'
   'storey'
)
EXCEPT='^\(\('"${EXCEPTIONS// /\\)\\|\\(}"'\)\)'

(
   grep -e "$PAT" -e "$EXCEPT" "$1" | grep -v '^\(colouris\)\|\(favouris\)'
   for i in e es ed ing ation ations ; do
      echo "colouris$i->colouriz$i"
      echo "coloriz$i->colouriz$i"
   done
   for i in e es ed ing ; do
      echo "favouris$i->favouriz$i"
      echo "favoriz$i->favouriz$i"
   done
   grep -v -e "$PAT" -e "$EXCEPT" "$1" | sed 's/^\(.*\)->\(.*\)$/\2->\1/'
) | sort -d
