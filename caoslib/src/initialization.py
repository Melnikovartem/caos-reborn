import requests
import configparser
import json, pickle
from bs4 import BeautifulSoup as bs
from clint.textui import puts, colored, prompt

from utils.constants import CONFIG_PATH, COOKIES_PATH, LINKS_PATH

def init():
    login = prompt.query('Tell me your login: ')
    password = prompt.query('Tell me your password: ')
    group = prompt.query('Tell me you group number from the caos.ejudge.ru: ')

    config = configparser.ConfigParser()
    config['Credentials'] = {}
    config['Group'] = {}

    config['Credentials']['login'] = login
    config['Credentials']['password'] = password
    config['Group']['group_number'] = group

    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

    init_session()


def init_session():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    credentials = {
        'login': config['Credentials']['login'],
        'password': config['Credentials']['password']
    }

    session = requests.session()

    url = 'https://caos.ejudge.ru/ej/client?contest_id=1{:02d}'.format(int(config['Group']['group_number']))
    start_page = session.post(
        url,
        data=credentials,
        headers=dict(referer=url),
    )

    soup = bs(start_page.content, 'html.parser')
    if 'Permission denied' in soup.text:
        puts(colored.red("Invalid login or password. Run './caos init' again with correct credentials"))        
        exit(0)

    links = soup.find_all('a', {'class': 'menu'})[:-1]
    with open(LINKS_PATH, 'w') as linksfile:
        linksfile.write(json.dumps(dict(map(lambda x: (x.text, x['href']), links)), indent=2))
    
    with open(COOKIES_PATH, 'wb') as cookiesfile:
        pickle.dump(session.cookies, cookiesfile)
