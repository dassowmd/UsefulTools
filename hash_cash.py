import string
import random
import hashlib

example_challenge = '9Kzs52jSfxa65s4df6s5a4'
def generation(challenge=example_challenge, size=25):
    answer = ''.join(random.choice(string.ascii_lowercase) +
                     random.choice(string.ascii_uppercase) +
                     random.choice(string.digits) for x in range(size))
    attempt = challenge + answer
    return attempt, answer

shaHash = hashlib.sha256()

def testAttempt():
    attempt, answer = generation()
    shaHash.update(attempt)
    solution = shaHash.hexdigest()
    return solution

for x in xrange(1,100000):
    solution = testAttempt()
    lower = 0
    upper = 3
    if solution[lower:upper] == 'af3ebab695bf674bdcda'[lower:upper]:
        print solution