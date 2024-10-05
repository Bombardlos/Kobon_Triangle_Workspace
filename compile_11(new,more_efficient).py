from copy import deepcopy
used_faux_dicts = set()

# Function to apply swaps to a list
def apply_swaps(lst, swaps):
    for a, b in swaps:
        try:
            index = lst.index(a)
            if index < len(lst) - 1 and lst[index + 1] == b:
                lst[index], lst[index + 1] = lst[index + 1], lst[index]
        except ValueError:
            continue

# Read function title lol
def initialize_lists_and_pairs(k):
    k_minus = k - 1
    list_1 = list(range(1, k_minus + 1))
    list_2 = list(range(1, k_minus + 1))

    # Pre-populate swapped_pairs_1 and swapped_pairs_2 with initial pairs
    swapped_pairs_1 = [(i, i + 1) for i in range(1, k_minus - 1, 2)]
    swapped_pairs_2 = [(i, i + 1) for i in range(2, k_minus, 2)]
    if k_minus % 2 == 0:
        swapped_pairs_1 = [(i, i + 1) for i in range(1, k_minus, 2)]

    # Apply the prefilled swaps to list_1 and list_2
    apply_swaps(list_1, swapped_pairs_1)
    apply_swaps(list_2, swapped_pairs_2)

    return list_1, list_2

# Precompute the initial possible_pairs
def compute_possible_pairs(lst):
    return [(i, min(lst[i], lst[i + 1]), max(lst[i], lst[i + 1])) for i in range(len(lst) - 1) if lst[i] not in (lst[i+1]-1, lst[i+1]+1)]

# Function to generate the mirrored version of the selected_list
def generate_mirrored_faux_tupled(dict, k):
    a = dict[::-1]
    mirror = tuple((tuple(k - v for v in value)) for value in a)
    return mirror
# Function to generate the mirrored version of the selected_list
def generate_mirrored_faux_dict(dict, k):
    a = dict[::-1]
    mirror = [[(v if v == 0 else k - v) for v in value] for value in a]
    return mirror
# Function to generate the mirrored version of the selected_list
def generate_mirrored_list(selected_list, k):
    return [k - x for x in reversed(selected_list)]

# True if NOT sequential ascending
def sequential_test(pair):
    return pair[0] + 1 != pair[1]

# Test if the swap made a triangle
def triangle_test(fauxdict, pair):
    return fauxdict[pair[0] - 1][-1] == fauxdict[pair[1] - 1][-1]

# Test if the necessary secondary swaps are both valid
def secondary_pair_test(fauxdict, all_swapped, pair1, pair2):
    a = sequential_test(pair1)
    b = sequential_test(pair2)
    c = triangle_test(fauxdict, pair1)
    d = triangle_test(fauxdict, pair2)
    e = not(pair1 in all_swapped or pair2 in all_swapped)
    return a and b and c and d and e

def prev_swap(selected_list, selected_fauxdict, all_swapped, all_swapped_o, swap_index, prev_pair):
    # Perform the prev swap
    selected_list[swap_index - 1], selected_list[swap_index] = selected_list[swap_index], selected_list[swap_index - 1]

    # Update fauxdict for the prev swap
    selected_fauxdict[prev_pair[0] - 1].append(prev_pair[1])
    selected_fauxdict[prev_pair[1] - 1].append(prev_pair[0])

    # Add to swapped list
    all_swapped.add(prev_pair)
    all_swapped_o.append(prev_pair)
    return

def next_swap(selected_list, selected_fauxdict, all_swapped, all_swapped_o, swap_index, next_pair):
    # Perform the next swap
    selected_list[swap_index + 1], selected_list[swap_index + 2] = selected_list[swap_index + 2], selected_list[swap_index + 1]

    # Update fauxdict for the next swap
    selected_fauxdict[next_pair[0] - 1].append(next_pair[1])
    selected_fauxdict[next_pair[1] - 1].append(next_pair[0])

    # Add to swapped list
    all_swapped.add(next_pair)
    all_swapped_o.append(next_pair)
    return

