import os
import github

# Choose the default client file
client_file = os.path.join(os.path.expanduser("~/"), ".client_file")

with open(client_file, 'r') as fd:
    client_id = fd.readline().strip()  # Can't hurt to be paranoid
    client_secret = fd.readline().strip()

gh = github.Github(client_id=client_id, client_secret=client_secret)
requests_left, requests_limit = gh.rate_limiting
print("Requests Left:", requests_left)
print("Request Limit:", requests_limit)
