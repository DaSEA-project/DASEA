package helpers

import (
	"fmt"
)

type HTTPResponse struct {
	message  string `json:"message"`
	status   int    `json:"status"`
}

const (
	ZENODO_API = "https://zenodo.org/api/deposit/depositions"
)


func ZenodoAPI() {
	const zenodoToken = getEnvVariable("ZENODO_API_KEY")
	response := httpRequest("GET", ZENODO_API);
	fmt.Println(response);
	return
}
