package sovereign.placement_test

import rego.v1

import data.sovereign.placement

profiles := {"eu-assistant": {
	"permitted_domains": ["aws-eusc"], "permitted_jurisdictions": ["DE"],
	"approved_models": ["m1"], "max_data_class": "confidential", "country_only": true,
}}

endpoints := {
	"eusc-de": {"domain": "aws-eusc", "model_id": "m1", "processing_jurisdictions": ["DE"]},
	"com-fra": {"domain": "aws-commercial", "model_id": "m1", "processing_jurisdictions": ["DE"]},
	"eusc-geo": {"domain": "aws-eusc", "model_id": "m1", "processing_jurisdictions": ["DE", "FR"]},
}

req(ep) := {"use_case_id": "eu-assistant", "endpoint_id": ep, "caller_entitled": true, "data_class": "internal"}

test_allow_eusc if placement.allow with input as req("eusc-de") with data.profiles as profiles with data.endpoints as endpoints

test_deny_commercial if not placement.allow with input as req("com-fra") with data.profiles as profiles with data.endpoints as endpoints

test_deny_geo_profile if not placement.allow with input as req("eusc-geo") with data.profiles as profiles with data.endpoints as endpoints
