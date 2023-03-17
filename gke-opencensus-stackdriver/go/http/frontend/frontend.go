/*
Copyright 2023 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

// [START trace_imports]
import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	cloudtrace "github.com/GoogleCloudPlatform/opentelemetry-operations-go/exporter/trace"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/propagation"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

// [END trace_imports]
var (
	projectID   = os.Getenv("PROJECT_ID")
	backendAddr = os.Getenv("BACKEND")
	location    = os.Getenv("LOCATION")
)

// [START trace_mainhandler]
func mainHandler(w http.ResponseWriter, r *http.Request) {
	childCtx, cancel := context.WithTimeout(r.Context(), 1000*time.Millisecond)
	defer cancel()

	res, err := otelhttp.Get(childCtx, backendAddr)
	if err != nil {
		log.Fatalf("%v", err)
	}

	fmt.Printf("%v\n", res.StatusCode)
}

// [END trace_mainhandler]
// [START trace_mainfunction]
func main() {
	// set up trace context propagator
	otel.SetTextMapPropagator(propagation.TraceContext{})

	// set up Cloud Trace exporter
	exporter, err := cloudtrace.New(cloudtrace.WithProjectID(projectID))
	if err != nil {
		log.Fatal(err)
	}
	otel.SetTracerProvider(sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(exporter),
	))

	// handle incoming request
	http.Handle("/", otelhttp.WithRouteTag("/", http.HandlerFunc(mainHandler)))

	log.Fatal(http.ListenAndServe(":8081", nil))
}

// [END trace_mainfunction]
