#!python3
import json
from nsuts import *
from nsuolymp_cfg import *

nsuts = NsutsClient(nsuts_options)
nsuts.auth()
nsuts.select_olympiad(183)
nsuts.select_tour(11362)

res = nsuts.get_admin_queue(limit = 9999)
data = list(sorted(res['submissions'], key = lambda x: int(x['id'])))
with open("queue.json", "w") as f:
    json.dump(data, f, indent=2)
