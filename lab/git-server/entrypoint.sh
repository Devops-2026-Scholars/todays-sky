#!/bin/sh
set -eu

mkdir -p /repos /run /tmp

if ! git config --system --get-all safe.directory 2>/dev/null | grep -qx '\*'; then
  git config --system --add safe.directory '*'
fi
git config --system http.receivepack true

if [ ! -d /repos/weather.git ]; then
  git init --bare --initial-branch=main /repos/weather.git
fi

git config --file /repos/weather.git/config http.receivepack true
git config --file /repos/weather.git/config http.uploadpack true
git --git-dir=/repos/weather.git symbolic-ref HEAD refs/heads/main

chown -R nginx:nginx /repos
spawn-fcgi -s /run/fcgiwrap.sock -F 2 -u nginx -g nginx -M 766 -- /usr/bin/fcgiwrap
exec nginx -g "daemon off;"
