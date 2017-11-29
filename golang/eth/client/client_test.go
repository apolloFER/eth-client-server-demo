package client

import (
    "testing"
)

func TestServerNotActive(t *testing.T) {
	err := SendHtml("llllll", 1111, "test")
	if err == nil {
		t.Fail()
	}
}

func TestWrongEthUrl(t *testing.T) {
	backupUrl := Url
	Url = "https://empty.url.is/"
	_, err := GetCurrentBlock()
	if err == nil {
		t.Fail()
	}
	Url = backupUrl
}

func TestBlockFetching(t *testing.T) {
	_, err := GetCurrentBlock()

	if err != nil {
		t.Fail()
	}
}