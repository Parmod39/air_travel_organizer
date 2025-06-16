class SuggestionStrategy:
    def suggest(self, manager, **kwargs):
        raise NotImplementedError("Must override suggest method")
