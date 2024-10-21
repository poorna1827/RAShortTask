#!/bin/bash

clear

for ticker in $(cat /Users/liam/PycharmProjects/WeiredTrading/data/ticker_data/ticker_list_v1.txt);
do
  results=$(python data_util/ib-data-download/download_mins_bars.py --base-directory "/Users/liam/PycharmProjects/WeiredTrading/data" --start-date 20220101 --size '30 mins' $ticker);
  echo results;
done

for ticker in $(cat /Users/liam/PycharmProjects/WeiredTrading/data/ticker_data/ticker_list_v1.txt);
do
  results=$(python data_util/ib-data-download/download_daily_bars.py --base-directory "/Users/liam/PycharmProjects/WeiredTrading/data" --max-days --size '1 day' $ticker);
  echo results;
done