# Function to handle common logic for both first_pass and next_pass
def pass_logic(i, pair, original_list, fauxdict, all_swapped_pairs, all_swapped_ordered, recorded_passes, pass_number, k, code, upper_score, true_for_right=False):
    selected_list = original_list.copy()
    selected_fauxdict = deepcopy(fauxdict)
    all_swapped = all_swapped_pairs.copy()
    all_swapped_o = all_swapped_ordered.copy()

    swap_index = i

    # Perform the primary swap
    selected_list[swap_index], selected_list[swap_index + 1] = selected_list[swap_index + 1], selected_list[swap_index]

    # Update selected_fauxdict for the primary swap
    selected_fauxdict[pair[0] - 1].append(pair[1])
    selected_fauxdict[pair[1] - 1].append(pair[0])

    all_swapped_o.append(pair)

    # Check if the primary swap results in a triangle
    first = (min(selected_list[0], selected_list[1]), max(selected_list[0], selected_list[1]))
    last = (min(selected_list[-2], selected_list[-1]), max(selected_list[-2], selected_list[-1]))
    if first == pair or last == pair:
        return False

    # Check for secondary swaps
    prev_pair = (min(selected_list[swap_index - 1], selected_list[swap_index]),
                    max(selected_list[swap_index - 1], selected_list[swap_index]))
    next_pair = (min(selected_list[swap_index + 1], selected_list[swap_index + 2]),
                    max(selected_list[swap_index + 1], selected_list[swap_index + 2]))

    # Do secondary swaps if valid, quit if not
    if secondary_pair_test(selected_fauxdict, all_swapped, prev_pair, next_pair):
        prev_swap(selected_list, selected_fauxdict, all_swapped, all_swapped_o, swap_index, prev_pair)
        next_swap(selected_list, selected_fauxdict, all_swapped, all_swapped_o, swap_index, next_pair)
    
    else:
        return False

    # Add the main swap to the set of swapped pairs
    all_swapped.add(pair)

    # Record the turn data, checking for mirrored sets
    record_pass(selected_list, all_swapped, all_swapped_o, selected_fauxdict, recorded_passes, pass_number, k, code, upper_score, true_for_right=true_for_right)
    return True

# Function to record each pass, while preventing mirrored sets
def record_pass(selected_list, all_swapped, all_swapped_ordered, selected_fauxdict, recorded_passes, pass_number, k, code, upper_score, true_for_right=False):
    fauxdict_tupled = tuple((tuple(value)) for value in selected_fauxdict)

    before_len = len(used_faux_dicts)
    used_faux_dicts.add(fauxdict_tupled)
    after_len = len(used_faux_dicts)

    if before_len != after_len:
        # Record the pass with its pass number
        recorded_passes.append({
            "pass_number": pass_number,
            "code": code,
            "selected_list": selected_list,
            "all_swapped": all_swapped,
            "all_swapped_ordered": all_swapped_ordered,
            "selected_fauxdict": selected_fauxdict,
            "upper_score": upper_score
        })

        # FLAWED, MISSES SOME MIRRORS FOR LEFT
        """
        if true_for_right:
            # Record the pass with its pass number
            mirrored_dict = generate_mirrored_faux_dict(selected_fauxdict, k)
            mirrired_dict_tupled = tuple((tuple(value)) for value in mirrored_dict)
            used_faux_dicts.add(mirrired_dict_tupled)

            new_pairs = []
            for pair in all_swapped_ordered:
                new_pair = (k - pair[1], k - pair[0])
                new_pairs.append(new_pair)

            recorded_passes.append({
                "pass_number": pass_number,
                "code": code + "m",
                "selected_list": generate_mirrored_list(selected_list, k),
                "all_swapped": set(new_pairs),
                "all_swapped_ordered": new_pairs,
                "selected_fauxdict": mirrored_dict,
                "upper_score": -upper_score
            })
        #"""

        #"""
        # Record the pass with its pass number
        mirrored_dict = generate_mirrored_faux_dict(selected_fauxdict, k)
        mirrired_dict_tupled = tuple((tuple(value)) for value in mirrored_dict)
        used_faux_dicts.add(mirrired_dict_tupled)

        new_pairs = []
        for pair in all_swapped_ordered:
            new_pair = (k - pair[1], k - pair[0])
            new_pairs.append(new_pair)

        recorded_passes.append({
            "pass_number": pass_number,
            "code": code + "m",
            "selected_list": generate_mirrored_list(selected_list, k),
            "all_swapped": set(new_pairs),
            "all_swapped_ordered": new_pairs,
            "selected_fauxdict": mirrored_dict,
            "upper_score": -upper_score
        })
        #"""

