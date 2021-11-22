package helpers

import (
	"encoding/csv"
	"errors"
	"os"
	"strings"
)

// Write to CSV, use models.getkeys and .values with a filepath
func WriteToCsv(keys []string, values []string, fpath string) {

	tokens := strings.Split(fpath, "/")
	path := strings.Join(tokens[:len(tokens)-1], "/")
	err := os.MkdirAll(path, 0777)
	if err != nil {
		panic(err)
	}

	// TODO make simple, stupid
	if _, err := os.Stat(fpath); errors.Is(err, os.ErrNotExist) {
		file, err := os.Create(fpath)
		if err != nil {
			panic(err)
		}
		writer := csv.NewWriter(file)
		writer.Write(keys)
		writer.Flush()
		file.Close()
	}

	file, err := os.OpenFile(fpath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0777)
	if err != nil {
		panic(err)
	}

	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write(values)
}

func checkFile(filename string) error {
	_, err := os.Stat(filename)
	if os.IsNotExist(err) {
		_, err := os.Create(filename)
		if err != nil {
			return err
		}
	}
	return nil
}
