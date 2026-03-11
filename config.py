import os

class Config:
    # ==============================
    # BASIC SECURITY
    # ==============================
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    # ==============================
    # DATABASE CONFIG
    # ==============================
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Shrikant"
    MYSQL_DB = "rental_system"

    # ==============================
    # FILE UPLOAD SETTINGS
    # ==============================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # ==============================
    # UPI PAYMENT SETTINGS
    # ==============================
    UPI_ID = os.environ.get("UPI_ID", "proindietech@upi")
    UPI_NAME = os.environ.get("UPI_NAME", "Proindietech Rental")

    # Optional: If you add QR image
    UPI_QR_IMAGE = os.path.join("static", "images", "upi_qr.png")

    # Property Listing Fee
    PROPERTY_LISTING_FEE = 10   # ₹10 per property

    # ==============================
    # APP SETTINGS
    # ==============================
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"