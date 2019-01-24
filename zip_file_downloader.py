import requests, zipfile
from io import BytesIO
from tqdm import tqdm
import math
import os

urls = [
    'https://whitmezaphotography.pixieset.com/download/filestart/?filekey=d1eb06c82c8d4fb7e7b9365c87de9cd2&fid=13928047',
    'https://whitmezaphotography.pixieset.com/download/filestart/?filekey=d1eb06c82c8d4fb7e7b9365c87de9cd2&fid=13928027',
    'https://whitmezaphotography.pixieset.com/download/filestart/?filekey=d1eb06c82c8d4fb7e7b9365c87de9cd2&fid=13928038',
    'https://whitmezaphotography.pixieset.com/download/filestart/?filekey=d1eb06c82c8d4fb7e7b9365c87de9cd2&fid=13928063'
    ]
for url in tqdm(urls):

    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0));
    block_size = 1024
    wrote = 0
    with open('output.bin', 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                         unit_scale=True):
            wrote = wrote + len(data)
            f.write(data)
    with open('output.bin', 'rb') as f:
        z = zipfile.ZipFile(BytesIO(f.read()))
        z.extractall(r'C:\Users\dasso\Desktop\Wedding Pics')
    os.remove('output.bin')
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong")