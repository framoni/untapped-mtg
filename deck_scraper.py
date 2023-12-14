"""
Scrape Standard MTG Arena meta decks for wildcards
"""

from bs4 import BeautifulSoup
import json
import os
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--start-maximized")
browser = webdriver.Chrome(options=options)


def login():
    browser.get('https://accounts.untapped.gg/login')
    browser.find_element(By.ID, 'username').send_keys('ramoguru@gmail.com')
    browser.find_elements(By.CLASS_NAME, 'Input__InnerInput-sc-1tlu48p-0.ioCvVj')[1].send_keys('@htwPH.Z6qQ3+UK')
    browser.find_element(By.CLASS_NAME, 'sc-bdVaJa.ewcTgJ.button').click()
    time.sleep(5)


def get_wildcards(html):
    wildcards = []
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all(class_='CollectionCardIcon__MissingCard-sc-1w1jc4y-4 gxbyyw')
    for it, c in enumerate(cards):
        try:
            raw_name = c.find(class_='sc-biBsmb sc-ljRaeN ffKkww ilyNwr card-tile')['aria-label']
            name = ''.join(raw_name.split(',')[:-2])
            quantity = int(raw_name.split(',')[-2].split('x')[0])
            rarity = raw_name.split(',')[-1].split(' ')[1]
            wildcards.append({'name': name, 'quantity': quantity, 'rarity': rarity})
        except TypeError:
            return 'failed'
    return wildcards


def get_pics(browser, decks):
    url = 'https://mtga.untapped.gg/meta/decks'
    browser.get(url)
    delay = 1
    max_tries = 10
    old_num = 0
    counter = 0
    pics_num = 0
    while True:
        browser.execute_script("window.scrollBy(0 , 500 );")
        time.sleep(delay)
        boxes = browser.find_elements(By.CLASS_NAME, 'DecksListResult__DeckRowContainer-sc-1nwze7u-3.btmbfJ')
        deck_titles = [b.find_element(By.CLASS_NAME, 'sc-jdPOwN.lgfshW').text for b in boxes]
        for it, title in enumerate(deck_titles):
            pic_name = 'pics/' + title + '.png'
            try:
                if not os.path.exists(pic_name):
                    browser.execute_script("arguments[0].scrollIntoView();", boxes[it])
                    boxes[it].screenshot(pic_name)
                    pics_num += 1
            except:
                pass
        print("Pics taken: {}".format(pics_num))
        new_num = pics_num
        if new_num == old_num:
            counter += 1
            if counter == max_tries:
                break
        else:
            counter = 0
        old_num = new_num


def get_decks(browser):
    decks = {}
    delay = 1
    max_tries = 10
    old_length = 0
    counter = 0
    while True:
        browser.execute_script("window.scrollBy(0 , 500 );")
        time.sleep(delay)
        boxes = browser.find_elements(By.CLASS_NAME, 'DecksListResult__DeckRowContainer-sc-1nwze7u-3.btmbfJ')
        deck_titles = [b.find_element(By.CLASS_NAME, 'sc-jdPOwN.lgfshW').text for b in boxes]
        boxes_html = [b.get_attribute('innerHTML') for b in boxes]
        # for it, b in enumerate(boxes):
        #     pic_name = 'pics/' + deck_titles[it] + '.png'
        #     try:
        #         if not os.path.exists(pic_name):
        #             b.screenshot(pic_name)
        #     except:
        #         pass
        deck_wildcards = [get_wildcards(html) for html in boxes_html]
        for it, title in enumerate(deck_titles):
            if title not in decks and deck_wildcards[it] != 'failed':
                decks[title] = deck_wildcards[it]
        print("Decks found: {}".format(len(decks)))
        new_length = len(decks)
        if new_length == old_length:
            counter += 1
            if counter == max_tries:
                break
        else:
            counter = 0
        old_length = new_length
    return decks


def main():
    login()
    url = 'https://mtga.untapped.gg/meta/decks'
    browser.get(url)
    time.sleep(5)
    browser.find_element(By.XPATH, "//*[contains(text(), 'AGREE')]").click()
    decks = get_decks(browser)
    with open('mtga_standard_wc.json', 'w') as f:
        f.write(json.dumps(decks))
    get_pics(browser, decks)


if __name__ == "__main__":
    main()
