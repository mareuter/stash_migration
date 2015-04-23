import optparse
import os
import sys

import contents
import database as db
import extras
import migration

if __name__ == "__main__":
    # Setup argument parser
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbosity", action="count", default=0, help="Increase output verbosity")
    parser.add_option("-o", "--org", default="lsst-sims",
                      help="Set the organization for comment migration repository.")
    parser.add_option("-c", "--db-connect-file", help="Pass a file containing the connection information "
                      "a Stash database.")
    parser.add_option("-t", "--token-file", help="Pass a token file for Github API authentication.")
    parser.add_option("-n", "--no-migration", action="store_true", default=False,
                      help="Run the script but do not perform the migration actions.")
    parser.add_option("-m", "--manual-assocs", help="Provide a file with manual associations between "
                      "pull requests and merge commits.")

    (options, args) = parser.parse_args()

    try:
        repo_name = args[0]
    except IndexError:
        print("Usage: migrate_comment.py <repo name>")
        sys.exit(255)

    organization = options.org
    verbosity = options.verbosity
    token_file = options.token_file
    no_migration = options.no_migration
    manual_assocs = options.manual_assocs
    db_connect_file = options.db_connect_file

    if verbosity > 0:
        print("Getting database connection.")
    conn = db.get_conn(db_connect_file, verbosity)

    # Gather all of the repositories pull requests
    names = contents.get_names(conn, verbosity)
    repo_id = contents.get_repo_id(conn, repo_name, verbosity)
    pull_requests = contents.get_prs(conn, repo_id, verbosity)
    print("Number of pull requests:", len(pull_requests))
    for pr_id in pull_requests:
        comments = contents.get_comments(conn, names, pr_id, verbosity=verbosity)
        pull_requests[pr_id]["comments"] = comments

    if verbosity > 1:
        print
        print pull_requests
        print

    # Get the merge commits from the log dump file
    merges = extras.get_merge_commits(repo_name, names)
    print("Number of merge commits:", len(merges))
    if verbosity > 1:
        print merges
        print

    manual = extras.get_manual_associations(manual_assocs, verbosity)
    if manual_assocs is not None:
        print("Number of manual associations:", len(manual))

    comment_count = 0

    # Migrate to Github!
    gh = migration.get_login(token_file)
    for pr_id in pull_requests:
        # Connect the merge commit to the pull request
        merge_sha = None
        for sha in merges:
            if merges[sha]["branch"] == pull_requests[pr_id]["branch_name"] \
                    and merges[sha]["user"] is not None:
                merge_sha = sha
                break

        if merge_sha is None:
            try:
                merge_sha = manual[pr_id]
            except KeyError:
                print("Pull request ID %s cannot be matched to a merge commit!" % pr_id)
                print(pull_requests[pr_id]["title"])
                print
                continue

        # Build initial PR comment
        pr_comment = "%s\n%s" % (pull_requests[pr_id]["title"], pull_requests[pr_id]["description"])
        comment_count += 1
        if not no_migration:
            migration.add_comment(gh, organization, repo_name, merge_sha, merges[merge_sha]["user"],
                                  pr_comment, None, None)

        # Now go through all the PR comments
        for comment in pull_requests[pr_id]["comments"]:
            comment_count += 1
            if not no_migration:
                migration.add_comment(gh, organization, repo_name, merge_sha, comment[0], comment[1],
                                      comment[2], comment[3])

    print("Number of comments:", comment_count)
