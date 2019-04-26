/**
 * Copyright 2017 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// [START all]
package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

func main() {
	// use port1 serves service1 and port2 serves service2
	const (
		port1 = "8081"
		port2 = "8082"
	)

	finish := make(chan bool)

	server1 := http.NewServeMux()
	server1.HandleFunc("/", hello1)

	server2 := http.NewServeMux()
	server2.HandleFunc("/", hello2)

	go log.Fatal(http.ListenAndServe(":"+port1, server1))
	go log.Fatal(http.ListenAndServe(":"+port2, server2))
		
}

// hello1 prints "Hello world from service1"
func hello1(w http.ResponseWriter, r *http.Request) {
	log.Printf("Server1, %s", r.URL.Path)
	host, _ := os.Hostname()
	fmt.Fprintf(w, "Hello world from service1\n")
	fmt.Fprintf(w, "Full path: %s%s\n", host, r.URL.Path)
}

// hello2 prints "Hello world from service2"
func hello2(w http.ResponseWriter, r *http.Request) {
	log.Printf("Server2, %s", r.URL.Path)
	host, _ := os.Hostname()
	fmt.Fprintf(w, "Hello world from service2\n")
	fmt.Fprintf(w, "Full path: %s%s\n", host, r.URL.Path)
}

// [END all]
