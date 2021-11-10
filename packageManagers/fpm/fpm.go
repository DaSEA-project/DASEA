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
	ID int64
)

func UnmarshalResponse(data []byte) (response, error) {
	var r response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func parsePackage(pkg map[string]interface{}) models.Package {
	_id := ID
	ID++
	latestPkg := pkg["latest"].(map[string]interface{})
	model := models.Package{}

	model.ID = _id
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
		_type := reflect.TypeOf(latestPkg["maintainer"])
		switch _type.Kind() {
		case reflect.String:
			model.Maintainer = latestPkg["maintainer"].(string)
		case reflect.Slice:
			fallthrough
		case reflect.Array:
			sb := strings.Builder{}
			for _, v := range latestPkg["maintainer"].([]interface{}) {
				sb.WriteString(v.(string))
				sb.WriteString(";")
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
			for _, v := range latestPkg["author"].([]interface{}) {
				sb.WriteString(v.(string))
				sb.WriteString(";")
			}
			model.Author = sb.String()
		default:
			panic("unsupported type")
		}
	}

	///////////////////////////////////////////////
	///////////////////////////////////////////////

	return model
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
	res, _ := UnmarshalResponse(data)
	keys := getKeys(res.Packages)
	pkgs := make([]models.Package, 0, len(keys))
	for _, key := range keys {
		pkg := res.Packages[key]
		pp := parsePackage(pkg.(map[string]interface{}))
		pkgs = append(pkgs, pp)
	}

	csvData := make([][]string, 0)
	q := models.Package{}
	csvData = append(csvData, q.GetKeys())
	for _, p := range pkgs {
		csvData = append(csvData, p.GetValues())
	}
	helpers.WriteToCsv(csvData, "packageManagers/fpm/out/packages.csv")
	fmt.Printf("%+v", pkgs[0])

}
