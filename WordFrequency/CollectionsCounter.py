from collections import Counter

strs = input("Please enter the text you would like counted\n")
count = Counter(strs.lower().split())
print(count)
