package chromebrew

import (
	"fmt"
	"io/ioutil"
	"sort"
	"strings"
)

const (
	PACKAGE_REGESTRY = "https://github.com/skycocker/chromebrew"
	PACKAGE_DIR      = "./core/chromebrew/tmp/"
)

func Traverse() {

	// clone repo
	// _, err := git.PlainClone(PACKAGE_DIR, false, &git.CloneOptions{
	// 	URL:      PACKAGE_REGESTRY,
	// 	Progress: os.Stdout,
	// })
	// if err != nil {
	// 	panic(err)
	// }
	// read files

	bytesRead, _ := ioutil.ReadFile("./core/chromebrew/tmp/packages/a2png.rb")
	file_content := string(bytesRead)
	lines := strings.Split(file_content, "\n")
	fmt.Println(lines[3])
	fmt.Println(strings.Contains(lines[4], "description"))

	// write to csv
}

func contains(s []string, searchterm string) bool {
	i := sort.SearchStrings(s, searchterm)
	return i < len(s) && s[i] == searchterm
}
