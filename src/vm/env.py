class can_env(object):
    _env = {}

    def add(self, func, name, n_args) -> None:
        self._env[name] = [func, n_args]


def Cantonesetype(args):
    var = args[0]
    print(type(var))
    return type(var)

def CantoneseInput(args):
    assert len(args) == 1
    return input(args[0])

Env = can_env()
Env.add(Cantonesetype, "type", 1)
Env.add(CantoneseInput, "input", 1)