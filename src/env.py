class can_env(object):
    _env = {}

    def add(self, func, name, n_args) -> None:
        self._env[name] = [func, n_args]


def Cantonesetype(args):
    var = args[0]
    print(type(var))
    return type(var)

Env = can_env()
Env.add(Cantonesetype, "type", 1)