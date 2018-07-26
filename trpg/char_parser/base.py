class CharParser(object):
    def __init__(self):
        self.details = {
            'name': 'Char Name',
            'player': 'Unknown Player'
        }

    def parse(self, text):
        raise NotImplementedError()
