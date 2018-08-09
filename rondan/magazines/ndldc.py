#
# Functions for NDL Digital Collection article data fetching
#
# author: peter.muehleder@uni-leipzig.de
#

from ..utils import get_url_as_soup
import time

TIMEOUT = 1
ARTICLE_URL = 'http://iss.ndl.go.jp/api/opensearch?dpgroupid=digitalcontents&from={year_from}-01&until={year_to}-12&title={magazine}&publisher={publisher}'


def get_issue(permalink):
    soup = getUrlAsSoup(permalink+".rdf", parser="xml")
    time.sleep(TIMEOUT)
    toc = []

    try:
        issueTitle = soup.find("title").text
    except:
        issueTitle = ""
    volume = soup.find("volume")
    try:
        value = soup.find("value").text
    except:
        value = ""

    #get time of publication
    try:
        issued = soup.find("issued").text
    except:
        issued = "0-0"
    datesplit = issued.split('-')
    if len(datesplit) >= 2:
        year = int(datesplit[0])
        month = int(datesplit[1])
    else:
        year = int(datesplit[0])
        month = 0

    if volume and soup:
        vol = volume.Description.value.text

        toctree = soup.find("tableOfContents")
        if toctree:
            print("\t Mining " + issueTitle + " ...")

            #iterate through table of contents
            for item in toctree.find_all("title"):
                articlestr = item.text.replace("//", "").replace("@@", "")

                title = ""
                pages = ""
                authors = ""

                parts = articlestr.split('/')

                if len(parts) == 1:
                    title = parts[0]
                elif len(parts) == 2:
                    title = parts[0]
                    if "p" in parts[1] and "(" in parts[1]:
                        pages = parts[1]
                    else:
                        authors = parts[1].strip().split(";")
                else:
                    last = parts[len(parts) - 1]
                    if "p" in last and "(" in last:
                        pages = last
                        if len(parts[len(parts)-2]) > 15 and ";" not in parts[len(parts)-2]:
                            content = parts[:len(parts)-1]
                        else:
                            authors = parts[len(parts) - 2].strip().split(";")
                            content = parts[0:len(parts) - 2]
                        for c in content:
                            title += c
                    else:
                        authors = last.strip().split(";")
                        content = parts[0:len(parts) - 2]
                        for c in content:
                            title += c
                pageFrom = 0
                pageUntil = 0
                if pages != "":
                    if pages[0] == " ":
                        pages = pages[1:len(pages)].split(" ")[0]
                    else:
                        pages = pages.split(" ")[0]


                pages = pages.replace('p',"")
                pages = pages.split('～')
                pageFrom = str(pages[0])
                if len(pages) > 1:
                    if pages[1] != "":
                        pageUntil = str(pages[1])

                toc.append({'title': title.replace("-","ー"),
                            'authors': authors,
                            'pageFrom': pageFrom,
                            'pageUntil': pageUntil})

    return {'title': issueTitle,
            'year': year,
            'month': month,
            'toc': toc }



def ndldc_get_issues(magazine, publisher, year_from, year_to):
    issues = []

    soup = get_url_as_soup(ARTICLE_URL.format(magazine=magazine, publisher=publisher, year_from=year_from, year_to=year_to), parser="xml")
    total_results = int(soup.find("totalResults").text)
    print("Issues found: "+repr(total_results))

    for item in soup.find_all("item"):
        title = item.find("title").text
        
        if str(magazine) == str(title):
            permalink = item.find("link").text
            vol = item.find("volume")
            issue = get_issue(permalink)
            issues.append(issue)
       

    return issues


