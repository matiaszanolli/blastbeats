class Settings(dict):

    instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        self._defaults = {}
        self._defaults.update(self.__dict__)
        if not Settings.instance:
            Settings.instance = self

        def __getattr__(self, name):
            return self.__dict__.get(name, None)

        def __setattr__(self, name, value):
            self.__dict__[name] = value

        def __delattr__(self, name):
            del self.__dict__[name]

        def reset(self):
            self.__dict__ = self._defaults
            return self

        def __repr__(self):
            return str(self.__dict__)

        def __str__(self):
            return str(self.__dict__)

        def __iter__(self):
            return iter(self.__dict__)

        def __len__(self):
            return len(self.__dict__)

        def __enter__(self):
            return self.instance if self.instance else self


SETTINGS = Settings({
            "MATCH_CONTEXT_SCALE": 50,
            "CURRENT_RMS": None,
            "CURRENT_RMS_COEFFICIENT": None,
            "AMPLITUDE_COEFFICIENT": None,
            "MID_FIR": None,
            "SIDE_FIR": None,
            "TARGET_MID_LOUDEST_PIECES": None,
            "TARGET_SIDE_LOUDEST_PIECES": None,
        })
