// Copyright 2023 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"log"
	"net/http"

	"github.com/GoogleCloudPlatform/kubernetes-engine-samples/distributed-tracing/common"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func main() {
	if err := common.Setup(); err != nil {
		log.Print(err)
	}

	mux := http.NewServeMux()
	mux.Handle("/hello/",
		otelhttp.WithRouteTag("/hello/{name}",
			http.StripPrefix("/hello/", &helloHandler{client: otelhttp.DefaultClient})))
	log.Fatalln(http.ListenAndServe(":8080", otelhttp.NewHandler(mux, "backend")))
}
