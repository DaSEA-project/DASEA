def _serialize_data(lst, outfile):
    # Add header row
    rows = [lst[0].to_csv_header()]
    rows += [el.to_csv() for el in lst]
    with open(outfile, "w") as fp:
        for line in rows:
            print(line, file=fp)


# def _serialize_packages(packages_lst):


# def _serialize_versions(versions_lst):
#     version_rows = [versions_lst[0].to_csv_header()]
#     version_rows += [v.to_csv() for v in versions_lst]
#     with open(VERSIONS_FILE, "w") as fp:
#         for line in version_rows:
#             print(line, file=fp)


# def _serialize_dependencies(deps_lst):
#     deps_rows = [deps_lst[0].to_csv_header()]
#     deps_rows += [d.to_csv() for d in deps_lst]
#     with open(DEPS_FILE, "w") as fp:
#         for line in deps_rows:
#             print(line, file=fp)
