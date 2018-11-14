#!/usr/bin/env python3

import requests
import json, time
from typing import Any, Dict, List, Tuple, Optional, NamedTuple, Union

class NsutsClient:
    def __init__(self, config):
        # type: (Dict[str, Any]) -> None
        self.config = config

    # internal
    def get_cookies(self):
        # type: () -> Dict[str, str]
        return {
            'CGISESSID': self.config['session_id'],
            'PHPSESSID': self.config['session_id']
        }

    def request_get(self, path):
        # type: (str) -> Any
        if path[0] != '/':
            path = '/' + path
        url = self.config['nsuts'] + path
        response = requests.get(url, cookies = self.get_cookies())

        if response.status_code != 200:
            raise Exception("Unknown error during request.")

        return response
        
    # public
    def is_authorized(self):
        # type: () -> bool
        return 'session_id' in self.config

    def auth(self):
        # type: () -> None
        data = {
            'email': self.config['email'],
            'password': self.config['password']
        }
        url = self.config['nsuts'] + '/api/login'
        response = requests.post(url, json = data)
        if response.status_code != 200:
            raise Exception('Authorization error: unable to connect to nsuts')

        auth_result = json.loads(response.text)
        if auth_result['success'] != True:
            raise Exception('Authorization error: ' + auth_result['error'])

        self.config['session_id'] = auth_result['sessid']

    def select_olympiad(self, olympiad_id):
        # type: (int) -> None
        response = self.request_get('/select_olympiad.cgi' + '?olympiad=' + str(olympiad_id))
        # assume everything is ok

    def select_tour(self, tour_id):
        # type: (int) -> None
        response = self.request_get('/select_tour.cgi' + '?tour_to_select=' + str(tour_id))
        # assume everything is ok

    def get_admin_queue(self, limit = 25, tasks = None):
        # type: (int, Optional[List[int]]) -> Any
        url = '/api/queue/submissions?limit=' + str(limit)
        if tasks is not None:
            url = url + '&task=' + ','.join(map(str, tasks))
        response = self.request_get(url)
        submits = json.loads(response.text)
        return submits
    
    def get_solution_source(self, solution_id):
        # type: (int) -> str
        code = self.request_get('/show.cgi?source=' + str(solution_id)).text # type: str
        start_pos = code.find('<code>')
        return code[start_pos + 6:-13]

    def submit_solution(self, task_id, compiler_name, source_text):
        # type: (int, str, Union[bytes,str]) -> None
        data = {
            'lang': compiler_name,
            'task': task_id,
            'text': source_text
        }
        url = self.config['nsuts'] + '/submit.cgi?submit=1'
        response = requests.post(url, cookies = self.get_cookies(), data = data)

    def get_my_last_submit_id(self):
        # type: () -> Optional[int]
        submits = self.get_my_submits_status()
        if len(submits) == 0:
            return None
        submits = sorted(submits, key = lambda s: s['date'])
        return int(submits[-1]['id'])

    def get_my_submits_status(self):
        # type: () -> Any
        response = self.request_get('/api/report/get_report')
        return json.loads(response.text)['submits']


RunResult = NamedTuple('RunResult', [('verdict', str), ('exit_code', int), ('time', float), ('memory', float)])
def nsuolymp_get_results(nsuts, submit_ids, submit_names, admin = False):
    # type: (NsutsClient, List[int], List[str], bool) -> Optional[List[Tuple[str, List[RunResult]]]]
    while True:
        nsuts_results = nsuts.get_my_submits_status()
        id_to_result = {int(res['id']):res for res in nsuts_results}

        all_ready = True
        out_results = []
        for i,sid in enumerate(submit_ids):
            if sid not in id_to_result.keys():
                return None
            res = id_to_result[sid]
            verdicts = res['result_line']
            if verdicts is None:
                all_ready = False
                break
            rr = [RunResult(ver, -1, -1.0, -1.0) for ver in verdicts]
            out_results.append((submit_names[i], rr))

        if all_ready:
            break
        time.sleep(1.0)

    if admin:
        #TODO: request only my own submits
        nsuts_adminres = nsuts.get_admin_queue(limit = 999)
        id_to_result = {int(res['id']):res for res in nsuts_adminres["submissions"]}

        out_results = []
        for i,sid in enumerate(submit_ids):
            assert(sid in id_to_result.keys())
            res = id_to_result[sid]
            verdicts = res['res']
            assert(verdicts is not None)
            tnm = json.loads(res['time_and_memory'])
            rr = []
            for t,ver in enumerate(verdicts):
                test_time = -1.0
                test_memory = -1.0
                if tnm is not None:
                    key = str(t+1)
                    test_time = float(tnm[key]["t"]) * 0.001
                    test_memory = float(tnm[key]["m"])
                rr.append(RunResult(ver, -1, test_time, test_memory))
            out_results.append((submit_names[i], rr))

    return out_results


def main():
    # type: () -> None
    config = {
        # URL is required field in this config
        'nsuts': 'http://10.0.3.162/nsuts-new',

        # There two ways for authentication in NsuTS
        # 1. Specify email and password
        'email': 'test@test.ru',
        'password': 'test',
        # 2. Specify sessid, which will be assigned after successful authenticaion
        #'session_id': 'cbc5750b24f9b17e3fc77a22fa941a1d',

        # Olympid ID and and Tour ID are not using by default, these lines can be omitted
        'olympiad_id': 58,
        'tour_id': 11114
    } # type: Any

    nsuts = NsutsClient(config)
    if not nsuts.is_authorized():
        nsuts.auth()
    #print(nsuts.config['session_id'])
    nsuts.select_olympiad(config['olympiad_id'])
    nsuts.select_tour(config['tour_id'])
    #nsuts.get_admin_queue()
    #source_text = nsuts.get_solution_source(311692)
    #nsuts.submit_solution(117795, 'vcc2015', source_text)
    print(nsuts.get_my_submits_status())
    print(nsuts.get_my_last_submit_id())

if __name__ == '__main__':
    main()
