import json
from pathlib import Path
import os.path
import time

def process_product_list_reset(target_file):
    Path.unlink(target_file)

def process_product_list(target_file):

    n=30
    while not os.path.exists(target_file):
        time.sleep(1)
        n=n-1
        if n == 0:
            print (f"ERROR: Unable to locate output file: {target_file}")
            return

    content = json.load(open(target_file, 'r'))

    fmt=" %-8s %-16s %-64s"

    print(fmt % ("Token", "Store", "Title"))
    print(fmt % (''.join('-' for _ in range(8)), ''.join('-' for _ in range(16)), ''.join('-' for _ in range(32))))

    for item in content:
        title=item['title']
        store=item['store']
        token=item['token']
        store_guid=item['guid']

        print(fmt % (token, store, title))
