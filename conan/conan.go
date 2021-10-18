package main

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
	"gopkg.in/yaml.v2"
)

type Dependencies []struct {
	Revision        string      `json:"revision"`
	Reference       string      `json:"reference"`
	IsRef           bool        `json:"is_ref"`
	DisplayName     string      `json:"display_name"`
	ID              string      `json:"id"`
	BuildID         interface{} `json:"build_id"`
	Context         string      `json:"context"`
	Remote          Remote      `json:"remote"`
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
type Remote struct {
	Name string `json:"name"`
	URL  string `json:"url"`
}

type Item struct {
	Folder string `yaml:"folder"`
}

// Clone executes a bash command to run bash or powershell script that clones repository
func clone(c string, p string) {
	cmd := exec.Command(c, p)
	stdout, err := cmd.Output()
	log.Info(string(stdout))

	if err != nil {
		log.Errorf("Failed cloning repository with error '%s'", err)
	}

}

// TODO: Make this a vardiac function together with func clone
func conan_info(name string, version string) {
	arg0 := "conan"
	arg1 := "info"
	arg2 := "-n"
	arg3 := "requires"
	arg4 := name + "/" + version + "@"
	arg5 := "--json"

	out_file := "out" + "/" + name + "/" + version + ".json"

	cmd := exec.Command(arg0, arg1, arg2, arg3, arg4, arg5, out_file)
	stdout, err := cmd.Output()

	log.Info(string(stdout))

	if err != nil {
		log.Errorf("Failed calling conan api with error %s", err)
	}
}

// Traverse walks the file tree of "recipes"
func traverse() {
	// var recipes []string

	err := filepath.Walk("repo/src/recipes", func(path string, info os.FileInfo, err error) error {

		if err != nil {
			fmt.Printf("Prevent panic by handling failure accessing a path %q: %v\n", path, err)
			return err
		}

		dir, file := filepath.Split(path)

		if file == "config.yml" {
			tmp := strings.Split(dir, "/")
			name := tmp[len(tmp)-2]
			test := parse_yaml(path)
			version := test[0]

			conan_info(name, version)
			parse_JSON(name, version)
		}

		// recipes = append(recipes, path)
		return nil
	})

	if err != nil {
		log.Fatalf("Error when walking directories: %v\n", err)
	}
}

// Parse_yaml opens a config.yml file and parses the content into a map
func parse_yaml(path string) []string {
	var res []string
	m := make(map[string]map[string]Item)

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

// Parse-JSON parses conan info json file to dependenceis struct
func parse_JSON(name string, version string) {
	file, err := os.Open("out/" + name + "/" + version + ".json")

	if err != nil {
		log.Info(err)
	}
	defer file.Close()

	byte_val, _ := ioutil.ReadAll(file)

	var dependencies Dependencies

	json.Unmarshal(byte_val, &dependencies)

	for i := 0; i < len(dependencies); i++ {

		if dependencies[i].DisplayName == name+"/"+version {
			log.Info(name + "/" + version + " requires: ")
			log.Info(dependencies[i].Requires)
		}
	}
}

func main() {
	if runtime.GOOS == "windows" {
		path := "ps\\clone.ps1"
		cmd := "powershell"

		clone(cmd, path)

	} else {
		cmd := "/bin/sh"
		path := "bash/clone.sh"

		clone(cmd, path)
	}
	traverse()
}
