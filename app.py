from website import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting Dicto Flask app...")
    app.run(host="0.0.0.0", port=5005, debug=True)