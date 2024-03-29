import urllib.request
import json

# Install dependecies:
#
# $ pip install PyYAML
#
# Run:
# 
# python3 scripts/assert_ethereum_latest_release.py

ETHEREUM_SPEC_COMMIT_PREFIX = "ETHEREUM_SPEC_COMMIT: "
CONSENSUS_SPEC_FILEPATH = "beacon_chain.md"

REMOTE_BASE_URL = 'https://api.github.com/repos/ethereum/consensus-specs/releases'

def read_default_commit_from_md(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(ETHEREUM_SPEC_COMMIT_PREFIX):
                return line[len(ETHEREUM_SPEC_COMMIT_PREFIX):].strip()

default_commit = read_default_commit_from_md(CONSENSUS_SPEC_FILEPATH)
print("default_commit", default_commit)

def get_latest_release_tag(include_pre_releases=True):
    """Fetch the latest release tag from the GitHub API, considering pre-releases if specified."""
    request = urllib.request.Request(REMOTE_BASE_URL)
    request.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())
        # If pre-releases are considered, sort them to find the latest.
        # Assumes the API returns releases in descending order, which is true for '/releases' but not for '/releases/latest'.
        if include_pre_releases:
            releases = sorted(data, key=lambda x: x['published_at'], reverse=True)
            return releases[0]['tag_name'] if releases else None
        else:
            return data['tag_name'] if 'tag_name' in data else None

# Fetch the latest release tag from GitHub, considering pre-releases
latest_tag = get_latest_release_tag(include_pre_releases=True)
print("Latest Release Tag (including pre-releases):", latest_tag)

# Assert the latest tag matches the expected commit/tag
if default_commit == latest_tag:
    print("Assertion succeeded: The latest release tag matches the expected value.")
else:
    raise Exception(f"Latest release {latest_tag} does not match local: {default_commit}")
