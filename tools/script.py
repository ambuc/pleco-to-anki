# 2021 03 21

import bs4
import codecs
import csv

if __name__ == "__main__":
    # expects https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO
    with open("/Users/jamesbuckland/Desktop/frequency_list.html", encoding='unicode_escape') as fp:
        soup = bs4.BeautifulSoup(fp, "html.parser")

        # full table
        x = str(soup.body.pre)
        # remove leading "<pre>"
        x = x[5:]
        lns = x.split("<br/>")
        #remove trailing "<pre>"
        lns = lns[0:-1]

        with open('some.csv', 'w', newline='') as f:
            writer = csv.writer(f)

            for ln in lns:
                chunks = ln.split('\t')
                try:
                    # https://stackoverflow.com/a/20922160
                    writer.writerows([[chunks[0], chunks[1].encode('latin1').decode('gb2312'), chunks[2], chunks[3]]])
                except Exception as e:
                    print(e)


