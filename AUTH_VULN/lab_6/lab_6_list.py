import os
import sys


def insert_word(input_file, word_to_add, position):
    # Split the input file name and extension
    base_name, file_extension = os.path.splitext(input_file)
    output_file = (
        f"{base_name}_{position}{file_extension}"  # Create the output file name
    )

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        lines = infile.readlines()
        for i, line in enumerate(lines):
            if (i + 1) % position == 0:
                outfile.write(word_to_add + "\n")
            else:
                outfile.write(line)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input_file> <word_to_add> <position>")
        sys.exit(1)

    input_file = sys.argv[1]
    word_to_add = sys.argv[2]
    position = int(sys.argv[3])

    insert_word(input_file, word_to_add, position)
    print(f"Words inserted at every {position} positions in {input_file}_{position}")


if __name__ == "__main__":
    main()
