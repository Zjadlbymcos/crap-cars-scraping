import requests
import re
import csv
from bs4 import BeautifulSoup
from time import sleep


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

# marka = input("daj mie marke\n")
# model = input("daj mie model\n")

marka = "volkswagen"
model = "passat"

csvOutputFileName = f"{marka}-{model}.csv"

url = f"https://www.olx.pl/motoryzacja/samochody/{marka}/{model}/"

offersOutput = []
currentPage = 1
totalPages = 0

while url:
    sleep(1)
    rawPage = requests.get(url)
    page = BeautifulSoup(rawPage.text, "html.parser")

    if currentPage == 1:
        totalPages = int(page.findAll("a", attrs={"data-cy": "page-link-last"})[0].find("span").text)

    printProgressBar(currentPage, totalPages)

    for offer in page.find("table", {"class": "offers"}).find_all("tr", {"class": "wrap"}):
        offerUrl = offer.find("a", {"class": "thumb"})[
            "href"] if offer.find("a", {"class": "thumb"}) else None

        if offerUrl:
            sleep(1)
            offerPage = BeautifulSoup(
                requests.get(offerUrl).text, "html.parser")

            if "olx.pl" in offerUrl:
                productionYear = (offerPage.findAll("th", text=re.compile("Rok produkcji")))[
                    0].find_parent("tr").find("strong").text.strip()

                mileage = re.sub("[km]|\ ", "", (offerPage.findAll("th", text=re.compile("Przebieg")))[
                    0].find_parent("tr").find("strong").text.strip())
                
            if "otomoto.pl" in offerUrl:
                productionYear = (offerPage.findAll("span", text=re.compile("Rok produkcji")))[
                    0].find_parent("li").find("div").text.strip()

                mileage = re.sub("[km]|\ ", "", (offerPage.findAll("span", text=re.compile("Przebieg")))[
                    0].find_parent("li").find("div").text.strip())

            offersOutput.append([productionYear, mileage])
            

    next = page.find("span", {"class": "next"})
    url = next.find("a")["href"] if next.find("a") else None
    currentPage = currentPage + 1

with open(csvOutputFileName, "w") as file:
    headers = ("Rok produkcji", "Przebieg")
    csvWriter = csv.writer(file)
    csvWriter.writerows(offersOutput)
