


from .BaseCommand import BaseCommand


class CopyTransformObjectSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script()
