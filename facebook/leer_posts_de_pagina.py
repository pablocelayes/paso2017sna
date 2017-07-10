#!/usr/bin/env python
# -*- coding: utf-8 -*-
from localsettings import EMAIL, PASSWORD

from splinter import Browser

import lxml
from lxml import etree
import time
import json
import datetime as dt
import os
from random import shuffle
from itertools import chain
import re
import urlparse
from math import ceil
from collections import defaultdict

def login(br, email, password):
    br.visit("https://www.facebook.com")
    br.find_by_id("email").first.fill(email)
    br.find_by_id("pass").first.fill(password)
    br.find_by_id("loginbutton").first.click()

    # Go to my profile
    br.find_by_xpath("//a[@title='Profile']").first.click()

def get_post_links(br, htmlparser, max_posts=100):
    for s in range(max_posts/2):
        time.sleep(1)
        br.execute_script("window.scrollTo(0, %d)" % (5000 * s))
        rootnode = etree.fromstring(br.html, htmlparser)
        post_links = rootnode.xpath(".//*[@class='timestampContent']/../../@href")
        post_links = [pl.split('?')[0] for pl in post_links]
        post_links = list(set(post_links))
        nposts = len(post_links)
        print "%d posts, %d pages" % (nposts, s)
        if nposts >= max_posts:
            post_links = post_links[:max_posts]
            break

    return post_links    

if __name__ == '__main__':
    # EMAIL = raw_input("Email address:")
    # PASSWORD = raw_input("Password:")
    htmlparser = etree.HTMLParser()

    user_name = EMAIL.split("@")[0]

    # TODO: cambiar esto para que use el path local
    executable_path = {'executable_path':'/home/pablo/Proyectos/paso2017sna/facebook/chromedriver'}

    br = Browser('chrome', **executable_path)
    # Login
    login(br, EMAIL, PASSWORD)
    
    # pagina = 'hectorbaldassi'
    # pagina = 'martinllaryoraoficial'
    # pagina = 'pablocarrook'
    pagina = 'liliolivero'
    
    #  Load or fetch post links
    post_links_fname = "postlinks_%s.json" % pagina
    try:
        post_links = json.load(open(post_links_fname))
    except Exception as e:
        br.visit('https://www.facebook.com/pg/%s/posts/' % pagina)
        post_links = get_post_links(br,htmlparser)
        with open(post_links_fname, 'w') as f:
            json.dump(post_links, f)

    # Fetch posts data
    url_base = 'https://web.facebook.com'
    data_posts = []
    for i, pl in enumerate(post_links):
        pag, tipo = pl.split('/')[1:3]
        if pag != pagina:
            # TODO: manejar estos casos
            continue
        
        url = url_base + pl
        br.visit(url)
        url_browser = br.driver.current_url.split('?')[0]
        url_link = url.split('?')[0]
        if url_browser != url_link:
            print "Omitiendo redirect"
            print "De:\t %s" % url
            print "A:\t %s" % url_posta

        data = {'url': url}
        
        xp_post = ".//*[contains(@class, 'permalinkPost')][1]"

        try:
            post = br.find_by_xpath(xp_post)[0]
        except Exception as e:
            print "No pudimos leer post para %s" % url
            # TODO: leer /video/
            continue

        ## Fecha

        ## Cuerpo
        # click en "ver más..."

        xp_cuerpo = xp_post + "//div[contains(@class, 'fbUserContent')]/div[1]"
        xp_vermas = xp_cuerpo + '//a[@class="see_more_link"]'

        vermas = br.find_by_xpath(xp_vermas)
        if vermas:
            vermas[0].click()

        cuerpo = br.find_by_xpath(xp_cuerpo)[0]
        data['cuerpo'] = cuerpo.text


        ## Imagen

        ## Contar likes
        xp_likes = ".//*[contains(@class, 'UFILikeSentence')][1]//span[@role='toolbar']/../a[@rel='ignore'][1]"
        likes = post.find_by_xpath(xp_likes)[0]
        data['nlikes'] = likes.text.split('\n')[0]


        ## Listar likes (usuarios)

        ## Comentarios (+likes)
        xp_coments = ".//*[contains(@class, 'fbUserContent')]/div[2]"

        data_posts.append(data)
        print "%d/%d posts leídos" % (i + 1, len(post_links))

    with open("posts_%s.json" % pagina, 'w') as f:
        json.dump(data_posts, f)
