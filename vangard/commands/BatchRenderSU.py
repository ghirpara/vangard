


from .BaseCommand import BaseCommand
from vangard.UserFunctions import extract_glob_to_list


class BatchRenderSU(BaseCommand):

    def process(self, args):
        super().process(args)

        glob_list = extract_glob_to_list(args.scene_files)
        args.scene_files = glob_list
        
        self.exec_default_script()

    
