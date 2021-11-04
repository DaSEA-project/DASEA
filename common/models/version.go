package models

type Version struct {
	ID 						int64 	`json:"id"`
	VersionNumber string	`json:"version_number"`
	PackageID 		int64 	`json:"package_id"`
}