#!/usr/bin/env pip-run
__requires__ = ['requests', 'beautifulsoup4', 'cowsay']
import requests
from bs4 import BeautifulSoup as BS
import cowsay
res = requests.get('https://python.org')
b = BS(res.text, 'html.parser')
cowsay.dragon(b.find("div", class_="introduction").get_text())
