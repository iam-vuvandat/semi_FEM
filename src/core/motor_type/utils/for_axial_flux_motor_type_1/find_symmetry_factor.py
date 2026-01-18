import math

def simplify_fraction(a, b):
    k = math.gcd(int(a), int(b))
    return a // k, b // k, k

class Output:
    def __init__(self,
                 symmetry_factor = None,
                 slot_reduced = None,
                 pole_reduced = None):
        self.symmetry_factor = symmetry_factor
        self.slot_reduced = slot_reduced
        self.pole_reduced = pole_reduced

def find_symmetry_factor(motor):
    slot_number = motor.slot_number
    pole_number = motor.pole_number
    pole_pair_number = pole_number/2
    slot_reduced,pole_pair_reduced,symmetry_factor = simplify_fraction(slot_number,pole_pair_number)
    pole_reduced = pole_pair_reduced * 2
    return Output(symmetry_factor=symmetry_factor,
                  slot_reduced= slot_reduced,
                  pole_reduced= pole_reduced)

if __name__ == "__main__":
    def test():
        a = 14
        b = 7
        a,b,k = simplify_fraction(a=a,b=b)
        print(a,b,k)
    test()