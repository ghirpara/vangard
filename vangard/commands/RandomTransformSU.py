


from .BaseCommand import BaseCommand


class RandomTransformSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script()
