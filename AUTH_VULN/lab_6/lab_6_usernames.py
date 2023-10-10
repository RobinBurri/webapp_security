import sys


def create_name_list(name1, name2, position, list_length):
    # Split the input file name and extension
    output_file = "usernamelist.txt"

    with open(output_file, "w") as outfile:
        for i in range(1, list_length):
            if (i) % position == 0:
                outfile.write(name2 + "\n")
            else:
                outfile.write(name1 + "\n")


def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <name 1> <name 2> <position> <list length>")
        sys.exit(1)

    name1 = sys.argv[1]
    name2 = sys.argv[2]
    position = int(sys.argv[3])
    list_length = int(sys.argv[4])

    create_name_list(name1, name2, position, list_length)


if __name__ == "__main__":
    main()
