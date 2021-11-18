package helpers

import (
	"encoding/csv"
	"errors"
	"os"
	"strings"

	"github.com/heyjoakim/DASEA/common/models"
)

// Parse json to struct type
func ParseJSON() int {
	return 42
}

// Parse yaml to struct type
func ParseYAML() int {
	return 42
}

// Write json to CSV file
func JSONToCSV() int {
	return 42
}

// Write 2D array to CSV file. The first row is the header.
func WriteToCsv(data [][]string, filePath string) {
	tokens := strings.Split(filePath, "/")
	path := strings.Join(tokens[:len(tokens)-1], "/")

	err := os.MkdirAll(path, 0777)
	if err != nil {
		panic(err)
	}
	file, err := os.Create(filePath)

	if err != nil {
		panic(err)
	}

	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, value := range data {
		writer.Write(value)
	}
}

func WriteLineToCsv(model models.Package, filePath string) {
	tokens := strings.Split(filePath, "/")
	path := strings.Join(tokens[:len(tokens)-1], "/")

	// TODO make simple, stupid
	if _, err := os.Stat(filePath); errors.Is(err, os.ErrNotExist) {
		file, err := os.Create(filePath)
		if err != nil {
			panic(err)
		}
		writer := csv.NewWriter(file)
		writer.Write(model.GetKeys())
		writer.Flush()
		file.Close()
	}

	err := os.MkdirAll(path, 0777)
	if err != nil {
		panic(err)
	}
	file, err := os.OpenFile(filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0777)

	if err != nil {
		panic(err)
	}

	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write(model.GetValues())
}
