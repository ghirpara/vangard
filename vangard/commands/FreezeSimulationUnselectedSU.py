


from .BaseCommand import BaseCommand


class FreezeSimulationUnselectedSU(BaseCommand):

    def process(self, args):
        super().process(args)
        self.exec_default_script()