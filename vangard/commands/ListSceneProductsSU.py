
import os
import json
import time
from pathlib import Path

from .BaseCommand import BaseCommand

class ListSceneProductsSU(BaseCommand):

    def process_product_list_reset(target_file):
        print (f"Attempt to unlink file {target_file}")
        
        if (os.path.exists(target_file)):
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


    def process(self, args):
        super().process(args)

        target_file = args['target_file']

        self.process_product_list(target_file)
        
        self.exec_default_script(args, None)

        self.process_product_list_reset(target_file)