#!/bin/bash

################################################################################
# Script that takes a list of repository names, does a dump (git clone --bare),
# and then dumps the merge commits to a file.
################################################################################

if [ -z $1 ]; then
  echo "Usage: dump_and_find.sh <file_of_repos>"
  exit
fi

scm="https://${USER}@stash.lsstcorp.org/scm/sim"

repo_file=${1}
repos=$(cat ${repo_file})
for repo in $repos
do
  echo "Dumping ${repo}"
  git clone --bare ${scm}/${repo}.git
  cd ${repo}.git
  echo "Finding merge commits"
  git log --merges --format="%H %an %s" > ${repo}.log
  mv ${repo}.log ../
  cd ../
done
