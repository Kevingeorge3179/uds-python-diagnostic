from dataclasses import dataclass, field

@dataclass
class Result:

    ok : bool
    kind : str
    message : str
    nrc : int | None = None
    fields : dict = field(default_factory=dict)