# Probably could have just combined with next_pass lol
def first_pass(k, list_2, possible_pairs, fauxdict_right, true_for_right=True):
    original_list = list_2.copy()  # Keep a copy of the original list
    all_swapped_pairs = set()      # Keep track of all swapped pairs
    all_swapped_ordered = []       # Keep track of all swapped pairs in order
    recorded_passes = []           # List to store each turn's result
    code = 0

    m = (k - 3) // 2

    for pair in possible_pairs:
        i = pair[0]
        pair = (pair[1], pair[2])
        # Ignore if pair fails sequential test
        if not sequential_test(pair):
            continue

        # Ignore bottom half
        # FLAWED WHEN NOT RECORDING MIRRORS
        # SOME STEPS ARE NEGATIVE FOR SOME TIME BEFORE EVENTUALLY TURNING POSITIVE
        # TO PROVE NO MATCH EXISTS, RECORD MIRRORS ON BOTH SIDES, THEN REMOVE MIRRORS AFTER ON ONE SIDE

        # STILL GOOD AT FINDING MATCHES, SO TRY IT ON HIGH VALUES
        if i > m:
            continue

        if i == m - 1:
            upper_score = 2
        elif i == m:
            upper_score = 0
        else:
            upper_score = 3

        # Use pass_logic for swapping
        pass_logic(i, pair, original_list, fauxdict_right, all_swapped_pairs, all_swapped_ordered, recorded_passes, 1, k, str(code), upper_score, true_for_right=true_for_right)
        code += 1

    # Return recorded passes for next_pass usage
    return recorded_passes

# Function for the subsequent passes
def next_pass(k, recorded_passes, previous_pass_number, true_for_right=False):
    new_pass_number = previous_pass_number + 1
    new_recorded_passes = []

    # Process only the passes from the previous pass
    for pass_data in recorded_passes:
        if pass_data['pass_number'] == previous_pass_number:
            selected_list = pass_data['selected_list']
            all_swapped = pass_data['all_swapped']
            all_swapped_ordered = pass_data['all_swapped_ordered']
            selected_fauxdict = pass_data['selected_fauxdict']
            prev_code = pass_data['code']
            prev_upper_score = pass_data['upper_score']

            possible_pairs = compute_possible_pairs(selected_list)

            code = 0

            for pair in possible_pairs:
                i = pair[0]
                pair = (pair[1], pair[2])
                # Ignore if pair contains 1 or k - 1, or other excluded pairs
                if pair in all_swapped:
                    continue
                
                upper_score = prev_upper_score + score_diff_lookup[i]

                # FLAWED WHEN NOT RECORDING MIRRORS
                # SOME STEPS ARE NEGATIVE FOR SOME TIME BEFORE EVENTUALLY TURNING POSITIVE
                # TO PROVE NO MATCH EXISTS, RECORD MIRRORS ON BOTH SIDES, THEN POSSIBLY REMOVE MIRRORS AFTER ON ONE SIDE

                # STILL GOOD AT FINDING MATCHES, SO TRY IT ON HIGH VALUES
                if upper_score < 0:
                    continue

                # Use pass_logic for swapping
                count_flag = pass_logic(i, pair, selected_list, selected_fauxdict, all_swapped, all_swapped_ordered, recorded_passes, new_pass_number, k, prev_code + "," + str(code), upper_score, true_for_right=true_for_right)
                if count_flag:
                    code += 1
    
    return recorded_passes + new_recorded_passes

# No need to use keys when using integers to begin with, but it acts like a dict
def generate_fauxdicts(k):
    fauxdict_left = [[] for _ in range(k - 1)]  # Create a list of empty lists
    fauxdict_right = [[] for _ in range(k - 1)]
    fauxdicts = [fauxdict_left, fauxdict_right]
    kmod = k % 2

    # Populate fauxdict_left
    for i in range(1, k - 1, 2):
        fauxdict_left[i - 1].append(i + 1)
        fauxdict_left[i].append(i)

    # Special case 0's
    fauxdict_right[0].append(0) 
    fauxdicts[kmod][k - 2].append(0)

    for i in range(2, k - kmod, 2):
        fauxdict_right[i - 1].append(i + 1)
        fauxdict_right[i].append(i)

    return fauxdict_left, fauxdict_right

