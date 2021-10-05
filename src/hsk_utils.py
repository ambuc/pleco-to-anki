import csv


class HskReader():
    def __init__(self):
        self._hsks = [
            self._make_hsk_dict(1),
            self._make_hsk_dict(2),
            self._make_hsk_dict(3),
            self._make_hsk_dict(4),
            self._make_hsk_dict(5),
            self._make_hsk_dict(6),
        ]

    @staticmethod
    def _make_hsk_dict(n):
        s = set()
        csvfile = open(f"third_party/hsk_{n}.csv")
        for row in csv.reader(csvfile, delimiter=','):
            hw = row[2]
            hw = hw.split("(")[0]
            s.add(hw)
        return s

    def Has(self, hw):
        return any(hw in s for s in self._hsks)

    def InHsk(self, n, hw):
        return hw in self._hsks[n - 1]

    def GetHskLevel(self, hw):
        for i, s in enumerate(self._hsks):
            if hw in s:
                return i + 1
        return None

    def GetHskLevelPartial(self, hw):
        for i, s in enumerate(self._hsks):
            if hw in s:
                return i + 1
            for el in s:
                if hw in el:
                    return i + 1
        return None

    def GetHsk(self, n):
        return self._hsks[n - 1]

    def GetHskAndBelow(self, n):
        return set().union(*self._hsks[:n])
