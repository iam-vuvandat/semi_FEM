import math

def simplify_fraction(a, b):
    """
    Simplifies a fraction using the Greatest Common Divisor (GCD).
    Returns simplified numerator, denominator, and the GCD itself.
    """
    k = math.gcd(int(a), int(b))
    return a // k, b // k, k

class Output:
    """
    Container class for symmetry results to be returned to the main motor object.
    """
    def __init__(self,
                 symmetry_factor = None,
                 slot_reduced = None,
                 pole_reduced = None):
        self.symmetry_factor = symmetry_factor
        self.slot_reduced = slot_reduced
        self.pole_reduced = pole_reduced

def find_symmetry_factor(motor):
    """
    Calculates the machine symmetry factor (periodicity) based on Slot and Pole numbers.
    Accesses variables through the new nested geometry_data structure.
    """
    # Accessing parameters through the refactored nested structure
    stator = motor.geometry_data.stator
    rotor  = motor.geometry_data.rotor

    slot_number = stator.slot_number # Located in stator container
    pole_number = rotor.pole_number  # Located in rotor container
    
    # Mathematical logic remains strictly identical
    pole_pair_number = pole_number / 2
    
    # Find GCD and reduced values using simplify_fraction logic
    slot_reduced, pole_pair_reduced, symmetry_factor = simplify_fraction(slot_number, pole_pair_number)
    
    pole_reduced = pole_pair_reduced * 2
    
    return Output(symmetry_factor=symmetry_factor,
                  slot_reduced=slot_reduced,
                  pole_reduced=pole_reduced)

if __name__ == "__main__":
    def test():
        # Example test case
        a = 14
        b = 7
        a_red, b_red, k = simplify_fraction(a=a, b=b)
        print(f"Numerator: {a_red}, Denominator: {b_red}, GCD: {k}")
    test()