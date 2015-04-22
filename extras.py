def get_fullname(name_dict, key):
    """Get a full name from a mapping.

    This function returns the full name for a given user name or ID.

    Args:
        name_dict: The dict object containing the name mapping.
        key: The user name or ID to search the name mapping dict for.

    Returns:
        The full name associated with the given user name or ID. None is returned if the key doesn't match
        anything in the dict.
    """
    for k in name_dict:
        if key in k:
            return name_dict[k]
    return None

def get_merge_commits(repo_name, names):
    """Get merge commits from file.

    This function creates a dict of merge commits from a file based on the repository name. The file should
    live in a directory called merges underneath the main execution script. The file should have the name
    <repo name>.log.

    Args:
        repo_name: The repository name to retrieve merge commits for.
        names: The name mapping dict object.

    Returns:
        A dict of merge commits with the following format:

        {'58137c37e7279a940d8f8482589s94948a0b059298e9': {'user': 'Full Name',
                                                          'branch': 'bugfix/cool-branch-name'}...}
    """
    import os
    merges = {}
    merge_file = os.path.join("merges", "%s.log" % repo_name)
    with open(merge_file, 'r') as fd:
        for line in fd:
            values = line.strip().split()
            if "master" == values[-1]:
                # Older merge commits?
                try:
                    branch_name = values[10]
                except IndexError:
                    print("Cannot find branch for %s" % line)
                full_name = " ".join(values[1:3])
            else:
                branch_name = values[-1].strip('\'')
                full_name = get_fullname(names, values[1])
                if full_name is None:
                    full_name = " ".join(values[1:3])
            merges[values[0]] = {"user": full_name, "branch": branch_name}

    return merges

def get_manual_associations(man_file, verbosity=0):
    """Get manual associations from a file.

    This function gets manual associations between merge commits and pull requests. The format of the file
    should be:

    Pull request ID: Commit SHA1
    304: 74d3002
    ...

    Args:
        man_file: The filename containing the manual associations.
        verbosity: Set the verbosity of the function.

    Returns:
        A dict of the manual associations with the key being the pull request ID and the value being the
        commit SHA1.
    """
    man_assocs = {}
    if man_file is not None:
        with open(man_file, 'r') as mfile:
            for line in mfile:
                values = line.strip().split(':')
                man_assocs[int(values[0])] = values[1].strip()

    return man_assocs
