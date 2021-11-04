package helpers

import (
	"fmt"
	"os/exec"
)

func sysCommand(name string, args ... string) {
	cmd := exec.Command(name, args...)
	stdout, err := cmd.Output()
	fmt.Print(string(stdout)) //TODO: Use logger library?

	if err != nil {
		fmt.Printf("Failed cloning repository with error '%s'", err)
	}
}