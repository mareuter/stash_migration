import os

import migration
gh = migration.get_login()
requests_left, requests_limit = gh.rate_limiting
print("Requests Left:", requests_left)
print("Request Limit:", requests_limit)
