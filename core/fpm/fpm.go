package fpm

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"reflect"
	"sort"
	"strings"

	"github.com/heyjoakim/DASEA/common/helpers"
	"github.com/heyjoakim/DASEA/common/models"
)

type response struct {
	Packages  map[string]interface{} `json:"packages"`
	IndexDate string                 `json:"index-date"`
}

const (
	PACKAGE_REGESTRY = "https://raw.githubusercontent.com/fortran-lang/fpm-registry/master/index.json"
)

var (
	PKGS_MAP  = make(map[string]int)
	versionID = 0
)

func unmarshalResponse(data []byte) (response, error) {
	var r response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func unknownToString(property interface{}) string {
	_type := reflect.TypeOf(property)
	switch _type.Kind() {
	case reflect.String:
		return property.(string)
	case reflect.Slice:
		fallthrough
	case reflect.Array:
		sb := strings.Builder{}
		for i, v := range property.([]interface{}) {
			sb.WriteString(v.(string))
			if i < len(property.([]interface{}))-1 {
				sb.WriteString(";")
			}
		}
		return sb.String()
	default:
		panic("unsupported type")
	}
}

func parsePackage(pkg map[string]interface{}) models.CSVInput {
	full := models.CSVInput{}
	model := models.Package{}

	latestPkg := pkg["latest"].(map[string]interface{})

	model.ID = int64(PKGS_MAP[latestPkg["name"].(string)])
	model.PackageManager = "FPM"
	model.Platform = "Fortran"
	if latestPkg["name"] != nil {
		model.Name = latestPkg["name"].(string)
	}
	if latestPkg["description"] != nil {
		model.Description = latestPkg["description"].(string)
	}
	if latestPkg["git"] != nil {
		model.SourceCodeURL = latestPkg["git"].(string)
	}
	if latestPkg["maintainer"] != nil {
		model.Maintainer = unknownToString(latestPkg["maintainer"])
	}
	if latestPkg["license"] != nil {
		model.License = latestPkg["license"].(string)
	}
	if latestPkg["author"] != nil {
		model.Author = unknownToString(latestPkg["author"])
	}

	//////////////// VERSIONS /////////////////////
	///////////////////////////////////////////////

	versionKeys := getKeys(pkg)
	versions := make([]models.Version, 0)

	var deps map[string]interface{}
	var devDeps map[string]interface{}

	for _, version := range versionKeys {
		v := pkg[version].(map[string]interface{})
		// check if version is not already added, since package can contain dupes
		if contains(versions, v["version"].(string)) {
			continue
		}
		version := models.Version{ID: int64(versionID), PackageID: model.ID, Version: v["version"].(string)}
		versionID = versionID + 1
		versions = append(versions, version)
		helpers.WriteToCsv(version.GetKeys(), version.GetValues(), "data/fpm/fmp-versions.csv")
		ds := v["dependencies"]
		if ds != nil {
			deps = ds.(map[string]interface{})
		}
		dds := v["dependencies"]
		if ds != nil {
			devDeps = dds.(map[string]interface{})
		}
	}

	/////////////// DEPENDENCIES //////////////////
	///////////////////////////////////////////////

	helpers.WriteToCsv(model.GetKeys(), model.GetValues(), "data/fpm/fpm-packages.csv")
	full.Pkg = model
	full.Versions = versions
	full.Dependencies = append(getDependencies(deps), getDependencies(devDeps)...)

	// fmt.Println(full)

	return full
}

func getDependencies(deps map[string]interface{}) []models.Dependency {
	dependencies := make([]models.Dependency, 0)
	depNames := getKeys(deps)
	for _, dependency := range depNames {
		d := deps[dependency].(map[string]interface{})
		constraint := d["tag"]
		var constraintString string
		if constraint != nil {
			constraintString = constraint.(string)
		}

		dependencies = append(dependencies, models.Dependency{TargetName: dependency, Constraints: constraintString})
	}

	return dependencies
}

func contains(s []models.Version, e string) bool {
	for _, a := range s {
		if a.Version == e {
			return true
		}
	}
	return false
}

func getKeys(m map[string]interface{}) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// call this
func Traverse() []models.CSVInput {
	response, err := http.Get(PACKAGE_REGESTRY)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := unmarshalResponse(data)
	keys := getKeys(res.Packages)
	pkgs := make([]models.CSVInput, 0, len(keys))
	for i, key := range keys {
		PKGS_MAP[key] = i
		pkg := res.Packages[key]
		pp := parsePackage(pkg.(map[string]interface{}))
		pkgs = append(pkgs, pp)
	}

	fmt.Println(PKGS_MAP)
	// fmt.Println(pkgs)
	return pkgs
}
