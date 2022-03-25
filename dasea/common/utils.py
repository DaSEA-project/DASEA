# Write array to csv
def _serialize_data(lst, outfile):
    # Add header row
    rows = [lst[0].to_csv_header()]
    rows += [el.to_csv() for el in lst]
    with open(outfile, "w") as fp:
        for line in rows:
            print(line, file=fp)

# Write one line or more to a csv
def _serialize_data_rows(lst, outfile):
    rows = []
    rows += [el.to_csv() for el in lst]
    with open(outfile, "a+") as fp:
        if fp.tell() == 0:
            head = lst[0].to_csv_header()
            print(head, file=fp)
        for line in rows:
            print(line, file=fp)

