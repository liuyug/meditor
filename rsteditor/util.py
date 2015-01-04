
import urllib2
import urllib
import gzip

from PyQt4 import QtCore


def toUtf8(text):
    if text is None:
        return b''
    if isinstance(text, QtCore.QString):
        return unicode(text.toUtf8(), encoding='utf-8')
    if not isinstance(text, unicode):
        return text.decode('utf-8', 'ignore')
    return text

def downloadFile(url, path=None, verbose=True):
    """ Download from internet """
    retry = 3
    timeout = 30
    intervaltime = 5
    zip=False
    agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130619 Firefox/17.0'
    #agent = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1'
    while True:
        try:
            r = urllib2.Request(urllib.quote(url, safe=':/=?&'))
            r.add_header('User-Agent',agent)
            d = urllib2.urlopen(r, timeout = timeout)
            if 'content-encoding' in d.info():
                print('!!Content-Encoding:', d.info()['content-encoding'])
                zip=True
            if path:
                f = open(path,'wb')
                if zip:
                    f.write(gzip.decompress(d.read()))
                else:
                    f.write(d.read())
                ct=d.info()['content-type']
                url2=d.geturl()
                d.close()
                f.close()
                return (ct, path, url2)
            else:
                if zip:
                    data=gzip.decompress(d.read())
                else:
                    data = d.read()
                ct=d.info()['content-type']
                url2=d.geturl()
                d.close()
                return (ct, data, url2)
        except Exception as err:
            print('Error : %s - %s'% (err, url))
            retry -= 1
            if retry > 0:
                print('Wait %d sec and try again... %d'% (intervaltime, retry))
                time.sleep(intervaltime)
                intervaltime += 5
                timeout += 10
            else:
                print('Can\'t download, and return NONE.')
                return (None,None,url)
