#!/bin/bash

clear

for f in $(./backtrader/backtrader/tests/*.py);
do
  results=$(python "$f");
  echo results;
done