# Creates the arrangements, makes records
def kobon_arrange(line_count, true_for_right=True):
    l1, l2 = initialize_lists_and_pairs(line_count)
    fauxdict_left, fauxdict_right = generate_fauxdicts(line_count)
    p1, p2 = compute_possible_pairs(l1), compute_possible_pairs(l2)

    # Choose left or right
    if true_for_right:
        line_list = l2
        fauxdict = fauxdict_right
        pairs = p2
    else:
        line_list = l1
        fauxdict = fauxdict_left
        pairs = p1

    # Perform first pass and record the results
    recorded_passes = first_pass(line_count, line_list.copy(), pairs.copy(), deepcopy(fauxdict), true_for_right=true_for_right)
    past_length = len(recorded_passes)

    # Use recorded data for the next passes
    i = 1
    while True:
        recorded_passes = next_pass(line_count, recorded_passes, previous_pass_number=i, true_for_right=true_for_right)
        current_length = len(recorded_passes)
        if current_length == past_length:
            break
        past_length = current_length
        i += 1
    
    return recorded_passes

# Search for entries where the swaps don't overlap and reach the max amount
def match_records(k):
    m = (k - 3) // 2
    global score_diff_lookup
    # Precompute score differences for all possible i values
    score_diff_lookup = {}
    for i in range(k):  # Assuming i ranges from 0 to k-1
        if i < m - 1:
            score_diff_lookup[i] = 3
        elif i == m - 1:
            score_diff_lookup[i] = 2
        elif i == m:
            score_diff_lookup[i] = 0
        elif i == m + 1:
            score_diff_lookup[i] = -2
        else:
            score_diff_lookup[i] = -3



    max_length = ((k - 2)*(k - 3)) // 2
    half_length = max_length // 2
    if k % 2 == 1:
        half_length = max_length
    print("RIGHT")
    right_records = kobon_arrange(k, true_for_right=True)
    print("")
    print("")
    print("")
    print("LEFT")
    left_records = kobon_arrange(k, true_for_right=False)
    print("")
    print("")
    print("")
    print("CHECKING FOR MATCHES...")
    matched_records = {}

    sorted_recorded_passes = [[] for _ in range(max_length + 1)]

    for record in left_records:
        swap_len = len(record["all_swapped"])
        sorted_recorded_passes[swap_len].append(record)

    left_records = sorted_recorded_passes

    # Iterate over each record from the right side
    for right_record in right_records:
        right_swapped_pairs = right_record["all_swapped"]
        len_right_swapped_pairs = len(right_swapped_pairs)
        matched_records[right_record["code"]] = []

        left_swap_length_required = half_length - len_right_swapped_pairs
        # Compare with each left-side record
        left_records_subset = left_records[left_swap_length_required]

        # Compare with each left-side record
        for left_record in left_records_subset:
            left_swapped_pairs = left_record["all_swapped"]

            # Check if there is no overlap in swapped pairs
            if right_swapped_pairs.isdisjoint(left_swapped_pairs):

                # Add the record
                matched_records[right_record["code"]].append(right_record)
                matched_records[right_record["code"]].append(left_record)

    # Remove records with no matches
    matched_records = {key: value for key, value in matched_records.items() if value}

    return matched_records

matches = match_records(11)
print(matches)
print(" ")

#"""
if matches:
    total = 0
    print("MATCHES FOUND:")
    for key, value in matches.items():
        print("RIGHT:")
        for k, v in value[0].items():
            print(f"{k}: {v}")
        print("-")
        print("LEFT:")
        for k, v in value[1].items():
            print(f"{k}: {v}")
        print("-")
        print("ARRANGEMENT:")
        swap_left = value[1]["all_swapped_ordered"][::-1]
        swap_right = value[0]["all_swapped_ordered"]
        print(swap_left + [0] + swap_right)
        print(" ")
        print(" ")
        total += 1
    print(total)
#"""

if not matches:
    print("NO MATCHES FOUND")
