import datetime


class Restaurant:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self._times = []
        self._avg_seconds = None

    def get_average_time(self):
        # Set to none by add_time()
        # allows caching of average time
        if self._avg_seconds is None:
            avg_seconds = sum(self._times) / len(self._times)
        return avg_seconds

    def add_time(self, timestamp_str):
        self._times.append(convert_from_timestamp(timestamp_str))
        self._avg_seconds = None

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{count} | {name} | {avg}\n\t{times}\n".format(
            count=len(self._times),
            name=self.name,
            avg=format_seconds(self.get_average_time()),
            times=", ".join(map(lambda time: format_seconds(time), self._times)),
        )


def convert_from_timestamp(timestamp_str):
    dt_obj = datetime.datetime.fromtimestamp(int(float(timestamp_str)))
    hour = dt_obj.hour
    minutes = dt_obj.minute
    seconds = dt_obj.second
    return hour*3600 + minutes*60 + seconds


# format seconds to 12 hours format
# Ex. 49204 => '1:40:04 P.M.'
def format_seconds(sec):
    # Ex. td = "11:52:12"
    td = str(datetime.timedelta(seconds=sec))
    td_split = td.split(":")
    (hours, minutes, seconds) = (int(td_split[0]), int(td_split[1]), int(td_split[2]))
    if hours >= 12:
        period = " P.M."
    else:
        period = " A.M."
    if hours > 12:
        hours -= 12
        td = str(hours) + td[2:]
    if hours == 0:
        hours = 12
    return td + period