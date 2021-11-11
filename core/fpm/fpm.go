package fpm

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"reflect"
	"sort"
	"strings"

	"github.com/heyjoakim/DASEA/common/models"
)

type response struct {
	Packages  map[string]interface{} `json:"packages"`
	IndexDate string                 `json:"index-date"`
}

type full struct {
	pkg          models.Package
	versions     []models.Version
	dependencies []models.Dependency
}

const (
	PACKAGE_REGESTRY = "https://raw.githubusercontent.com/fortran-lang/fpm-registry/master/index.json"
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

func parsePackage(pkg map[string]interface{}) full {
	full := full{}

	latestPkg := pkg["latest"].(map[string]interface{})

	model := models.Package{}

	model.PackageManager = "FPM"
	model.Platform = "Fortran"
	if latestPkg["name"] != nil {
		model.Name = latestPkg["name"].(string)
		fmt.Println(model.Name)
	}
	if latestPkg["description"] != nil {
		model.Description = latestPkg["description"].(string)
	}
	if latestPkg["git"] != nil {
		model.SourceCodeURL = latestPkg["git"].(string)
	}
	if latestPkg["maintainer"] != nil {
		_type := reflect.TypeOf(latestPkg["maintainer"])
		switch _type.Kind() {
		case reflect.String:
			model.Maintainer = latestPkg["maintainer"].(string)
		case reflect.Slice:
			fallthrough
		case reflect.Array:
			sb := strings.Builder{}
			for i, v := range latestPkg["maintainer"].([]interface{}) {
				sb.WriteString(v.(string))
				if i < len(latestPkg["maintainer"].([]interface{}))-1 {
					sb.WriteString(";")
				}
			}
			model.Maintainer = sb.String()
		default:
			panic("unsupported type")
		}
	}
	if latestPkg["license"] != nil {
		model.License = latestPkg["license"].(string)
	}
	if latestPkg["author"] != nil {
		_type := reflect.TypeOf(latestPkg["author"])
		switch _type.Kind() {
		case reflect.String:
			model.Author = latestPkg["author"].(string)
		case reflect.Slice:
			fallthrough
		case reflect.Array:
			sb := strings.Builder{}
			for i, v := range latestPkg["author"].([]interface{}) {
				sb.WriteString(v.(string))
				if i < len(latestPkg["author"].([]interface{}))-1 {
					sb.WriteString(";")
				}
			}
			model.Author = sb.String()
		default:
			panic("unsupported type")
		}
	}

	//////////////// VERSIONS /////////////////////
	///////////////////////////////////////////////

	versionKeys := getKeys(pkg)
	versions := make([]models.Version, 0)

	var deps map[string]interface{}
	var devDeps map[string]interface{}

	for _, version := range versionKeys {
		v := pkg[version].(map[string]interface{})
		if contains(versions, v["version"].(string)) {
			continue
		}
		versions = append(versions, models.Version{Version: v["version"].(string)})
		ds := v["dependencies"]
		fmt.Println(ds)
		if ds != nil {
			deps = ds.(map[string]interface{})
		}
		dds := v["dependencies"]
		fmt.Println(dds)
		if ds != nil {
			devDeps = dds.(map[string]interface{})
		}

	}

	/////////////// DEPENDENCIES //////////////////
	///////////////////////////////////////////////

	full.pkg = model
	full.versions = versions
	full.dependencies = append(getDependencies(deps), getDependencies(devDeps)...)

	fmt.Println(full)

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
func Traverse() {
	response, err := http.Get(PACKAGE_REGESTRY)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := unmarshalResponse(data)
	keys := getKeys(res.Packages)
	pkgs := make([]full, 0, len(keys))
	for _, key := range keys {
		pkg := res.Packages[key]
		pp := parsePackage(pkg.(map[string]interface{}))
		pkgs = append(pkgs, pp)
	}

	return pkgs

}
