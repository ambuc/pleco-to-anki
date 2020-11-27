#!/bin/bash

binary_path=$(rlocation "__main__/p2a")

expected=$(cat $(rlocation "__main__/testdata/output.csv"))

actual=$($binary_path --path=$(rlocation "__main__/testdata/input.xml"))

if [[ $expected -ne $actual ]]; then
  echo >&2 "ERROR: expected not actual"
  echo $actual
  echo $expected
  exit 1
fi
