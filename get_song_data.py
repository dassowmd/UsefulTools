import acoustid

def get_fingerprint(filepath):
   fp = acoustid.fingerprint_file(filepath)
   return fp

def lookup_fingerprint(song_fingerprint, song_duration, API_Key = 'UrmHbpV5BV'):
    res = acoustid.lookup(API_Key, song_fingerprint, song_duration)
    return res

def best_match_dict(lookup_result):
    parsed = acoustid.parse_lookup_result(lookup_result)
    high_score = 0
    res_dict = {}
    for i in parsed:
        if i[0] > high_score:
            res_dict['score'] = i[0]
            res_dict['artist'] = i[3]
            res_dict['title'] = i[2]
    return res_dict

def search_best_match(filepath):
    fp = get_fingerprint(filepath)
    lookup = lookup_fingerprint(fp[1],fp[0])
    best_match = best_match_dict(lookup)
    return  best_match