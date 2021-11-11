package main

import (
	"fmt"
	"os"

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
		default:
			fmt.Println("Unknown command:", arg)
		}
	}
}
