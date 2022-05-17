



def mine():
    f = open("data/tmp/ubuntu/apt-cache_dump.txt", "r")
    raw_lines = list(f)
    while not raw_lines[0].startswith("Package"):
        raw_lines.pop(0)

    packages = []
    i = 0
    while raw_lines:
        i += 1
        if i % 10000 == 0:
            print(i)
        line = raw_lines.pop(0).strip()
        if line.startswith("Package:"):
            package = line.split(":")[1].strip()
            packages.append(package)

    print(len(packages))

    





if __name__ == "__main__":
    mine()