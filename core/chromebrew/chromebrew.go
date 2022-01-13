package chromebrew

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"regexp"
	"sort"
	"strings"
	"time"

	"github.com/heyjoakim/DASEA/common/helpers"
	"github.com/heyjoakim/DASEA/common/models"
	"gopkg.in/src-d/go-git.v4"
)

var (
	PACKAGE_REGESTRY           = "https://github.com/skycocker/chromebrew"
	TMP_DIR                    = "./core/chromebrew/tmp"
	PACKAGE_DIR                = "./core/chromebrew/tmp/packages"
	PKG_ID                     = int64(1)
	VERSION_ID                 = int64(1)
	DEPENDENCY_ID              = int64(1)
	date                       = time.Now().Format("01-02-2006")
	PKGS_MAP                   = make(map[string]int64)
	chromebrew_PACKAGE_DATA    = fmt.Sprintf("data/chromebrew/chromebrew_packages-%s.csv", date)
	chromebrew_VERSION_DATA    = fmt.Sprintf("data/chromebrew/chromebrew_versions-%s.csv", date)
	chromebrew_DEPENDENCY_DATA = fmt.Sprintf("data/chromebrew/chromebrew_dependencies-%s.csv", date)
)

func cloneRepository() {
	fmt.Println("Cloning repository")
	_, err := git.PlainClone(TMP_DIR, false, &git.CloneOptions{
		URL:      PACKAGE_REGESTRY,
		Progress: os.Stdout,
	})
	if err != nil {
		panic(err)
	}
}

func getPackageNames() []string {
	files, err := ioutil.ReadDir(PACKAGE_DIR)
	if err != nil {
		log.Fatal(err)
	}

	packageNames := []string{}
	for _, f := range files {
		packageNames = append(packageNames, strings.Trim(f.Name(), ".rb"))
	}
	return packageNames
}

func createNameIdPackageMap(packages []string) {
	for _, packageName := range packages {
		PKGS_MAP[packageName] = PKG_ID
		PKG_ID++
	}
}

func contains(s []string, searchterm string) bool {
	i := sort.SearchStrings(s, searchterm)
	return i < len(s) && s[i] == searchterm
}

func getAndExportPackageMetadata() {
	// get files
	files, err := ioutil.ReadDir(PACKAGE_DIR)
	if err != nil {
		log.Fatal(err)
	}
	for _, file := range files {
		// get file content
		bytesRead, _ := ioutil.ReadFile(PACKAGE_DIR + "/" + file.Name())
		file_content := string(bytesRead)
		lines := strings.Split(file_content, "\n")

		var pckg models.Package
		pckg.Name = strings.Trim(file.Name(), ".rb")
		pckg.ID = PKGS_MAP[pckg.Name]
		pckg.PackageManager = "Chromebrew"

		// Write package data to CSV
		helpers.WriteToCsv(pckg.GetKeys(), pckg.GetValues(), chromebrew_PACKAGE_DATA)

		var version models.Version
		version.ID = VERSION_ID
		version.PackageID = PKGS_MAP[pckg.Name]

		var dependencies = []string{}

		for _, line := range lines {
			if strings.Contains(line, "description") {
				version.Description = strings.Trim(strings.Trim(lines[3], "description "), "'")
			}

			if strings.Contains(line, "homepage") {
				version.HomepageURL = strings.Trim(strings.Trim(lines[4], "homepage "), "'")
			}

			if strings.Contains(line, "version") {
				version.Version = strings.Trim(strings.Trim(lines[4], "version "), "'")
			}

			if strings.Contains(line, "@_ver") {
				version.Version = strings.Trim(strings.Trim(lines[4], "@_ver =  "), "'")
			}
			if strings.Contains(line, "license") {
				version.License = strings.Trim(strings.Trim(lines[4], "license "), "'")
			}

			if strings.Contains(line, "source_url") {
				version.SourceCodeURL = strings.Trim(strings.Trim(lines[4], "source_url "), "'")
			}

			if strings.Contains(line, "depends_on") {
				re := regexp.MustCompile(`'[^"]+'`)
				newStrs := re.FindAllString(line, -1)
				for _, s := range newStrs {
					dependencies = append(dependencies, strings.Trim(s, "'"))
				}
			}
		}

		// write version data to CSV
		helpers.WriteToCsv(version.GetKeys(), version.GetValues(), chromebrew_VERSION_DATA)
		VERSION_ID++

		for _, dep := range dependencies {
			var formattedDep models.Dependency
			formattedDep.ID = DEPENDENCY_ID
			formattedDep.SourceID = VERSION_ID
			formattedDep.TargetID = PKGS_MAP[dep]

			// write dependency data to CSV
			helpers.WriteToCsv(formattedDep.GetKeys(), formattedDep.GetValues(), chromebrew_DEPENDENCY_DATA)
			DEPENDENCY_ID++
		}
	}

}

func Traverse() {
	// clone repo
	cloneRepository()

	// extract package names from file name
	packageNames := getPackageNames()
	fmt.Println("Found", len(packageNames), "packages")
	createNameIdPackageMap(packageNames)

	// get package data and export to csv
	getAndExportPackageMetadata()
	fmt.Println("Chromebrew Package Data Exported")

	// delete tmp directory
	os.RemoveAll(TMP_DIR)
}
