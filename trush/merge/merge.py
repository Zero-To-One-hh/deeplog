def combine_lines(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        numbers = []
        for line in infile:
            numbers.extend(line.split())
        outfile.write(' '.join(numbers))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Combine lines of numbers into one line")
    parser.add_argument('input_file', type=str, help='Input file with multiple lines of numbers')
    parser.add_argument('output_file', type=str, help='Output file with numbers in one line')
    args = parser.parse_args()

    combine_lines(args.input_file, args.output_file)
