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

(
   grep "$PAT" "$1"
   for i in e es ed ing ation ations ; do
      echo "coloriz$i->colouriz$i"
      echo "colouris$i->colouriz$i"
   done
   grep -v "$PAT" "$1" | sed 's/^\(.*\)->\(.*\)$/\2->\1/'
) | sort -d
