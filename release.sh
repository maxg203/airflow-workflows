#!/bin/bash

set -e

# MUST run from a package root directory, and inside a Git repository.
# Bump PyPI package version and create a GitHub release.
# Then if created successfully, upload the new release to PyPI via twine.

version=$1
text=$2
branch=$(git rev-parse --abbrev-ref HEAD)
token=$(git config --global github.token)

repo_full_name=$(git config --get remote.origin.url)
url=$repo_full_name
re="^(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$"

if [[ $url =~ $re ]]; then
	protocol=${BASH_REMATCH[1]}
	separator=${BASH_REMATCH[2]}
	hostname=${BASH_REMATCH[3]}
	user=${BASH_REMATCH[4]}
	repo=${BASH_REMATCH[5]}
fi

# echo "Bump version..."
sed "s/version = '.*'/version = '$version'/g" setup.py > temp.py
rm setup.py
mv temp.py setup.py

# Commit and push version bump
git add setup.py
git commit -m "Bump version to $version"
git push origin master


generate_post_data()
{
  cat <<EOF
{
  "tag_name": "$version",
  "target_commitish": "$branch",
  "name": "$version",
  "body": "$text",
  "draft": true,
  "prerelease": false
}
EOF
}


echo "Create release $version for repo: $repo_full_name branch: $branch"
curl --data "$(generate_post_data)" "https://api.github.com/repos/$user/$repo/releases?access_token=$token"

pip3 install twine
python3 setup.py sdist
twine upload dist/*
