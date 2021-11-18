package models

import (
	"reflect"
	"strconv"
)

// Package defining type package
type Package struct {
	ID             int64  `json:"id"`
	Name           string `json:"name"`
	PackageManager string `json:"package_manager"`
	Platform       string `json:"platform"`
	Description    string `json:"description"`
	HomepageURL    string `json:"homepageUrl"`
	SourceCodeURL  string `json:"sourceCodeUrl"`
	Maintainer     string `json:"maintainer"`
	License        string `json:"license"`
	Author         string `json:"author"`
}

func (p *Package) GetKeys() []string {
	keys := make([]string, 0)
	t := reflect.TypeOf(Package{})
	for i := 0; i < t.NumField(); i++ {
		keys = append(keys, t.Field(i).Name)
	}
	return keys
}

func (p *Package) GetValues() []string {
	values := make([]string, 0)
	values = append(values, strconv.Itoa(int(p.ID)))
	values = append(values, p.Name)
	values = append(values, p.PackageManager)
	values = append(values, p.Platform)
	values = append(values, p.Description)
	values = append(values, p.HomepageURL)
	values = append(values, p.SourceCodeURL)
	values = append(values, p.Maintainer)
	values = append(values, p.License)
	values = append(values, p.Author)

	return values
}
