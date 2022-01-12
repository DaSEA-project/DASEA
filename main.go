package main

import (
	"fmt"
	"os"

	"github.com/heyjoakim/DASEA/common/helpers"
	"github.com/heyjoakim/DASEA/core/chromebrew"
	"github.com/heyjoakim/DASEA/core/conan"
	"github.com/heyjoakim/DASEA/core/fpm"
	"github.com/heyjoakim/DASEA/core/vcpkg"
)

func main() {
	args := os.Args[1:]

	for _, arg := range args {
		switch arg {
		case "fpm":
			fpm.Traverse()
		case "vcpkg":
			vcpkg.Traverse()
		case "conan":
			conan.Traverse()
		case "chromebrew":
			chromebrew.Traverse()
		case "release-dataset":
			helpers.ReleaseDataset()
		default:
			fmt.Println("Unknown command:", arg)
		}
	}
}
