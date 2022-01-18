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
	return values
}
