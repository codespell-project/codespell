class DFA:
    def __init__(self):
        self.states = {'q0', 'q1'}
        self.alphabet = {'a', 'b'}
        self.transitions = {
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q0', 'b': 'q1'}
        }
        self.start_state = 'q0'
        self.accept_states = {'q0'}

    def is_valid_string(self, input_string):
        current_state = self.start_state
        for char in input_string:
            if char not in self.alphabet:
                return False
            current_state = self.transitions[current_state][char]
        return current_state in self.accept_states

# Example usage:
dfa = DFA()

# Test some strings
print(dfa.is_valid_string("ab"))  # True (even number of 'a's)
print(dfa.is_valid_string("aab"))  # False (odd number of 'a's)
print(dfa.is_valid_string("bb"))  # True (even number of 'a's, none in this case)
print(dfa.is_valid_string("baab"))  # False (odd number of 'a's)

