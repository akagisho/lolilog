import sys
import os
import re
import time
import datetime
import requests
from bs4 import BeautifulSoup

class Lolipo:
    URL_TOP = 'https://user.lolipop.jp/'
    URL_LOGIN = 'https://user.lolipop.jp/?mode=login&exec=1'
    URL_ANALYZE = 'https://user.lolipop.jp/?mode=analyze'

    def __init__(self):
        None

    def get_lolipo_domains(self):
        res = requests.get(self.URL_TOP)
        soup = BeautifulSoup(res.text, 'html.parser')
        select = soup.find('select', {'id': 'domain-id'})

        domains = {}
        for option in str(select.contents[0]).split("\n"):
            m = re.search(r'value=[\'"](\d+)[\'"][^>]*>(.*)$', option)
            if m:
                domains[m.group(1)] = m.group(2)
        return domains

    def login(self, account, domain, passwd):
        domain_id = None
        domains = self.get_lolipo_domains()
        for key in domains.keys():
            if domains[key] == domain:
                domain_id = key
                break
        if not domain_id:
            raise Exception('Cannot find domain')

        params = {
            'domain_plan': '0',
            'account': account,
            'domain_id': domain_id,
            'passwd': passwd
        }
        res = requests.post(self.URL_LOGIN, params, allow_redirects=False)
        if res.status_code != 302:
            raise Exception('Cannot login')

        self.sessid = res.cookies.get('LLPPSESSID')

        return self.sessid

    def get_user_domains(self):
        cookies = dict(LLPPSESSID = self.sessid)
        res = requests.get(self.URL_ANALYZE, cookies=cookies)

        soup = BeautifulSoup(res.text, 'html.parser')
        trs = soup.find_all('tr', class_='page-group s4-1')

        domains = {}
        for tr in trs:
            tds = tr.find_all('td')

            content = str(tds[0].contents[1])
            m = re.search(r'https?://([^/]*)', content)
            if m:
                domain = m.group(1)

            content = str(tds[1].contents[1])
            m = re.search(r'id=(\w*)', content)
            if m:
                domain_id = m.group(1)
                domains[domain_id] = domain

        return domains

    def get_domain_id(self, domain):
        domain_id = None

        domains = self.get_user_domains()
        for key in domains.keys():
            if domains[key] == domain:
                domain_id = key
                break

        return domain_id

    def set_domain(self, domain = None):
        domain_id = 'lolipopDomain'
        if domain:
            domain_id = self.get_domain_id(domain)

        url = self.URL_ANALYZE + '&exec=setting&id=' + domain_id
        cookies = dict(LLPPSESSID = self.sessid)
        res = requests.get(url, cookies=cookies)

    def get_access_log(self, save_dir, domain = None):
        self.set_domain(domain)

        today = datetime.datetime.today()
        for i in range(-90, -1):
            date = today + datetime.timedelta(days=i)
            slt_date = datetime.datetime.strftime(date, '%y%m%d')

            print(slt_date)
            file_path = self.get_access_log_date(slt_date, save_dir)
            if file_path:
                print('Saved: ' + file_path)
            else:
                print('not exists')

            time.sleep(0.5)

    def get_access_log_date(self, slt_date, save_dir):
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        params = {'sltDate': slt_date}
        url = self.URL_ANALYZE + '&exec=download'
        cookies = dict(LLPPSESSID = self.sessid)
        res = requests.post(url, params, cookies=cookies)

        if res.headers['Content-Type'] != 'application/octet-stream':
            return

        content_disposition = res.headers['Content-Disposition']
        attribute = 'filename='
        file_name = content_disposition[content_disposition.find(attribute) + len(attribute):]
        file_name = file_name.replace('"', '')

        file_path = save_dir + '/' + file_name
        with open(file_path, 'wb') as f:
            f.write(res.content)

        return file_path

if __name__ == '__main__':
    lolipo_domain = sys.argv[1]
    passwd = sys.argv[2]

    save_dir = 'logs'
    if len(sys.argv) > 3:
        save_dir = sys.argv[3]

    my_domain = lolipo_domain
    if len(sys.argv) > 4:
        my_domain = sys.argv[4]

    lolipo = Lolipo()
    lolipo.login(lolipo_domain.split('.', 1)[0], lolipo_domain.split('.', 1)[1], passwd)
    lolipo.get_access_log(save_dir, my_domain)
