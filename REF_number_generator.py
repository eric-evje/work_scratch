# Quick function to generate a list of unique 5 place hex value for the part number index
# If further ref numbers are required, please run the program. Do not change the seed
# Find the ending value of the current part number index list, and append further values

import random
import csv

def main():
    random.seed(10)
    sample_range = range(65536, 1048575)
    REF = random.sample(sample_range, 5000)

    output_file = "REF_numbers_2.txt"

    with open(output_file, 'w') as o:
        index = 0
        for line in REF:
            index += 1
            line_str = str(hex(line))[2:].upper()
            if len(line_str) == 5:
                print(str(index) + ", " + line_str)
                o.write(str(index) + ", " + line_str + "\n")
            else:
                print("Not 5 digits {}".format(line_strs))


if __name__ == '__main__':
    main()

