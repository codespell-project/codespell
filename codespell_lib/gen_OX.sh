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
EXCEPT='^defenc'
(
   grep "\($PAT\)\|\($EXCEPT\)" "$1"
   for i in e es ed ing ation ations ; do
      for j in col fav ; do
         echo "${j}oriz$i->${j}ouriz$i"
         echo "${j}ouris$i->${j}ouriz$i"
      done
   done
   grep -v "$PAT" "$1" | sed 's/^\(.*\)->\(.*\)$/\2->\1/'
) | sort -d
