import random
from collections import defaultdict
from faker import Faker

# Run this in your terminal to install Faker if you don't have it: pip install faker

# Generates 'n' unique names using the provided generator function 'gen'
def generate_unique_with_suffix(gen, n):
    used = set()
    counts = defaultdict(int)
    out = []

    while len(out) < n:
        base = gen()
        counts[base] += 1

        # First time -> no suffix; later -> add counter
        cand = base if counts[base] == 1 else f"{base}{counts[base]}"

        used.add(cand)
        out.append(cand)

    return out

if __name__ == "__main__":
    # Set # of names to generate
    num_names = 10000

    # Instantiate 'Faker` object
    fake = Faker()

    # Generate and validate "knight" names
    knight_names = generate_unique_with_suffix(fake.first_name_male, num_names)
    assert all('\t' not in n and '\n' not in n and '\r' not in n for n in knight_names), "knight names have tabs/newlines"

    # Generate and validate "lady" names
    lady_names = generate_unique_with_suffix(fake.first_name_female, num_names)
    assert all('\t' not in n and '\n' not in n and '\r' not in n for n in lady_names), "lady names have tabs/newlines"

    # Create dictionaries
    knight_to_lady = {}
    lady_to_knight = {}

    # Shuffle the lady and knight names
    shuffled_lady_names = list(lady_names)
    shuffled_knight_names = list(knight_names)

    # Populate the dictionaries
    for knight_name in knight_names:
        random.shuffle(shuffled_lady_names)
        knight_to_lady[knight_name] = shuffled_lady_names.copy() 

    for lady_name in lady_names:
        random.shuffle(shuffled_knight_names)
        lady_to_knight[lady_name] = shuffled_knight_names.copy() 

    # Write to file
    with open(f"marriage_inputs_10000.txt", "w", encoding="latin-1") as f:
        # Write # of names
        f.write(f"{num_names}\n")

        # Write knight_to_lady dictionary
        for knight, ladys in knight_to_lady.items():
            assert len(ladys) == num_names, f"Mismatch in number of ladys for {knight}"
            f.write(f"{knight}\t{'\t'.join(ladys)}\n")

        # Write lady_to_knight dictionary
        for lady, knights in lady_to_knight.items():
            assert len(knights) == num_names, f"Mismatch in number of knights for {lady}"
            f.write(f"{lady}\t{'\t'.join(knights)}\n")