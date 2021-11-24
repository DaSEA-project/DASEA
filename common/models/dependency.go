package models

import (
	"reflect"
	"strconv"
)

//Dependency defining type from package to version
type CsvDependency struct {
	TargetName  string `json:"target_name"`
	Constraints string `json:"constraints"`
}

type Dependency struct {
	ID          int64  `json:"id"`
	SourceID    int64  `json:"source_id"`
	TargetID    int64  `json:"target_id"`
	Constraints string `json:"constraints"`
}

func (d *Dependency) GetKeys() []string {
	keys := make([]string, 0)
	t := reflect.TypeOf(Dependency{})
	for i := 0; i < t.NumField(); i++ {
		keys = append(keys, t.Field(i).Name)
	}
	return keys
}

func (d *Dependency) GetValues() []string {
	values := make([]string, 0)
	values = append(values, strconv.Itoa(int(d.ID)))
	values = append(values, strconv.Itoa(int(d.SourceID)))
	values = append(values, strconv.Itoa(int(d.TargetID)))
	values = append(values, d.Constraints)

	return values
}
