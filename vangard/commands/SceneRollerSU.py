


from .BaseCommand import BaseCommand


class SceneRollerSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script(args, None)
