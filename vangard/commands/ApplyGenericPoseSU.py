


from .BaseCommand import BaseCommand


class ApplyGenericPoseSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script(args, None)
