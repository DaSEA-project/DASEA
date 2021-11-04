package models

type Dependency struct {
	ID 					int64 	`json:"id"`
	SourceID 		int64 	`json:"source_id"`
	TargetID 		int64 	`json:"target_id"`
	Constraints string  `json:"constraints"`
}