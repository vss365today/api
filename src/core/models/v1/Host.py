from records import Record


class Host(dict):
    def __init__(self, record: Record):
        self.id: str = record["uid"]
        self.handle: str = record["handle"]
        self.url: str = self.make_url(record["handle"])

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    @staticmethod
    def make_url(writer_handle: str) -> str:
        return f"https://twitter.com/{writer_handle}"
