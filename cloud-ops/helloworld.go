package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/brianvoe/gofakeit/v6"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"
)

var (
	logger, _      = zap.NewProduction()
	requestCounter = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "url_request_count",
			Help: "Simple counter for http requests",
		},
	)
)

func main() {
	prometheus.MustRegister(requestCounter)
	http.HandleFunc("/", handler)
	http.Handle("/metrics", promhttp.Handler())
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	logger.Info("Listening on localhost:",
		zap.String("port", port))

	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), nil))
}

func handler(w http.ResponseWriter, r *http.Request) {
	requestCounter.Inc()
	agentID := gofakeit.UserAgent()
	logger.Info("Hello world received a request.",
		zap.String("Browser", agentID))
	target := os.Getenv("TARGET")
	if target == "" {
		target = "World"
	}
	fmt.Fprintf(w, "Hello %s!\n", target)
}
