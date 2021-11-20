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
	currentTime           = time.Now()
	date                  = currentTime.Format("01-02-2006")
	dependencyCnt         int
	PKGS_MAP_IDX          = make(map[string]int)
	PKGS_VISITED          = make(map[string]bool)
	VERSIONS_MAP          = make(map[string][]string)
	VERSIONS_MAP_IDX      = make(map[string]int)
	CONAN_PACKAGE_DATA    = fmt.Sprintf("data/conan/conan_packages-%s.csv", date)
	CONAN_VERSION_DATA    = fmt.Sprintf("data/conan/conan_versions-%s.csv", date)
	CONAN_DEPENDENCY_DATA = fmt.Sprintf("data/conan/conan_dependencies-%s.csv", date)
)

func externalCommand(name string, args ...string) {
	cmd := exec.Command(name, args...)
	stdout, err := cmd.CombinedOutput()

	if err != nil {
		log.Errorf(string(stdout))
	}
}

func loggerInit() {
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

func parseJSON(name string, version string, pkgId int) {
	pkg := models.Package{}
	v := models.Version{}
	d := models.CsvDependency{}

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

		// We only want to get info about the current and not all are at index 0
		if packages[i].DisplayName == name+"/"+version {

			if PKGS_VISITED[name] == false {

				pkg.ID = int64(pkgId)
				pkg.Name = name
				pkg.PackageManager = "Conan"
				pkg.Platform = "C/C++"
				pkg.Description = packages[i].Description
				pkg.HomepageURL = packages[i].URL
				pkg.SourceCodeURL = "N/A"
				pkg.Maintainer = "N/A"
				pkg.License = packages[i].License[0]
				pkg.Author = "N/A"

				helpers.WriteLineToCsv(pkg, CONAN_PACKAGE_DATA)
				PKGS_VISITED[name] = true
			} else {
				log.Debugf("%s already visited", name, version)

			}
			v.ID = int64(VERSIONS_MAP_IDX[name+version])
			v.PackageID = int64(pkgId)
			v.Version = name + "@" + version
			helpers.WriteCsvVersion(v, CONAN_VERSION_DATA)

			// Inside specific version

			if packages[i].Requires != nil {
				// Looping thre requires slice
				for _, dependency := range packages[i].Requires {
					targetName := strings.Split(dependency, "/")
					d.ID = int64(dependencyCnt)
					d.SourceID = int64(VERSIONS_MAP_IDX[name+version])
					d.TargetID = int64(PKGS_MAP_IDX[targetName[0]])
					d.Constraints = "N/A"
					helpers.WriteCsvDependency(d, CONAN_DEPENDENCY_DATA)
					dependencyCnt++
				}

			} else {
				log.Debugf("%s %s has no dependencies", name, version)
			}

		} else {
			// log.Errorf("Package %s does not exist in conan info", name+version)
		}
	}
}

func getPackageInfo() {
	err := filepath.Walk("core/conan/assets/repo/src/recipes", func(path string, info os.FileInfo, err error) error {

		if err != nil {
			// log.Errorf("Prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}

		dir, file := filepath.Split(path)

		if file == "config.yml" {
			tmp := strings.Split(dir, "/")
			name := tmp[len(tmp)-2]
			versions := parseYAML(path)

			for _, version := range versions {
				conanInfo(name, version)
			}
		}

		return nil
	})

	if err != nil {
		log.Fatalf("Error when walking directories: %v\n", err)
	}
}

func geteMaps() {
	var tmpVersions []string
	i := 0
	err := filepath.Walk("core/conan/out", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			log.Errorf("Prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}
		dir, file := filepath.Split(path)
		test := filepath.Ext(path)

		if info.IsDir() && file != "out" { // Fore some reason Walk includes out dir
			tmpVersions = nil
		}

		if test == ".json" {
			// Get current package
			t := strings.Split(dir, "/")
			pkgName := t[len(t)-2]
			if _, exists := PKGS_MAP_IDX[pkgName]; !exists {
				PKGS_MAP_IDX[pkgName] = i //TODO: Save this to CSV INSTEAD
				i++
			}

			// Get current version (While walking)
			tt := strings.Split(file, ".json")
			versionName := tt[0]
			tmpVersions = append(tmpVersions, versionName)
			VERSIONS_MAP[pkgName] = tmpVersions
		}

		return nil
	})
	if err != nil {
		log.Fatalf("Error when walking out directories: %v\n", err)
	}
}

func traverse() {
	versionCnt := 0

	pkg_keys := make([]string, 0, len(PKGS_MAP_IDX)) //TODO: SMARTER
	for k := range PKGS_MAP_IDX {
		pkg_keys = append(pkg_keys, k)
	}
	sort.Strings(pkg_keys)

	for pkgId, name := range pkg_keys {
		pkgVersions := VERSIONS_MAP[name]

		for _, version := range pkgVersions {
			// fmt.Println(VERSIONS_MAP_IDX)
			VERSIONS_MAP_IDX[name+version] = versionCnt
			parseJSON(name, version, pkgId)
			versionCnt++
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

	DATA_FILES := []string{CONAN_PACKAGE_DATA, CONAN_DEPENDENCY_DATA, CONAN_VERSION_DATA}

	// Delete todays data file if already existing
	for _, file := range DATA_FILES {
		if _, err := os.Stat(file); err == nil {
			e := os.Remove(file)
			if e != nil {
				log.Fatal(e)
			}
		}
	}

	//generatePackageInfo() // Calls Conan Info, reupdating data (Time 0.5 - 1 hour)
	geteMaps()
	traverse()
}
