# fighter_crawling
This tools crawls data of MMA fighters, matchs and events on [Tapology](https://www.tapology.com)
## Requirements
- pycurl 
- requests
- BeautifulSoup
```
pip install pycurl
pip install requests
pip install bs4
```
## Note
You may receive wrong HTML or encounter Error 403 while crawling due to site blocking/cheating techniques.

This is solved by adding the header to mimic a real browser's GET request. 

`utility.py` contains a set of user-agent.

