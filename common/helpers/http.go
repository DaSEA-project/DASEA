package helpers

import (
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
)

func httpRequest(method, url string, payload io.Reader, contentType string) []byte {
	req, err := http.NewRequest(method, url, payload)
	if method == "POST" {
		req.Header.Add("Content-Type", contentType)
	}
	handleError(err)
	res, err := http.DefaultClient.Do(req)
	handleError(err)
	defer res.Body.Close()
	body, _ := ioutil.ReadAll(res.Body)
	statusOK := res.StatusCode >= 200 && res.StatusCode < 300
	if !statusOK {
		panic(fmt.Sprintln("Zenodo API Error %s", string(body)))
	}
	return body
}
