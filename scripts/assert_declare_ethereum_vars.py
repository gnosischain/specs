import urllib.request
import yaml
import sys
import argparse
import difflib
import re
import json

# Install dependecies:
#
# $ pip install PyYAML
#
# Run:
# 
# python3 scripts/assert_declare_ethereum_vars.py

# URL of the YAML file in the GitHub repo
# 'https://raw.githubusercontent.com/ethereum/consensus-specs/dev/configs/mainnet.yaml'
REMOTE_BASE_URL = 'https://raw.githubusercontent.com/ethereum/consensus-specs'

# Path to the local YAML file
FILES = [
     # local file                    # remote url path
    ('consensus/config/gnosis.yaml', 'configs/mainnet.yaml'),
    ('consensus/preset/gnosis/phase0.yaml', 'presets/mainnet/phase0.yaml'),
    ('consensus/preset/gnosis/altair.yaml', 'presets/mainnet/altair.yaml'),
    ('consensus/preset/gnosis/bellatrix.yaml', 'presets/mainnet/bellatrix.yaml'),
    ('consensus/preset/gnosis/capella.yaml', 'presets/mainnet/capella.yaml'),
    ('consensus/preset/gnosis/deneb.yaml', 'presets/mainnet/deneb.yaml'),
]

ETHEREUM_SPEC_COMMIT_PREFIX = "ETHEREUM_SPEC_COMMIT: "
CONSENSUS_SPEC_FILEPATH = "consensus.md"

# Keys to ignore for the config / preset diff tables
IGNORE_FOR_DIFF_CONFIG_KEYS = [
    # Genesis information is not relevant to display as diff
    'MIN_GENESIS_TIME',
    'MIN_GENESIS_ACTIVE_VALIDATOR_COUNT',
    'GENESIS_DELAY',
    # Config name will be different
    'CONFIG_NAME',
    'PRESET_BASE',
    # Deposit bridge data differs between all networks, not relevant in diff
    'DEPOSIT_CONTRACT_ADDRESS',
    'DEPOSIT_CHAIN_ID',
    'DEPOSIT_NETWORK_ID',
    # Fork scheduling differs between all networks, not relevant in diff
    'TERMINAL_TOTAL_DIFFICULTY',
    '_FORK_EPOCH',
    '_FORK_VERSION',
]
IGNORE_FROM_REMOTE_CONFIG_KEYS = [
    # Ignore pre-release
    'WHISK_EPOCHS_PER_SHUFFLING_PHASE',
    'WHISK_PROPOSER_SELECTION_GAP',
    'EIP6110_FORK_',
    'EIP7002_FORK_',
    'WHISK_FORK_'
]

def read_default_commit_from_md(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(ETHEREUM_SPEC_COMMIT_PREFIX):
                return line[len(ETHEREUM_SPEC_COMMIT_PREFIX):].strip()

def load_str_from_github(url):
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            return response.read().decode('utf-8')
        else:
            raise Exception("Failed to download file from GitHub")

def load_str_from_local(path):
    with open(path, 'r') as file:
        return file.read()

def compare_yaml_keys(github_yaml, local_yaml):
    github_keys = set(github_yaml.keys())
    local_keys = set(local_yaml.keys())

    # Keys in GitHub YAML but not in local YAML
    new_keys = github_keys.difference(local_keys)

    # Keys in local YAML but not in GitHub YAML
    missing_keys = local_keys.difference(github_keys)

    return new_keys, missing_keys

def delete_prerelease_keys(d):
    keys_to_delete = [key for key in d if any(re.compile(regex).search(key) for regex in IGNORE_FROM_REMOTE_CONFIG_KEYS)]
    for key in keys_to_delete:
        del d[key]

def assert_deep_equal_dict(a, b, id):
    try:
        assert a == b
    except AssertionError:
        a_str = json.dumps(a, indent=4, sort_keys=True)
        b_str = json.dumps(b, indent=4, sort_keys=True)
        diff = difflib.ndiff(a_str.splitlines(), b_str.splitlines())
        diff_str = '\n'.join(diff)
        raise AssertionError(f"Difference found in {id} :\n{diff_str}")

# Function to compare two dictionaries and create a diff
def create_diff(local_yaml, github_yaml):
    diff = {}
    all_keys = set(local_yaml.keys()).union(set(github_yaml.keys()))
    for key in all_keys:
        if any(re.compile(regex).search(key) for regex in IGNORE_FOR_DIFF_CONFIG_KEYS):
            continue
        local_value = local_yaml.get(key, "Not Present")
        github_value = github_yaml.get(key, "Not Present")
        if local_value != github_value:
            diff[key] = {'ethereum': str(github_value), 'gnosis': str(local_value)}
    return diff

def parse_md_table_to_json(md_content):
    """Parse a markdown table and convert it to a JSON-like dictionary."""
    json_data = {}
    lines = md_content.splitlines()
    for line in lines[2:]:  # Skip header lines
        if '|' in line:
            parts = [part.strip() for part in line.strip().split('|')]
            if len(parts) < 4:
                raise Exception(f"expected 3 but found {len(parts)} columns in table row {line}")
            key = parts[1].strip('`')
            ethereum = parts[2].strip('`') 
            gnosis = parts[3].strip('`') 
            json_data[key] = {'ethereum': ethereum, 'gnosis': gnosis}
    return json_data

def extract_config_diff_section(md_content):
    return re.search(r'### Config diff\n(.*?)(?=\n###|$)', md_content, re.DOTALL).group(1).strip()

def extract_preset_diff_section(md_content):
    return re.search(r'### Preset diff\n(.*?)(?=\n###|$)', md_content, re.DOTALL).group(1).strip()


parser = argparse.ArgumentParser(description='Compare YAML keys.')
parser.add_argument('--dev', action='store_true', help='check against dev branch')
args = parser.parse_args()

default_commit = read_default_commit_from_md(CONSENSUS_SPEC_FILEPATH)
print("default_commit", default_commit)

config_diff = {}
preset_diff = {}

for local_file_path, remote_url_path in FILES:
    commit = 'dev' if args.dev else default_commit

    url = f"{REMOTE_BASE_URL}/{commit}/{remote_url_path}" 
    print(url)
    github_yaml = yaml.safe_load(load_str_from_github(url))
    local_yaml = yaml.safe_load(load_str_from_local(local_file_path))
    delete_prerelease_keys(github_yaml)

    new_keys, missing_keys = compare_yaml_keys(github_yaml, local_yaml)

    print(local_file_path, commit, remote_url_path)
    if new_keys:
        raise Exception(f"New keys found in GitHub YAML not used in local YAML: {new_keys}")
    elif missing_keys:
        raise Exception(f"Keys in local YAML not found in GitHub YAML: {missing_keys}")
    else:
        print("No differences in keys found.")

    diff = create_diff(local_yaml, github_yaml)
    if "config" in local_file_path:
        config_diff = {**config_diff, **diff}
    else:
        preset_diff = {**preset_diff, **diff}

consensus_spec_str = load_str_from_local(CONSENSUS_SPEC_FILEPATH)
config_diff_table = parse_md_table_to_json(extract_config_diff_section(consensus_spec_str))
preset_diff_table = parse_md_table_to_json(extract_preset_diff_section(consensus_spec_str))

assert_deep_equal_dict(config_diff, config_diff_table, "config diff table")
assert_deep_equal_dict(preset_diff, preset_diff_table, "preset diff table")

