from namespace import Namespace

class Era(object):
    def __init__(self):
        self.lumberjack = self.GameUnit()
        self.warrior = self.CombatUnit()
        self.shooter = self.RangedUnit()

class MedievalAge(Era):
    __metaclass__ = Namespace()
    class GameUnit(object):
        def move(self): return "Medieval.GameUnit.move()"
    class CombatUnit(GameUnit):
        def fight(self): return "Medieval.CombatUnit.fight()"
    class RangedUnit(CombatUnit):
        def aim(self): return "Medieval.RangedUnit.aim()"

class ColonialAge(Era):
    __metaclass__ = Namespace(MedievalAge)
    class CombatUnit:
        def fight(self): return "ColonialAge.CombatUnit.fight()"

class IndustrialAge(Era):
    __metaclass__ = Namespace(ColonialAge)
    class GameUnit:
        def move(self): return "IndustrialAge.GameUnit.move()"
    class RangedUnit:
        def aim(self): return "IndustrialAge.RangedUnit.aim()"


if __name__ == '__main__':
    for era in MedievalAge(), ColonialAge(), IndustrialAge():
        for player in era.lumberjack, era.warrior, era.shooter:
            for action in "move", "fight", "aim":
                try: result = getattr(player,action)()
                except AttributeError:
                    result = "N/A"
                print "%s:%s.%s:\t%s" % (type(era).__name__,
                                         type(player).__name__,
                                         action, result)
