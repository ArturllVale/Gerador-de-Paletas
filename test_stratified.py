
import random

def test_stratified(count=6):
    hue_start = 0
    hue_range = 360
    
    step = hue_range / max(count, 1)
    
    slices = []
    print(f"\nGenerating {count} variations (Step size: {step:.4f}):")
    
    for k in range(count):
        slice_start = hue_start + (k * step)
        jitter = random.uniform(0, step * 0.8) 
        val = slice_start + jitter
        slices.append(val)
    
    random.shuffle(slices)
    
    # Analyze results
    slices_sorted = sorted(slices)
    min_diff = 360
    
    for i in range(len(slices_sorted)):
        val = slices_sorted[i]
        next_val = slices_sorted[(i+1)%len(slices_sorted)]
        if next_val < val: next_val += 360 # Wrap check
        diff = next_val - val
        if diff < min_diff: min_diff = diff
        
        print(f"Index {i}: {val:.2f} (Diff to next: {diff:.2f})")
        
    print(f"Min Distance between any two colors: {min_diff:.2f}")

if __name__ == "__main__":
    test_stratified(6)
    test_stratified(20)
    test_stratified(1000)
