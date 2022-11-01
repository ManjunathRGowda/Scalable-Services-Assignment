#!/bin/sh
# Author : Venkatesh Dharmapuri

if [ $1 == "chrome" ]
then
  rm -rf $HOME/.config/google-chrome/Default/*
  rm -rf $HOME/.cache/google-chrome/Default/*
fi

if [ $1 == "firefox" ]
then
  FIREFOX=$( ls $HOME/.mozilla/firefox 2>/dev/null | grep .default )
  sqlite3 ${HOME}/.mozilla/firefox/${FIREFOX}/places.sqlite "delete from moz_historyvisits;"
  sqlite3 ${HOME}/.mozilla/firefox/${FIREFOX}/cookies.sqlite "delete from moz_cookies;"
  find ${HOME}/.mozilla/firefox/${FIREFOX}/storage/default -name "http*" -type d -exec rm -r "{}" \; -prune
  find ${HOME}/.mozilla/firefox/${FIREFOX}/cache2/entries -type f -delete 2>/dev/null
fi