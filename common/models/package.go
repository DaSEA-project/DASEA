package models

type Package struct {
	ID          		int64     `json:"id"`
	Name        		string    `json:"name"`
	PackageManager 	string		`json:"package_manager"`
	Platform 				string    `json:"platform"`
	Description 		string  	`json:"description"`
	HomepageURL 		string 		`json:"homepageUrl"`
	SourceCodeURL		string 		`json:"sourceCodeUrl"`
	Maintainer 			string 		`json:"maintainer"`
	License 				string 		`json:"license"`
	Author 					string 		`json:"author"`
}