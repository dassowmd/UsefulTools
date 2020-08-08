import re


def find_IP_Regex(txt):
    re1 = "(\\d+)"  # Integer Number 1
    re2 = "(.)"  # Any Single Character 1
    re3 = "(\\d+)"  # Integer Number 2
    re4 = "(.)"  # Any Single Character 2
    re5 = "(\\d+)"  # Integer Number 3
    re6 = "(.)"  # Any Single Character 3
    re7 = "(\\d+)"  # Integer Number 4

    rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7, re.IGNORECASE | re.DOTALL)
    m = rg.search(txt)
    if m:
        int1 = m.group(1)
        c1 = m.group(2)
        int2 = m.group(3)
        c2 = m.group(4)
        int3 = m.group(5)
        c3 = m.group(6)
        int4 = m.group(7)
        return (
            str(int1) + str(c1) + str(int2) + str(c2) + str(int3) + str(c3) + str(int4)
        )
    else:
        return None


def find_Ping_Regex(txt):
    re1 = "(\\d{2})"  # Integer Number 1
    re2 = "(.)"  # Any Single Character 1
    re3 = "(\\d{3})"  # Integer Number 2

    rg = re.compile(re1 + re2 + re3, re.IGNORECASE | re.DOTALL)
    m = rg.search(txt)
    if m:
        int1 = m.group(1)
        c1 = m.group(2)
        int2 = m.group(3)
        return str(int1) + str(c1) + str(int2)
    else:
        return None


lineSplit = ["Testing", ("(192.168.2.4)")]
for i in lineSplit[0:]:
    mm = find_Ping_Regex(i)
    print mm
