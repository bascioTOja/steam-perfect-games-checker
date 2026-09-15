from achievement import Achievement


class Game:
    def __init__(self, app_id:str, game_name:str, achievements: list[dict]):
        self.app_id: str = app_id
        self.game_name: str = game_name
        self.achievements: list[Achievement] = self._craft_achievements(achievements)
        self.perfect: bool = self.check_perfect()

    def _craft_achievements(self, raw_achievements):
        if raw_achievements is None:
            return []

        return [Achievement(
            apiname=achievement.get('apiname', ''),
            achieved=achievement.get('achieved', False),
            unlocktime=achievement.get('unlocktime', 0),
            name=achievement.get('name', achievement.get('apiname', '')),
            description=achievement.get('description', ''),
        ) for achievement in raw_achievements]

    def check_perfect(self):
        if len(self.achievements) == 0:
            return False

        for achievement in self.achievements:
            if not achievement.achieved:
                return False
        return True

    def get_not_unlocked_achievements(self):
        return [achievement for achievement in self.achievements if not achievement.achieved]