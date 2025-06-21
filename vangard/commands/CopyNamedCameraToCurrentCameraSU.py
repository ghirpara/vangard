


from .BaseCommand import BaseCommand


class CopyNamedCameraToCurrentCameraSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script(args, None)




    
