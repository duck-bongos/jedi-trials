#!/bin/bash

while getopts ":p:" opt; do
  case $opt in
    p)
      path=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [[ -z "$path" ]]; then
  echo "Path not specified." >&2
  exit 1
fi

if [[ ! -d "$path" ]]; then
  echo "Invalid path." >&2
  exit 1
fi

find "$path" -maxdepth 1 -mindepth 1 -type d | while read -r dir; do
  dir="../${dir:4}"
  echo "Processing $dir"
  # Do whatever you want to do with each directory here
done
