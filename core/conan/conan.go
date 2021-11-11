package conan

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	log "github.com/sirupsen/logrus"
	yaml "gopkg.in/yaml.v2"
)

type dependencies []struct {
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

func externalCommand(name string, args ...string) {
	cmd := exec.Command(name, args...)
	stdout, err := cmd.Output()
	log.Info(string(stdout))

	if err != nil {
		log.Errorf("Failed cloning repository with error '%s'", err)
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

func parseJSON(name string, version string) {
	fname := fmt.Sprintf("out/%s/%s.json", name, version)
	file, err := os.Open(fname)

	if err != nil {
		log.Info(err)
	}
	defer file.Close()

	byte_val, _ := ioutil.ReadAll(file)

	var dependencies dependencies

	json.Unmarshal(byte_val, &dependencies)

	for i := 0; i < len(dependencies); i++ {

		if dependencies[i].DisplayName == name+"/"+version {
			log.Infof("%s/%s requires: ", name, version) //TODO: Change output to csv or what will be decided
			log.Info(dependencies[i].Requires)
		}
	}
}

func traverse() {
	err := filepath.Walk("repo/src/recipes", func(path string, info os.FileInfo, err error) error {

		if err != nil {
			log.Errorf("Prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}

		dir, file := filepath.Split(path)

		if file == "config.yml" {
			tmp := strings.Split(dir, "/")
			name := tmp[len(tmp)-2]
			test := parseYAML(path)
			version := test[0]

			conanInfo(name, version)
			parseJSON(name, version)
		}

		return nil
	})

	if err != nil {
		log.Fatalf("Error when walking directories: %v\n", err)
	}
}

// Traverses the conan package mange recipes
func Traverse() {
	if runtime.GOOS == "windows" {
		path := "core\\conan\\ps\\clone.ps1"
		cmd := "powershell"

		externalCommand(cmd, path)

	} else {
		cmd := "/bin/sh"
		path := "core/conan/bash/clone.sh"

		externalCommand(cmd, path)
	}
	// parseJSON("poco", "1.11.0") // traverse()
}
