import database as db

def get_names(conn, verbosity=0):
    """Create user name mapping.

    This function creates a two-key map that translates a Stash user ID or a Stash user name to a
    corresponding full name.

    Args:
        conn: A connection to a Stash DB.
        verbosity: Set the verbosity of the function.

    Returns:
        A dict with two keys: Stash user ID (int) and Stash user name (str) and a value of a user's
        full name.
    """
    sql = "select stash_user.id, user_name, display_name from stash_user, sta_normal_user, "
    sql += "cwd_user where sta_normal_user.user_id = stash_user.id and "
    sql += "cwd_user.user_name = sta_normal_user.name;"

    if verbosity > 0:
        print("Getting user names")
    res = db.get_db_data(conn.cursor(), sql)

    names = {}
    for values in res:
        names[(int(values[0]), values[1])] = values[2]

    return names

def get_repo_id(conn, repo_name, verbosity=0):
    """Get repository ID from name.

    This function get the Stash repository ID from a repository name.

    Args:
        conn: A connection to a Stash DB.
        repo_name: The repository name to retrieve the ID for.
        verbosity: Set the verbosity of the function.

    Returns:
        The Stash repository ID (int).
    """
    sql = "select id from repository where name = \"%s\";" % repo_name

    if verbosity > 0:
        print("Getting repository ID")
    res = db.get_db_data(conn.cursor(), sql)

    ids = [int(values[0]) for values in res]
    return ids

def get_prs(conn, repo_id, verbosity=0):
    """Get pull requests for repository.

    This function retrieves the pull requests for a given repository.

    Args:
        conn: A connection to a Stash DB.
        repo_id: The repository ID to retrieve pull requests for.
        verbosity: Set the verbosity of the function.

    Returns:
        A dict of pull requests. The content of the dictionary looks like:

        {'5828ac8526f29582d95820572e727ae7527c728b': {'title': 'A title', 'description': 'A description',
                                                      'branch_name': 'bugfix/cool-branch-name'}...}

        where the key is a SHA1 from a git repository.
    """
    sql = "select id, title, description, from_branch_name "
    sql += "from sta_pull_request where pr_state = 1 and "
    sql += "from_repository_id = %d;"

    if verbosity > 0:
        print("Getting pull requests")

    labels = ["title", "description", "branch_name"]
    prs = {}

    for rid in repo_id:
        res = db.get_db_data(conn.cursor(), sql % rid)
        for values in res:
            # Stupid Python 2.6 can't handle real dictionary comprehensions
            prs[int(values[0])] = {labels[0]: values[1], labels[1]: values[2], labels[2]: values[3]}

    return prs

def get_comments(conn, names, pr_id, verbosity=0):
    """Get pull request comments.

    This function gets all of the comments on a pull request. It handles getting both plain comments and
    inline diff file comments.

    Args:
        conn: A connection to a Stash DB.
        names: The user name mapping dict.
        pr_id: The Stash pull request ID (int)
        verbosity: Set the verbosity of the function.

    Returns:
        A list of comments with the following content:

        (User name (str), Comment (str), Line number (int), File path (str))

        where line number and file path can be None if the comment is a plain comment.
    """
    sql = "select sc.id, author_id, comment_text from sta_pr_comment_activity as spca, "
    sql += "sta_pr_activity as spa, sta_pull_request as spr, sta_comment as sc "
    sql += "where spca.activity_id = spa.activity_id and spa.pr_id = spr.id and "
    sql += "spca.comment_id = sc.id and spr.id = %d;" % pr_id

    if verbosity > 0:
        print("Getting pull request comments")
    res = db.get_db_data(conn.cursor(), sql)

    import extras
    comments = []

    for values in res:
        line_number = None
        file_path = None

        # Check if this is a diff comment
        sql = "select line_number, to_path from sta_diff_comment_anchor as "
        sql += "sdca where sdca.comment_id = %s" % values[0]
        res1 = db.get_db_data(conn.cursor(), sql)
        if len(res1) != 0:
            if verbosity > 2:
                print("A:", res1)
            line_number = int(res1[0][0])
            file_path = res1[0][1]

        comments.append((extras.get_fullname(names, values[1]), values[2], line_number, file_path))

    return comments
