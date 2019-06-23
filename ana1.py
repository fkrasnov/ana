from bs4 import BeautifulSoup
import glob
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymystem3 import Mystem
import os
from textblob import TextBlob
import re

m = Mystem()

#def clean(word):
#    return ''.join(letter for letter in word.lower() if 'a' <= letter <= 'z')
    
#wl = WordNetLemmatizer()
#stopWords = set(stopwords.words('english'))

files = glob.glob('/opt/lun3/07.551.11.4002/rj/CP/*.xml') + glob.glob('/opt/lun3/07.551.11.4002/rj/NPR/*.xml')


wvfile = open('rj.wv','w')
csvfile = open('rj.csv','w')
csvfile.write('TEXT|DATE|VOLUME|NUM|JOURNAL|TITLE\n')
authorsfile = open('rja.csv','w')
authorsfile.write('ID|FIO|ORG|JOURNAL\n')
i = 1
for f in files:
    print (f)
    try:
        x = open(f, 'r')
        soup = BeautifulSoup(x,features="html.parser")
        x.close()
    except:
        print ('BIN: ', f)
        continue
        
    date  = soup.issue.dateuni.getText()
    volume = soup.issue.volume.getText()
    num = soup.issue.number.getText()
    journal = soup.journal.title.getText()
    for a in soup.journal.issue.articles:
        if a.name != 'article' : continue
        title = a.arttitle.getText().replace("\n",'').replace(':','')
        blob_object = TextBlob(a.getText()) 
        words = [m.lemmatize(w.lower())[0] for w in blob_object.words  
                    if (w.lower() not in stopwords.words('russian')) & bool(re.search(r'^[а-яА-Я]+$', w)) & (len(w)>2)]
        bigrm = [ w[0]+"_"+w[1] for w in nltk.bigrams(words)] 
        buf_ru = " ".join(words + bigrm).replace("\n",'').replace(':','')
        if (len(buf_ru) > 20) :
            #wvfile.write('%d |TEXT %s |DATE %s |VOLUME %s |NUM %s |JOURNAL %s |TITLE %s\n' % (i,buf_ru,date,volume,num,journal,title))
            wvfile.write(buf_ru+'\n')
            csvfile.write('%s|%s|%s|%s|%s|%s\n' % (buf_ru,date,volume,num,journal,title))
            for au in a.authors:
                aur = au.find(lang="RUS")
                if aur is None: continue
                fio = 'NAN'
                if aur.surname is not None:
                    fio = aur.surname.getText()
                if aur.initials is not None:
                    fio +=" "+aur.initials.getText()
                org = 'NAN'
                if aur.orgname is not  None:
                    org = aur.orgname.getText().replace('\n', ' ').replace('|',' ')
                authorsfile.write('%s|%s|%s|%s\n' % (i,fio,org,journal) )
            i += 1

wvfile.close()
csvfile.close()
authorsfile.close()
