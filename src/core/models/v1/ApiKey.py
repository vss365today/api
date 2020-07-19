from records import Record


class ApiKey(dict):
    def __init__(self, record: Record):
        self.token: str = record["token"]
        self.desc: str = record["desc"]
        self.has_api_key: bool = bool(record["has_api_key"])
        self.has_archive: bool = bool(record["has_archive"])
        self.has_broadcast: bool = bool(record["has_broadcast"])
        self.has_host: bool = bool(record["has_host"])
        self.has_prompt: bool = bool(record["has_prompt"])
        self.has_subscription: bool = bool(record["has_subscription"])

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    def __str__(self):
        return self.token
