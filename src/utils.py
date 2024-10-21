from parsel import Selector
from typing import Iterable

def splicegen(maxchars: int, stringlist: list[str]) -> Iterable[list[int]]:
    runningcount = 0  
    tmpslice = []  
    for i, item in enumerate(stringlist):
        runningcount += len(item)
        if runningcount < maxchars:
            tmpslice.append(i)
        else:
            yield tmpslice
            tmpslice = [i]
            runningcount = len(item)
    yield tmpslice

def join_strings(strs: list[str]) -> str | None:
    has_non_none = any(x is not None for x in strs)
    if has_non_none:
        return ' '.join(s for s in strs if s is not None)
    else:
        return None
        
def get_query(content: Selector, query: str, sep: str = ' ') -> str | list[str] | None:
    response = content.xpath(query).getall()
    if not response:
        return None
    
    if sep:
        return sep.join(response)
    else: 
        return response