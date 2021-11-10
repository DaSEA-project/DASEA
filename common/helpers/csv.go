package helpers

import (
	"encoding/csv"
	"os"
	"strings"
)

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
