package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// type Response struct {
// 	Packages  map[PackageName]PackageParent `json:"packages"`
// 	IndexDate string                        `json:"index-date"`
// }

// type Package struct {
// 	Name            string                 `json:"name"`
// 	Version         string                 `json:"version"`
// 	License         string                 `json:"license"`
// 	Author          string                 `json:"author"`
// 	Maintainer      string                 `json:"maintainer"`
// 	Copyright       string                 `json:"copyright"`
// 	Description     string                 `json:"description"`
// 	Dependencies    map[string]interface{} `json:"dependencies"`
// 	DevDependencies map[string]interface{} `json:"dev-dependencies"`
// 	GitUrl          string                 `json:"git"`
// 	GitTag          string                 `json:"git-tag"`
// }

// type PackageName string

// type PackageParent map[VersionNumber]Package

// type VersionNumber string

///////////////////////////////////////////////////////////////////////////////

type Response struct {
	Packages  map[string]interface{} `json:"packages"`
	IndexDate string                 `json:"index-date"`
}

type Package struct {
	Name            string                 `json:"name"`
	Version         string                 `json:"version"`
	License         string                 `json:"license"`
	Author          string                 `json:"author"`
	Maintainer      string                 `json:"maintainer"`
	Copyright       string                 `json:"copyright"`
	Description     string                 `json:"description"`
	Dependencies    map[string]interface{} `json:"dependencies"`
	DevDependencies map[string]interface{} `json:"dev-dependencies"`
	Git             string                 `json:"git"`
	GitTag          string                 `json:"git-tag"`
}

// type PackageName string

// type PackageParent map[VersionNumber]Package

// type VersionNumber string

const (
	PACKAGE_REGESTRY = "https://raw.githubusercontent.com/fortran-lang/fpm-registry/master/index.json"
)

func UnmarshalResponse(data []byte) (Response, error) {
	var r Response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func getKeys(m map[string]interface{}) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

func traverse() {
	response, err := http.Get(PACKAGE_REGESTRY)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := UnmarshalResponse(data)
	keys := getKeys(res.Packages)
	fmt.Println(keys)

}

func main() {
	traverse()
}
