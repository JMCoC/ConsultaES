from dataclasses import dataclass


@dataclass
class DFA:
    states: set[str]
    alphabet: set[str]
    delta: dict[tuple[str, str], str]
    start: str
    finals: set[str]

    def longest_match(self, s: str, pos: int = 0) -> int:
        state = self.start
        last_final = 0
        for i, ch in enumerate(s[pos:], start=1):
            key = (state, ch)
            if key not in self.delta:
                break
            state = self.delta[key]
            if state in self.finals:
                last_final = i
        return last_final
