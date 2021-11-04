package helpers

import (
	"net/http"
)

func httpRequest(method, url string) (*http.Response) {
	req, err := http.NewRequest(method, url, nil)

	handleError(err)
	client := &http.Client{}
	resp, err := client.Do(req)
	handleError(err)
	return resp
}
