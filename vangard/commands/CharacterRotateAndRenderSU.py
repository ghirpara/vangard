


from .BaseCommand import BaseCommand


class CharacterRotateAndRenderSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script(args, None)
