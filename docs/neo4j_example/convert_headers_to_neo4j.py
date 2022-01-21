import numpy as np
import pandas as pd

# https://neo4j.com/developer/guide-import-csv/

pkg_df = pd.read_csv("data/alire_packages_01-14-2022.csv")
ver_df = pd.read_csv("data/alire_versions_01-14-2022.csv")
dep_df = pd.read_csv("data/alire_dependencies_01-14-2022.csv")

ver_df.dropna(subset=["pkg_idx"], inplace=True)
ver_df.pkg_idx = ver_df.pkg_idx.astype(np.uint)

dep_df.dropna(subset=["pkg_idx", "target_idx"], inplace=True)
dep_df.pkg_idx = dep_df.pkg_idx.astype(np.uint)
dep_df.target_idx = dep_df.target_idx.astype(np.uint)

instance_rel_df = ver_df[["idx", "pkg_idx"]].copy()
instance_rel_df.rename(columns={"idx": ":START_ID(Version)", "pkg_idx": ":END_ID(Package)"}, inplace=True)

pkg_df.rename(columns={"idx": "pkgId:ID(Package)"}, inplace=True)
ver_df.rename(columns={"idx": "verId:ID(Version)"}, inplace=True)
dep_df.rename(columns={"source_idx": "verId:START_ID(Version)", "target_idx": "pkgId:END_ID(Package)"}, inplace=True)

pkg_df.to_csv("data/alire_packages_neo4j.csv", index=False)
ver_df.to_csv("data/alire_versions_neo4j.csv", index=False)
dep_df.to_csv("data/alire_dependencies_neo4j.csv", index=False)
instance_rel_df.to_csv("data/alire_instancerels_neo4j.csv", index=False)
