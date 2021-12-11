package models

import (
	"reflect"
	"strconv"
)

// Version defining type version
type Version struct {
	ID            int64  `json:"id"`
	PackageID     int64  `json:"package_name"`
	Version       string `json:"version"`
	Description   string `json:"description"`
	HomepageURL   string `json:"homepageUrl"`
	SourceCodeURL string `json:"sourceCodeUrl"`
	Maintainer    string `json:"maintainer"`
	License       string `json:"license"`
	Author        string `json:"author"`
}

func (v *Version) GetKeys() []string {
	keys := make([]string, 0)
	t := reflect.TypeOf(Version{})
	for i := 0; i < t.NumField(); i++ {
		keys = append(keys, t.Field(i).Name)
	}
	return keys
}

func (v *Version) GetValues() []string {
	values := make([]string, 0)
	values = append(values, strconv.Itoa(int(v.ID)))
	values = append(values, strconv.Itoa(int(v.PackageID)))
	values = append(values, v.Version)
	values = append(values, v.Description)
	values = append(values, v.HomepageURL)
	values = append(values, v.SourceCodeURL)
	values = append(values, v.Maintainer)
	values = append(values, v.License)
	values = append(values, v.Author)
	return values
}
