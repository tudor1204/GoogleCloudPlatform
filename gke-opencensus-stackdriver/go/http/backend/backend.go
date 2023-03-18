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

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/propagation"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
)

var destURL   = os.Getenv("DESTINATION_URL")

// [START trace_callremote]
// make an outbound call
func callRemoteEndpoint(ctx context.Context) (string, error) {
	resp, err := otelhttp.Get(ctx, destURL)
	if err != nil {
		return "", fmt.Errorf("could not fetch remote endpoint: %w", err)
	}
	defer resp.Body.Close()

	_, err = io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("could not read response from Google: %w", err)
	}

	return strconv.Itoa(resp.StatusCode), nil
}

// [END trace_callremote]

// [START trace_mainhandler]
func mainHandler(w http.ResponseWriter, r *http.Request) {
	returnCode, err := callRemoteEndpoint(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintln(w, returnCode)
}

// [END trace_mainhandler]
// [START trace_main]
func main() {
	// set up trace context propagator
	otel.SetTextMapPropagator(propagation.TraceContext{})

	// set up OTLP exporter
	exporter, err := otlptracegrpc.New(context.Background(), otlptracegrpc.WithInsecure())
	if err != nil {
		log.Fatalf("Unable to construct trace exporter: %v", err)
	}
	otel.SetTracerProvider(sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(exporter),
	))

	// handle incoming request
	http.Handle("/", otelhttp.NewHandler(http.HandlerFunc(mainHandler), "root"))

	log.Fatal(http.ListenAndServe(":8080", nil))
}

// [END trace_main]
