from .types import BaseNode


class EventEngineCls:
    def __init__(self):
        self.__function_maps = {}

    def group(self, group_markers: list[BaseNode]):
        pass

    def goto(self, group_markers: list[BaseNode], *args):
        pass
