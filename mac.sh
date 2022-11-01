#!/bin/sh
# Author : Venkatesh Dharmapuri

if [ $1 == "chrome" ]
then
  rm -rf $HOME/Library/Caches/Google/Chrome/Default/*
  rm -rf $HOME/Library/Caches/Google/Chrome/PnaclTranslationCache/*
fi

if [ $1 == "firefox" ]
then
  FIREFOX=$( ls $HOME/Library/Application\ Support/Firefox/Profiles/ 2>/dev/null | grep .default )
  sqlite3 ${HOME}/Library/Application\ Support/Firefox/Profiles/${FIREFOX}/places.sqlite "delete from moz_historyvisits;"
  sqlite3 ${HOME}/Library/Application\ Support/Firefox/Profiles/${FIREFOX}/cookies.sqlite "delete from moz_cookies;"
  find ${HOME}/Library/Application\ Support/Firefox/Profiles/${FIREFOX}/storage/default -name "http*" -type d -exec rm -r "{}" \; -prune
  find ${HOME}/Library/Application\ Support/Firefox/Profiles/${FIREFOX}/cache2/entries -type f -delete 2>/dev/null
fi