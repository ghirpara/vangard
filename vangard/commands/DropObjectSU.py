


from .BaseCommand import BaseCommand


class DropObjectSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script(args, None)
