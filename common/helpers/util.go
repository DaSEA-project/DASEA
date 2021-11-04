package helpers

import (
	"os"

	"github.com/joho/godotenv"
)

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func getEnvVariable(envVar string) string {
	err := godotenv.Load(".env")
	if err != nil {
		handleError(err)
	}

	return os.Getenv(envVar)
}