def two_numbers(numbers:list[int],target):
    for i in range(len(numbers) - 1):
        other_num = target - numbers[i]
        for j in range(i+1, len(numbers)):
            if numbers[j] == other_num:
                return (i,j)
    return None

def find_two(numbers:list[int], target) -> tuple[int,int] | None:
    seen = dict[int,int] = {0}
    for i in range(len(numbers)):
        other_num = target - numbers[i]
        if other_num in seen:
            return (i, seen[other_num])
        seen.add((i, numbers[i]))
    return None

def find_single_letter(input_string: str) -> int:
    letter_occurrences: dict[str, int] = {}
    for ch in input_string:
        if ch in letter_occurrences:
            letter_occurrences[ch] += 1
        else:
            letter_occurrences[ch] = 1
    for index, char in enumerate(input_string):
        if letter_occurrences[char] == 1:
            return index
    return -1

def sliding_window(input_string: str) -> int:
    left = 0
    string_set: set[str] = ()
    max_length = 0

    for i, ch in enumerate(input_string):
        right = i
        while ch in string_set:
            string_set.remove(input_string[left])
            left += 1

        string_set.add(ch)
        current_length = right - left + 1
        if current_length > max_length:
            max_length = current_length
            
    return max_length
        
        

