from abc import abstractmethod

class Matcher:
    @abstractmethod
    def match(self, request: str, choices, default: str = "") -> str:
        pass

class StringMatcher(Matcher):
    """
    Simply finds the first choice explicitly mentioned in a request
    """
    def match(self, request: str, choices: list[str], default: str = "") -> str:
        for choice in choices:
            if choice in request:
                return choice
        return default
