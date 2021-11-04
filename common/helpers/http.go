package helpers

import (
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
)

func httpRequest(method, url string, payload io.Reader) ([]byte) {
	req, err := http.NewRequest(method, url, payload)
	if(method == "POST") {
		req.Header.Add("Content-Type", "application/json")
	}
	handleError(err)
	res, err := http.DefaultClient.Do(req)
	handleError(err)
	defer res.Body.Close()
	body, _ := ioutil.ReadAll(res.Body)
	fmt.Println(res)
	fmt.Println(string(body))
	return body
}
