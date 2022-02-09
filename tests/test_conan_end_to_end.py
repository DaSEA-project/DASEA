from glob import glob
from pathlib import Path
from core.conan import mine


DATA_DIR = "data/out/conan/"


def test_conan_end_to_end():
    mine()
    glob_pattern = str(Path(DATA_DIR, "*.csv"))
    generated_files = glob(glob_pattern)
    fnames = [Path(f).stem for f in generated_files]

    file_kind = set([f.split("_")[1] for f in fnames])
    assert file_kind == set(["packages", "versions", "dependencies"])
