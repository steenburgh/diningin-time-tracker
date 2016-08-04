import datetime


class Restaurant:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.unix_timestamps = []

    def add_time(self, timestamp_str):
        self.unix_timestamps.append(timestamp_str)

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{count} | {name} | {times}\n".format(
            count=len(self.unix_timestamps),
            name=self.name,
            times=str(self.unix_timestamps),
        )