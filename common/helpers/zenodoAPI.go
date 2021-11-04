package helpers

import (
	"fmt"
	"strings"

	"github.com/m7shapan/njson"
)

type ZENODOBucketResponse struct {
	Bucket  string `njson:"links.bucket"`
}

const (
	ZENODO_API = "https://zenodo.org/api/"
)

func ZenodoAPI() {
	zenodoToken := getEnvVariable("ZENODO_API_KEY")
	endpoint := ZENODO_API + "deposit/depositions?access_token=" + zenodoToken
	payload := strings.NewReader("{}")
	response := httpRequest("POST",endpoint,payload)
	res,_ := UnmarshalResponse(response)
	buckerURL := res.Bucket
	fmt.Println(buckerURL)

	// TODO: use bucket URL to upload the file in the bucket
	// bucketURL/fileName?access_token=zenodoToken


	return
}

func UnmarshalResponse(data []byte) (ZENODOBucketResponse, error) {
	var r ZENODOBucketResponse
	err := njson.Unmarshal(data, &r)
	return r, err
}
