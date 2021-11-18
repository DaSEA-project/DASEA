package models

// Version defining type version
type Version struct {
	ID        int64  `json:"id"`
	PackageID int64  `json:"package_name"`
	Version   string `json:"version"`
}
