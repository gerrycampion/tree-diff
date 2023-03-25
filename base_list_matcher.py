from abc import abstractmethod


class BaseListMatcher:
    @classmethod
    @abstractmethod
    def match_lists(base, compare):
        pass
