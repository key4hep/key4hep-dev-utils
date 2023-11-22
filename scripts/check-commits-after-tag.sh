# This script checks the commits after the last tag in all the repositories and
# prints the commit messages for those commits

# It can be used before making a release to make sure all the commits in the
# repositories belong in a tag

# list of repos to exclude
exclude_key4hep=("key4hep-doc" "key4hep-dev-utils" "key4hep-spack" "key4hep-tutorials" "key4hep-images" "documents" "k4LCIOReader" "key4hep-actions" "dmx" "key4hep-reco-validation" "Gaudi" "spack" "key4DCMTSim" "key4hep-validation" "FCCDetectors" "DD4hep" "key4hep-web")
exclude_aidasoft=("management" "aidasoft.github.io")
exclude_hepfcc=("spack" "jenkins-pipelines" "fcc-spi" "glossary" "WebTools" "fcc-tutorials" "hep-fcc.github.io" "fcc-spack")
exclude_cepc=("docker-cvmfs")
exclude=()
for name in "${exclude_key4hep[@]}"; do
    exclude+=("key4hep/$name")
done
for name in "${exclude_aidasoft[@]}"; do
    exclude+=("AIDASoft/$name")
done
for name in "${exclude_hepfcc[@]}"; do
    exclude+=("HEP-FCC/$name")
done
for name in "${exclude_cepc[@]}"; do
    exclude+=("CEPC/$name")
done
repositories=()
for org in key4hep iLCSoft AIDASoft HEP-FCC CEPC; do
    repositories+=($(gh repo list "$org" --json=nameWithOwner --jq='.[] | .nameWithOwner'))
done

for repo in "${repositories[@]}"; do
    for ex in "${exclude[@]}"; do
        if [ "$repo" == "$ex" ]; then
            continue 2
        fi
    done
    # Get the last tag in the repository
    last_tag=$(gh api repos/"$repo"/releases/latest --jq '.tag_name' 2>/dev/null | tr -d '"')
    if echo "$last_tag" | grep -q "Not Found"; then
        echo "No tag found in $repo"
        echo "-------------------------------------------------------------"
        continue
    fi
    sha=$(gh api repos/$repo/git/ref/tags/$last_tag --jq '.object.sha' | tr -d '"')
    date=$(gh api repos/$repo/commits/$sha --jq '.commit.author.date' | tr -d '"' )


    text=$(gh api "repos/$repo/commits" --jq '.[] | select(.commit.author.date > "'"$date"'" ) | (.sha[0:7] + " " + (.commit.message | split("\n")[0]))')
    if [ -n "$text" ]; then
        echo "Commits in $repo after the tag $last_tag:"
        echo "$text"
        unset text

        echo "-------------------------------------------------------------"
    fi
done
