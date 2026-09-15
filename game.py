from achievement import Achievement


class Game:
    def __init__(self, app_id: str, game_name: str, achievements: list[dict], schema_loader=None):
        self.app_id: str = app_id
        self.game_name: str = game_name
        self.schema_loader = schema_loader
        self._schema: dict = {}
        self._schema_loaded = False
        self.achievements: list[Achievement] = self._craft_achievements(achievements)
        self.perfect: bool = self.check_perfect()

    def _craft_achievements(self, raw_achievements):
        if raw_achievements is None:
            return []

        return [Achievement(
            apiname=achievement.get('apiname', ''),
            achieved=achievement.get('achieved', False),
            unlocktime=achievement.get('unlocktime', 0),
            name=achievement.get('name'),
            description=achievement.get('description'),
        ) for achievement in raw_achievements]

    def _needs_names(self, achievements: list[Achievement]) -> bool:
        return any(not achievement.name or not achievement.description for achievement in achievements)

    def _load_schema(self) -> dict:
        if not self._schema_loaded and self.schema_loader is not None:
            self._schema = self.schema_loader(self.app_id)
            self._schema_loaded = True
        return self._schema

    def check_perfect(self):
        if len(self.achievements) == 0:
            return False

        return all(achievement.achieved for achievement in self.achievements)

    def get_not_unlocked_achievements(self):
        not_unlocked = [achievement for achievement in self.achievements if not achievement.achieved]

        if not_unlocked and self._needs_names(not_unlocked):
            schema = self._load_schema()
            for achievement in not_unlocked:
                entry = schema.get(achievement.apiname, {})
                if not achievement.name:
                    achievement.name = entry.get('displayName', achievement.apiname)
                if not achievement.description:
                    achievement.description = entry.get('description', '')

        return not_unlocked
