
import os
import json
import time
import glob
from pathlib import Path
import itertools

from .BaseCommand import BaseCommand

class RandomizedLoraTrainingSetGeneratorSU(BaseCommand):
     
     # A dummy function to show what's being called
    def do_render(pose, expr, cam):
        """A sample function that takes a pose, an expression, and a camera."""
        print(f"Rendering -> Pose: {pose}, Expression: '{expr}', Camera: '{cam}'")

    def process(self, args):
        super().process(args)


        # 1. Compute the scene file list from the specified glob file pattern 
        scene_files = glob.glob(args.scene_files)

        # 2. Fetch the trainer config file 
        lora_trainer_config = json.load(open(args.lora_trainer_config))

        orders      = lora_trainer_config['ordering']
        poses       = lora_trainer_config['poses']     
        expressions = lora_trainer_config['expressions']     
        cameras     = lora_trainer_config['cameras']     
        data_map = {
            'p': poses,
            'e': expressions,
            'c': cameras
        }

        # 3. Create a list of the iterables in the desired order
        # This uses a list comprehension to look up each item from 'orders' in our map.
        # If orders = ['p', 'e', 'c'], this becomes [poses, exprs, cams]
        iterables_in_order = [data_map[key] for key in orders]


        for scene_file in scene_files:

            # 4. Load a scene file 
            self.exec_remote_script('LoadMergeSU', {'scene-file': scene_file, 'merge': False});


            # 4. Generate all combinations and call the function
            # itertools.product is equivalent to nested for-loops.
            # The * unpacks the list into arguments: product(poses, exprs, cams)
            for combination in itertools.product(*iterables_in_order):
                # 'combination' is a tuple, e.g., (1, 'a', 'W')
                # The order of items in the tuple matches the 'orders' list.
                
                # Create a dictionary to map the order key to its value for this combination
                # e.g., if orders=['p','e','c'], this becomes {'p': 1, 'e': 'a', 'c': 'W'}
                arg_map = dict(zip(orders, combination))
                
                # Call the function by looking up the arguments by their required names
                self.do_render(
                    pose=arg_map['p'], 
                    expr=arg_map['e'], 
                    cam=arg_map['c']
                )
