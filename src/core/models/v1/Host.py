from records import Record


class Host(dict):
    def __init__(self, record: Record):
        self.id: str = record["uid"]
        self.handle: str = record["handle"]
        self.url: str = self.make_url(record["handle"])

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    @staticmethod
    def make_url(handle: str) -> str:
        """Create a Twitter URL to the Host's profile."""
        return f"https://twitter.com/{handle}"
