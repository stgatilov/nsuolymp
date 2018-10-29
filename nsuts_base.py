#!/usr/bin/env python3

import requests
import json

class NsutsClient:
    def __init__(self, config):
        self.config = config

    # internal
    def get_cookies(self):
        return {
            'CGISESSID': self.config['session_id'],
            'PHPSESSID': self.config['session_id']
        }

    def request_get(self, path):
        if path[0] != '/':
            path = '/' + path
        url = self.config['nsuts'] + path
        response = requests.get(url, cookies = self.get_cookies())

        if response.status_code != 200:
            raise Exception("Can't change tour")

        return response
        
    # public
    def is_authorized(self):
        return 'session_id' in self.config

    def auth(self):
        data = {
            'email': self.config['email'],
            'password': self.config['password']
        }
        url = self.config['nsuts'] + '/api/login'
        response = requests.post(url, data)
        if response.status_code != 200:
            raise Exception('Authorization error: unable to connect to nsuts')

        auth_result = json.loads(response.text)
        if auth_result['success'] != True:
            raise Exception('Authorization error: ' + auth_result['error'])

        self.config['session_id'] = auth_result['sessid']

    def select_olympiad(self, olympiad_id):
        response = self.request_get('/select_olympiad.cgi' + '?olympiad=' + str(olympiad_id))
        # assume everything is ok

    def select_tour(self, tour_id):
        response = self.request_get('/select_tour.cgi' + '?tour_to_select=' + str(tour_id))
        # assume everything is ok

    def get_admin_queue(self, limit = 25, tasks = []):
        url = '/api/submission.php?limit=' + str(limit)
        if len(tasks) > 0:
            url = url + '&task=' + ','.join(map(str, tasks))
        response = self.request_get(url)
        submits = json.loads(response.text)
        return submits
    
    def get_solution_source(self, solution_id):
        code = self.request_get('/show.cgi?source=' + str(solution_id)).text
        start_pos = code.find('<code>')
        return code[start_pos + 6:-13]

    def submit_solution(self, task_id, compiler_name, source_text):
        data = {
            'lang': compiler_name,
            'task': task_id,
            'text': source_text
        }
        url = self.config['nsuts'] + '/submit.cgi?submit=1'
        response = requests.post(url, cookies = self.get_cookies(), data = data)

    def get_my_last_submit_id(self):
        submits = self.get_my_submits_status()
        if len(submits) == 0:
            return None
        submits = sorted(submits, key = lambda s: s['date'])
        return int(submits[-1]['id'])

    def get_my_submits_status(self):
        response = self.request_get('/api/report')
        return json.loads(response.text)['submits']


def main():
    config = {
        # URL is required field in this config
        'nsuts': 'http://192.168.1.7/nsuts-new',

        # There two ways for authentication in NsuTS
        # 1. Specify email and password
        'email': 'test@test.ru',
        'password': 'test',
        # 2. Specify sessid, which will be assigned after successful authenticaion
        'session_id': 'cbc5750b24f9b17e3fc77a22fa941a1d',

        # Olympid ID and and Tour ID are not using by default, these lines can be omitted
        'olympiad_id': 58,
        'tour_id': 11114
    }

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
