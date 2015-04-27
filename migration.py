import github

def get_login(token_file=None):
    """Get a Github API handle.

    This function gets a Github API handle. It takes a path to a token file as an optional argument. The
    token file should contain the Github authentication token on the first line of the file. The default
    location for the token file is in the user's home directory under a sub-directory called git. The
    default name for the token file is .token_file.

    Args:
        token_file: A file containing a Github authentication token.

    Returns:
        An instance of the github.Github class.
    """
    if token_file is None:
        # Choose the default token file
        import os
        token_file = os.path.join(os.path.expanduser("~/"), ".token_file")

    with open(token_file, 'r') as fd:
        token = fd.readline().strip()  # Can't hurt to be paranoid
        uname = fd.readline().strip()
    return github.Github(login_or_token=token)

def add_comment(holder, owner, repo, sha, username, comment, line_number, file_path):
    """Insert a comment into a commit.

    This function inserts a comment into a specific commit using the Github API provided by the PyGithub
    package. The function handles both plain comments and diff file comments. None must be passed to both
    line_number and file_path if a plain comment is desired.

    Args:
        holder: A Github object.
        owner: The organization or owner of the Github repository.
        repo: The Github repository name.
        sha: The SHA1 of the commit to insert the comment.
        username: The username associated with the comment.
        comment: The content of the comment.
        line_number: The line number of the file if this is a diff comment.
        file_path: The file path of the file if this is a diff comment.
    """
    import time

    r = holder.get_repo("%s/%s" % (owner, repo))
    c = r.get_commit(sha)

    user_comment = "(%s) %s" % (username, comment)
    if line_number is None:
        line_number = github.GithubObject.NotSet
    if file_path is None:
        file_path = github.GithubObject.NotSet

    c1 = c.create_comment(user_comment, path=file_path, position=line_number)

    print("Status:", c1.raw_headers["status"], " Rate-Limit Remaining:",
          c1.raw_headers["x-ratelimit-remaining"], "Rate-Limit Reset:",
          time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(c1.raw_headers["x-ratelimit-reset"]))))
    if c1 is None:
        print("Comment: %s on repo: %s for sha: %s could not be added!" % (comment, repo, sha))
