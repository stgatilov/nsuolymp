#!python3

# Dumps whole queue of selected tour into "queue.json" file.
# Used e.g. by Snark to merge ratings from WSO and opencup.
#
# Usage:
#   1) Copy this script into nsuolymp directory.
#   2) Ensure that correct credentials and nsuts URL are set in config.
#   3) Run this script with olympiadId and tourId from nsuts as command line arguments.

import json, sys
from nsuts import *
from nsuolymp_cfg import *

olympiad_id = int(sys.argv[1])
tour_id = int(sys.argv[2])

nsuts = NsutsClient(nsuts_options)
nsuts.auth()
nsuts.select_olympiad(olympiad_id)
nsuts.select_tour(tour_id)

res = nsuts.get_admin_queue(limit = 99999)
data = list(sorted(res['submissions'], key = lambda x: int(x['id'])))
with open("queue.json", "w") as f:
    json.dump(data, f, indent = 2)
