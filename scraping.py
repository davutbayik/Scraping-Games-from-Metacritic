import requests
from bs4 import BeautifulSoup
import html5lib
import time
import json

print("Scraping for metacritic/search started!")
start_time = time.time()

games_list = open("data/games_list.txt","r").readlines()
games_list = [game.strip() for game in games_list]

keyDict = {'title','developer','genres'}
games_dict = dict([(key, []) for key in keyDict])
error_titles = []

#request header for windows, may encounter errors without correct header
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

for game in games_list:

    URL = 'https://www.metacritic.com/search/all/{}/results'.format(game)
    r = requests.get(url=URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')

    elements = soup.find_all("div", {"class" : "main_stats"})

    #filter out game trailers by searching metacritic score banners in the search page
    for i,element in enumerate(elements):
        try:
            element.find("span", {"class" : "metascore_w medium game positive"}).text
            #found i as the index of first page of game for any platforms in the search page
            break

        except AttributeError:
            #found game trailer, skip to try next element
            continue
    
    try:
        link = elements[i].find('a').get("href")

        URL = f'https://www.metacritic.com{link}'
        r = requests.get(url=URL, headers=headers)
        soup = BeautifulSoup(r.content, 'html5lib')

        try:
            dev = soup.find("li", {"class" : "summary_detail developer"}).find("a").text
            genre = [t.text for t in soup.find("li", {"class" : "summary_detail product_genre"}).find_all("span")][1:]
            
            games_dict['title'].append(game)
            games_dict['developer'].append(dev)
            games_dict['genres'].append(genre)

        except AttributeError:
            error_titles.append(game)
            continue
    
    except IndexError:
        error_titles.append(game)
        continue

print("The time for scraping metacritic/search is:\n --- {} minutes ---\n"
      .format(round(float(((time.time() - start_time)/60)),2)))

print("Scraping for metacritic/search ended!")

print("Number of games succesfully scraped is:", len(games_dict['developer']))
print("Number of games got error while scraping is:", len(error_titles))

with open('data/games/games_dict.json', 'w') as fp:
    json.dump(games_dict, fp, indent=3)

with open('data/games/error_list.txt', 'w') as f:
    for line in error_titles:
        f.write(f'{line}\n')