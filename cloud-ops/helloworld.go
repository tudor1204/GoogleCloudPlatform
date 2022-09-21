package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/brianvoe/gofakeit/v6"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"
)

var (
	logger, _ = zap.NewProduction()

	requestDurationHistogram = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "request_duration_seconds",
			Help:    "Request duration distribution",
			Buckets: prometheus.LinearBuckets(0.5, 0.5, 10),
		})

	requestCounter = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "url_request_count",
			Help: "Simple counter for http requests",
		})
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
	start := time.Now()
	rand.Seed(start.UnixNano())
	wait := rand.Intn(5)
	agentID := gofakeit.UserAgent()
	time.Sleep(time.Duration(wait) * time.Second)

	logger.Info("Hello world received a request.",
		zap.String("Browser", agentID))

	requestCounter.Inc()
	target := os.Getenv("TARGET")
	if target == "" {
		target = "World"
	}
	fmt.Fprintf(w, "Hello %s!\n", target)
	duration := time.Since(start)
	logger.Info("Request time was",
		zap.Float64("Duration", duration.Seconds()))

	requestDurationHistogram.Observe(duration.Seconds())
	prometheus.Register(requestDurationHistogram)
}
