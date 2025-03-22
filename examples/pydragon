#!/usr/bin/env pip-run
import cowsay
import requests
from bs4 import BeautifulSoup as BS

res = requests.get('https://python.org')
b = BS(res.text, 'html.parser')
cowsay.dragon(b.find("div", class_="introduction").get_text())
