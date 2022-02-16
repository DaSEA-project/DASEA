from glob import glob
from pathlib import Path
from dasea.miners.cargo import mine


DATA_DIR = "data/out/cargo/"


def test_cargo_end_to_end():
    mine()
    glob_pattern = str(Path(DATA_DIR, "*.csv"))
    generated_files = glob(glob_pattern)
    fnames = [Path(f).stem for f in generated_files]

    file_kind = set([f.split("_")[1] for f in fnames])
    assert file_kind == set(["packages", "versions", "dependencies"])
