"""
    Created on 2012-01-27
    @author: jldupont
"""
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup


def parse(page):
    try:
        soup = BeautifulSoup(page)
        return ("ok:html", soup)
    except:
        try:
            soup = BeautifulStoneSoup(page)
            return ("ok:xml", soup)
        except:
            return ("error", None)
    


def fetch(page):
    """
    https://gist.github.com/1691098
    
    >> code, (code, headers, data)=fetch("http://www.google.com/googlebooks/uspto-patents-grants-biblio.html")
    >> print headers   
    {'x-xss-protection': '1; mode=block', 
    'x-content-type-options': 'nosniff', 
    'expires': 'Sat, 28 Jan 2012 01:46:44 GMT', 
    'vary': 'Accept-Encoding', 
    'server': 'sffe', 
    'last-modified': 'Fri, 27 Jan 2012 13:40:05 GMT', 
    'connection': 'close', 
    'cache-control': 'private, max-age=0', 
    'date': 'Sat, 28 Jan 2012 01:46:44 GMT', 
    'content-type': 'text/html'}
    """
    try:
        response=urllib2.urlopen(page)
        data=response.read()
        code=response.getcode()
        headers=response.info().items()
        h=headers_to_dict(headers)
        return ("ok", (code, h, data))
    except IOError, e:
        try:    code=e.code
        except: code="?"
        return ("error", (code, None, None))
    except Exception, e:
        return ("error", (e, None, None))
    
    
def headers_to_dict(headers):
    d={}
    for item in headers:
        key, value=item
        d[key.lower()]=value
    return d
    

def extract_anchors(soup):
    """
    >> status, (code, headers, data)=fetch("http://www.google.com/googlebooks/uspto-patents-grants-biblio.html")
    >> soup=parse(data)
    >> print extract_anchors(soup)
    
    """
    try:
        return soup.findAll('a')
    except:
        return None

def extract_href(soup):
    """
    >>> status, (code, headers, data)=fetch("http://www.google.com/googlebooks/uspto-patents-grants-biblio.html")
    >>> soup=parse(data)
    >>> extract_href(soup)
    
    """
    try:
        anchors=extract_anchors(soup)
        result=[]
        for anchor in anchors:
            href=anchor.get("href", None)
            if href is not None:
                result.append(str(href))
            
        return ("ok", filter(is_http_href, result))
    except:
        return ("error", None)

def f_extract_href((code, soup)):
    return extract_href(soup)

def is_http_href(href):
    try: 
        href=href.lower()
        return href.startswith("http://")
    except:
        return False

    
if __name__=="__main__":
    import doctest
    doctest.testmod()