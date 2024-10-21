#!/bin/bash

clear

mkdir ~/WT/data/STK_yf

for ticker in $(cat ~/WT/data/ticker_data/ticker_list_v1.txt);
do
  results=$(python ~/WT/Weird-Trading/backtrader/backtrader/samples/yahoo-test/yahoo-download-test.py --data $ticker);
  echo $ticker;
done