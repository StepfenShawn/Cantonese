from collections import namedtuple
import re

marco = namedtuple("marco", ["pattern", "alter"])

person_corr_marcos = marco(
    pattern=lambda s: re.match(r"(.*)同(.*)有幾襯", s, re.S),
    alter=lambda p: " corr(" + p.group(1) + ", " + p.group(2) + ") ",
)

lappend = marco(
    pattern=lambda s: re.match(r"(.*)加啲(.*)", s, re.S),
    alter=lambda p: p.group(1) + "->append(" + p.group(2) + ")",
)

lremove = marco(
    pattern=lambda s: re.match(r"(.*)摞走(.*)", s, re.S),
    alter=lambda p: p.group(1) + "->remove(" + p.group(2) + ")",
)

lclear = marco(
    pattern=lambda s: re.match(r"(.*)散水", s, re.S),
    alter=lambda p: p.group(1) + "->clear()",
)

# Build-in Marcos
marcos = [person_corr_marcos, lappend, lremove, lclear]


def explore_all_macros(code: str):
    match_search = re.search(re.compile(r"\<\|.*?\|\>", re.S), code)
    while match_search:
        case_marco = match_search.group()[2:-2]
        find = False
        for m in marcos:
            p = m.pattern(case_marco)
            if p:
                code = code.replace(match_search.group(), m.alter(p))
                find = True
        if not find:
            exit()
        match_search = re.search(re.compile(r"\<\|.*?\|\>", re.S), code)
    return code
