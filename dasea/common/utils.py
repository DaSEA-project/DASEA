def _serialize_data(lst, outfile):
    # Add header row
    rows = [lst[0].to_csv_header()]
    rows += [el.to_csv() for el in lst]
    with open(outfile, "w") as fp:
        for line in rows:
            print(line, file=fp)