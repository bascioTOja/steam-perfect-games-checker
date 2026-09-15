class Achievement:
    def __init__(self,  apiname, achieved, unlocktime, name, description):
        self.apiname = apiname
        self.achieved = achieved
        self.unlocktime = unlocktime
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description} ({"achieved" if self.achieved else "not achieved"})"