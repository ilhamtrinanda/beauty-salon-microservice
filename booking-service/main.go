package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

type Booking struct {
	ID         int    `json:"id"`
	CustomerID string `json:"customer_id"`
	SalonID    int    `json:"salon_id"`
	BookingDate string `json:"booking_date"`
	Status     string `json:"status"`
	Notes      string `json:"notes"`
	CreatedAt  string `json:"created_at"`
}

var db *sql.DB

func main() {
	var err error
	
	// Database connection
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "5432")
	user := getEnv("DB_USER", "postgres")
	password := getEnv("DB_PASSWORD", "password")
	dbname := getEnv("DB_NAME", "booking_db")

	psqlInfo := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err = sql.Open("postgres", psqlInfo)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Successfully connected to database!")

	// Create table
	createTable := `
	CREATE TABLE IF NOT EXISTS bookings (
		id SERIAL PRIMARY KEY,
		customer_id VARCHAR(255) NOT NULL,
		salon_id INT NOT NULL,
		booking_date TIMESTAMP NOT NULL,
		status VARCHAR(50) DEFAULT 'pending',
		notes TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`

	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}

	// Router
	r := mux.NewRouter()
	r.HandleFunc("/health", healthCheck).Methods("GET")
	r.HandleFunc("/api/bookings", getBookings).Methods("GET")
	r.HandleFunc("/api/bookings/{id}", getBooking).Methods("GET")
	r.HandleFunc("/api/bookings", createBooking).Methods("POST")
	r.HandleFunc("/api/bookings/{id}", updateBooking).Methods("PUT")
	r.HandleFunc("/api/bookings/{id}", deleteBooking).Methods("DELETE")

	port_num := getEnv("PORT", "8081")
	fmt.Printf("Booking Service running on port %s\n", port_num)
	log.Fatal(http.ListenAndServe(":"+port_num, enableCORS(r)))
}

func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		
		next.ServeHTTP(w, r)
	})
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "Booking Service is running"})
}

func getBookings(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	rows, err := db.Query("SELECT id, customer_id, salon_id, booking_date, status, notes, created_at FROM bookings")
	if err != nil {
		json.NewEncoder(w).Encode(map[string]interface{}{"success": false, "error": err.Error()})
		return
	}
	defer rows.Close()

	bookings := []Booking{}
	for rows.Next() {
		var b Booking
		err := rows.Scan(&b.ID, &b.CustomerID, &b.SalonID, &b.BookingDate, &b.Status, &b.Notes, &b.CreatedAt)
		if err != nil {
			continue
		}
		bookings = append(bookings, b)
	}

	json.NewEncoder(w).Encode(map[string]interface{}{"success": true, "data": bookings})
}

func getBooking(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, _ := strconv.Atoi(params["id"])

	var b Booking
	err := db.QueryRow("SELECT id, customer_id, salon_id, booking_date, status, notes, created_at FROM bookings WHERE id=$1", id).
		Scan(&b.ID, &b.CustomerID, &b.SalonID, &b.BookingDate, &b.Status, &b.Notes, &b.CreatedAt)

	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{"success": false, "message": "Booking not found"})
		return
	}

	json.NewEncoder(w).Encode(map[string]interface{}{"success": true, "data": b})
}

func createBooking(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var b Booking
	json.NewDecoder(r.Body).Decode(&b)

	err := db.QueryRow(
		"INSERT INTO bookings (customer_id, salon_id, booking_date, status, notes) VALUES ($1, $2, $3, $4, $5) RETURNING id, created_at",
		b.CustomerID, b.SalonID, b.BookingDate, b.Status, b.Notes,
	).Scan(&b.ID, &b.CreatedAt)

	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{"success": false, "error": err.Error()})
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{"success": true, "data": b})
}

func updateBooking(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, _ := strconv.Atoi(params["id"])

	var b Booking
	json.NewDecoder(r.Body).Decode(&b)

	_, err := db.Exec(
		"UPDATE bookings SET customer_id=$1, salon_id=$2, booking_date=$3, status=$4, notes=$5 WHERE id=$6",
		b.CustomerID, b.SalonID, b.BookingDate, b.Status, b.Notes, id,
	)

	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{"success": false, "error": err.Error()})
		return
	}

	b.ID = id
	json.NewEncoder(w).Encode(map[string]interface{}{"success": true, "data": b})
}

func deleteBooking(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, _ := strconv.Atoi(params["id"])

	_, err := db.Exec("DELETE FROM bookings WHERE id=$1", id)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{"success": false, "error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(map[string]interface{}{"success": true, "message": "Booking deleted"})
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}