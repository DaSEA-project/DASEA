package models

// Version defining type version
type Version struct {
	Version string `json:"version"`
}

type CsvVersion struct {
	ID        int64 `json:"id"`
	PackageID int64 `json:"package_name"`
	Version
}
