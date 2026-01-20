
import random

def test_cycle(count=20):
    golden_ratio = 0.618033988749895
    hue_start = 0
    hue_range = 360
    
    # Simulate the code in generator.py
    phase_shift = random.random()
    
    print(f"Phase Shift: {phase_shift}")
    
    seen = []
    
    for i in range(count):
        step_fraction = (i * golden_ratio + phase_shift) % 1.0
        hue_degrees = hue_start + (hue_range * step_fraction)
        
        # Quantize to integer to see if it makes a difference?
        hue_int = int(hue_degrees)
        print(f"i={i}: Hue={hue_degrees:.2f} (Int: {hue_int})")
        seen.append(hue_int)

    # Check for cycles
    # Simplistic check: if seen[i] == seen[i+6] for multiple i
    # But Golden Ratio is non-repeating.
    
if __name__ == "__main__":
    test_cycle(20)
