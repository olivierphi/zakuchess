from django_unicorn.components import UnicornView


class ChessBoardView(UnicornView):
    name = "World"
    counter = 1

    def increment_counter(self):
        self.counter += 1

    def clear_name(self):
        self.name = ""
