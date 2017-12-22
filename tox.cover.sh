#!/bin/sh -xe

# USAGE: ./tox.cover.sh [package]
#
# This script is used by tox.ini (and thus Travis CI) in order to
# generate separate stats for each package. It should be removed once
# those packages are moved to separate repo.
#
# -e makes sure we fail fast and don't submit coveralls submit

if [ "xxx$1" = "xxx" ]; then
  pkgs="certbot acme certbot_apache"
else
  pkgs="$@"
fi

cover () {
  if [ "$1" = "certbot" ]; then
    min=98
  elif [ "$1" = "acme" ]; then
    min=100
  else
    echo "Unrecognized package: $1"
    exit 1
  fi

  pkg_dir=$(echo "$1" | tr _ -)
  pytest --cov "$pkg_dir" --cov-append --cov-report= --numprocesses auto --pyargs "$1"
  coverage report --fail-under="$min" --include="$pkg_dir/*" --show-missing
}

rm -f .coverage  # --cov-append is on, make sure stats are correct
for pkg in $pkgs
do
  cover $pkg
done
