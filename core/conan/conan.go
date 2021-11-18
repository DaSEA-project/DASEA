package conan

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"

	"github.com/heyjoakim/DASEA/common/helpers"
	"github.com/heyjoakim/DASEA/common/models"
	log "github.com/sirupsen/logrus"
	yaml "gopkg.in/yaml.v2"
)

type packageJSON []struct {
	Revision        string      `json:"revision"`
	Reference       string      `json:"reference"`
	IsRef           bool        `json:"is_ref"`
	DisplayName     string      `json:"display_name"`
	ID              string      `json:"id"`
	BuildID         interface{} `json:"build_id"`
	Context         string      `json:"context"`
	Remote          remote      `json:"remote"`
	URL             string      `json:"url"`
	Homepage        string      `json:"homepage"`
	License         []string    `json:"license"`
	Description     string      `json:"description"`
	Topics          []string    `json:"topics"`
	Provides        []string    `json:"provides"`
	Recipe          string      `json:"recipe"`
	PackageRevision string      `json:"package_revision"`
	Binary          string      `json:"binary"`
	BinaryRemote    string      `json:"binary_remote"`
	CreationDate    string      `json:"creation_date"`
	RequiredBy      []string    `json:"required_by,omitempty"`
	Requires        []string    `json:"requires,omitempty"`
}
type remote struct {
	Name string `json:"name"`
	URL  string `json:"url"`
}

type item struct {
	Folder string `yaml:"folder"`
}

var (
	PKGS_MAP     = make(map[string]int)
	VERSIONS_MAP = make(map[string][]string)
)

func externalCommand(name string, args ...string) {
	cmd := exec.Command(name, args...)
	stdout, err := cmd.CombinedOutput()

	if err != nil {
		log.Errorf(string(stdout))
	}
}

func loggerInit() {
	currentTime := time.Now()
	date := currentTime.Format("01-02-2006")
	var filename string = fmt.Sprintf("core/conan/logs/%s.log", date)

	f, err := os.OpenFile(filename, os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0644)
	formatter := new(log.TextFormatter)
	formatter.TimestampFormat = "02-01-2006 15:04:05"
	formatter.FullTimestamp = true
	log.SetFormatter(formatter)

	if err != nil {
		fmt.Println(err)
	} else {
		mw := io.MultiWriter(f, os.Stdout)
		log.SetOutput(mw)
	}
}

func conanInfo(name string, version string) {

	arg0 := "conan"
	arg1 := "info" // TODO: Test if --update flag reduces time !if find other mechanism to not load cached packages
	arg2 := "-n"
	arg3 := "requires"
	arg4 := fmt.Sprintf("%s/%s@", name, version)
	arg5 := "--json"
	out := fmt.Sprintf("out/%s/%s.json", name, version)

	log.Infof("Getting info from %s/%s", name, version)
	externalCommand(arg0, arg1, arg2, arg3, arg4, arg5, out)
}

func parseYAML(path string) []string {
	var res []string
	m := make(map[string]map[string]item)

	file, err := ioutil.ReadFile(path)

	if err != nil {
		log.Errorf("Error reading yaml file %s, err")
	}

	err2 := yaml.Unmarshal([]byte(file), &m)

	if err != nil {
		log.Fatalf("error: %v", err2)
	}

	for _, value := range m {
		for key := range value {
			res = append(res, key)
		}
	}
	return res
}

func parseJSON(name string, version string, id int) {
	pkg := models.Package{}

	fname := fmt.Sprintf("core/conan/out/%s/%s.json", name, version)
	file, err := os.Open(fname)

	log.Infof("Writing %s", fname)

	if err != nil {
		log.Info(err)
	}
	defer file.Close()

	byte_val, _ := ioutil.ReadAll(file)

	var packages packageJSON

	json.Unmarshal(byte_val, &packages)

	for i := 0; i < len(packages); i++ {

		// We only want to get info about the current package and dont know if all is at index 0
		if packages[i].DisplayName == name+"/"+version {
			pkg.ID = int64(id)
			pkg.Name = name
			pkg.PackageManager = "Conan"
			pkg.Platform = "C/C++"
			pkg.Description = packages[i].Description
			pkg.HomepageURL = packages[i].URL
			pkg.SourceCodeURL = ""
			pkg.Maintainer = ""
			pkg.License = packages[i].License[0]
			pkg.Author = ""

			helpers.WriteLineToCsv(pkg, "data/conan/conan_packages.csv")

		} else {
			log.Errorf("Package %s does not exist in conan info", name+version)
		}
	}
}

func generateMaps() (map[string]int, map[string][]string) {
	i := 0

	err := filepath.Walk("core/conan/assets/repo/src/recipes", func(path string, info os.FileInfo, err error) error {

		if err != nil {
			log.Errorf("Prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}

		dir, file := filepath.Split(path)

		if file == "config.yml" {
			tmp := strings.Split(dir, "/")
			name := tmp[len(tmp)-2]
			PKGS_MAP[name] = i //TODO: Save this to CSV INSTEAD
			VERSIONS_MAP[name] = parseYAML(path)
			i++
		}

		return nil
	})

	if err != nil {
		log.Fatalf("Error when walking directories: %v\n", err)
	}

	return PKGS_MAP, VERSIONS_MAP

}

func traverse() {
	keys := make([]string, 0, len(PKGS_MAP)) //TODO: SMARTER
	for k := range PKGS_MAP {
		keys = append(keys, k)
	}

	sort.Strings(keys)

	for id, name := range keys {
		pkgVersions := VERSIONS_MAP[name]

		for _, version := range pkgVersions {
			// conanInfo(name, version)
			parseJSON(name, version, id)
		}
	}
}

// Traverses the conan package mange recipes
func Traverse() {
	loggerInit()

	if runtime.GOOS == "windows" {
		path := "core\\conan\\ps\\clone.ps1"
		cmd := "powershell"

		externalCommand(cmd, path)

	} else {
		cmd := "/bin/sh"
		path := "core/conan/bash/clone.sh"

		externalCommand(cmd, path)
	}

	fmt.Println(PKGS_MAP)

	generateMaps()
	traverse()
}
