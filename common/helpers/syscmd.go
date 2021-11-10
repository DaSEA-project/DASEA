package helpers

import (
	"log"
	"os/exec"
)

// Run system commands
func Run(name string, args ...string) {
	cmd := exec.Command(name, args...)
	stdout, err := cmd.Output()
	log.Print(string(stdout)) //TODO: Use logger library?

	if err != nil {
		log.Printf("Failed cloning repository with error '%s'", err)
	}
}
