# Trendy Ticket Service (TTS)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Razorpay](https://img.shields.io/badge/Razorpay-Payment-0C2451?style=for-the-badge&logo=razorpay&logoColor=white)
![SendGrid](https://img.shields.io/badge/SendGrid-Email-0099FF?style=for-the-badge&logo=sendgrid&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-Templates-B41717?style=for-the-badge&logo=jinja&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Markup-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styling-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Bcrypt](https://img.shields.io/badge/Bcrypt-Security-338033?style=for-the-badge&logo=letsencrypt&logoColor=white)

## 🎟️ Introducing Trendy Ticket Service — The Smarter Way to Manage Events & Tickets

**Trendy Ticket Service (TTS)** is a next-generation **SaaS-based Event & Ticket Management Platform** that empowers businesses, event organizers, and websites to seamlessly handle ticket sales, payments, and verification — all in one place.

With Trendy Ticket Service, any website can easily integrate our system using an **API Key** and **Event Token**. Once registered, you gain instant access to a secure, feature-rich event management dashboard designed to simplify every step of your ticketing process.

### 💡 How It Works

When a website connects to Trendy Ticket Service:

1. They receive a unique **API Key** upon signup and **Event Token** everytime they host a event.
2. Using these credentials, they can host events like weddings, birthdays, concerts, conferences, and more.
3. They can either process payments on their own website or redirect users to our secure payment gateway.
4. Our platform then handles ticket generation, delivery, and validation — ensuring a smooth experience for both organizers and attendees.

### ⚙️ Powerful Features

- ✅ **Complete Ticket Management** – Track total tickets sold, attendee details, and real-time analytics.
- ✅ **Secure Ticket Verification** – Prevent duplicate or reused tickets with one-time QR code scanning.
- ✅ **Smart Expiry System** – Set ticket validity and event expiry times to prevent misuse.
- ✅ **Attendance Insights** – Know who attended and who missed your event instantly.
- ✅ **Capacity Control** – Limit entries based on event size or ticket availability.
- ✅ **Seamless Integration** – Plug and play via API with minimal setup — perfect for developers and non-tech users alike.

### 🔒 Built for Security, Designed for Trust

Trendy Ticket Service ensures **100% secure transactions** and **authentic ticket validation**. Once a ticket is scanned and marked as attended, it can't be reused — giving event hosts complete control and peace of mind.

### 🚀 Why Choose Trendy Ticket Service?

- Simple integration for any website or platform
- Powerful admin dashboard for event analytics
- End-to-end automation — from payment to check-in
- Scalable, reliable, and secure infrastructure

Whether you're hosting a corporate event, a college fest, or a private celebration, **Trendy Ticket Service** handles it all — so you can focus on making your event unforgettable.

---

**🌐 Trendy Ticket Service — Simplify, Secure, and Scale Your Events.**

---

## 🚀 Features

### User Features
- **Secure Payment Processing**: Integrated with Razorpay for seamless payment transactions
- **Digital Ticket Generation**: Automatic ticket generation with QR codes after successful payment
- **Email Notifications**: Automated ticket id with ticket generation link will be sent to the user's email after successful payment.
- **OTP Verification**: Email-based OTP verification for secure transactions
- **Ticket Validation**: Users can verify and view their tickets using ticket IDs

### Admin Features
- **Admin Dashboard**: Comprehensive dashboard with event statistics and analytics
- **Event Management**: Create, host, and manage multiple events
- **Attendee Tracking**: View and manage event attendees
- **QR Code Scanner**: Real-time ticket verification via QR code scanning
- **Security Controls**: API key management and event token generation
- **Event Analytics**: Track active events, total attendees, and recent activities

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI 0.116.1
- **Database**: MongoDB (via Motor async driver)
- **Payment Gateway**: Razorpay
- **Email Service**: SendGrid
- **Template Engine**: Jinja2
- **Authentication**: Session-based with bcrypt password hashing
- **PDF Generation**: WeasyPrint (for ticket generation)
- **Security**: CORS middleware, HTTPOnly cookies, session management

## 📋 Prerequisites

- Python 3.8+
- MongoDB instance
- Razorpay account (API keys)
- SendGrid account (API key)

## 🔧 WEBSITE INTEGRATION

Integrate Trendy Ticket Service into your website with just a few lines of code. Our platform handles the entire payment and ticketing process seamlessly.

### Integration Steps

1. **Sign up** on Trendy Ticket Service to receive your unique **API Key**
2. **Host an event** to generate an **Event Token** for that specific event
3. **Add the payment script** to your website (see example below)
4. **Configure** your API Key and Event Token in the script
5. **Done!** All payments and ticket generation will be handled automatically

### Example Integration Code

Add this script to your website's payment page:

```html
<body>
  <h2>Send Amount to FastAPI</h2>

  <input type="number" id="amount" placeholder="Enter amount">
  <button onclick="sendPayment()">Send Payment</button>

  <script>
    async function sendPayment() {
      const amount = document.getElementById("amount").value;
      const token = "YOUR_EVENT_TOKEN"  // Replace with your Event Token
      const key = "YOUR_API_KEY"        // Replace with your API Key

      if (!amount || amount <= 0) {
        alert("Please enter a valid amount");
        return;
      }

      try {
        const response = await fetch("https://trendyticketservices.onrender.com/payment", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Accept": "application/json"  // ✅ This tells backend to return JSON
          },
          body: JSON.stringify({
            amount: parseFloat(amount),
            payment: true,  // true if you want payment processed on our website
            token: token,
            key: key
          }),
        });

        const data = await response.json();
        
        if (data.success && data.redirect_url) {
          // Navigate to the payment page
          window.location.href = "https://trendyticketservices.onrender.com" + data.redirect_url;
        } else {
          alert("Payment request failed. Please try again.");  
          // This message appears if your event token or API key is incorrect
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Payment request failed. Please try again.");
      }
    }
  </script>
</body>
```

### What Happens Next?

Once the user clicks the payment button:

1. **Validation** - Your API Key and Event Token are verified
2. **Redirect** - User is redirected to our secure payment gateway
3. **Payment** - User completes payment via Razorpay
4. **Ticket Generation** - Ticket is automatically generated with QR code
5. **Email Delivery** - Ticket ID and generation link are sent to the user's email
6. **Dashboard Update** - Attendee details appear in your admin dashboard

### API Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | float | Yes | Ticket price in INR |
| `payment` | boolean | Yes | Set to `true` to process payment on TTS platform |
| `token` | string | Yes | Your Event Token (unique per event) |
| `key` | string | Yes | Your API Key (unique per account) |

### Response Format

**Success Response:**
```json
{
  "success": true,
  "redirect_url": "/unique-payment-id"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Invalid key or token"
}
```

---

## 📁 Project Structure

```
TTS/
├── config/              # Configuration files
│   ├── objectsConfig.py
│   ├── otp_configs.py
│   ├── payment_config.py
│   └── ticketsDB.py
├── database/            # Database-related files
├── schemas/             # Pydantic schemas
│   ├── adminAuthSchemas.py
│   ├── adminDashboardSchemas.py
│   ├── emailSchemas.py
│   ├── paymentSchemas.py
│   ├── RedirectSchemas.py
│   └── ticketSchema.py
├── security/            # Security utilities
│   └── encrypyAmt.py
├── templates/           # HTML templates
│   ├── admin/          # Admin dashboard templates
│   ├── adminscanverification.html
│   ├── generate.html
│   ├── payments.html
│   ├── success.html
│   ├── tickets.html
│   ├── unsuccess.html
│   └── verification.html
├── utils/              # Utility functions
│   ├── adminGets.py
│   ├── adminPosts.py
│   ├── adminPuts.py
│   ├── general.py
│   ├── IST.py
│   ├── redirectCURD.py
│   ├── tickPost.py
│   └── trickGet.py
├── Tests/              # Test files
├── main.py             # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```


## 🔒 Security Features

- **Session Management**: Secure session handling with HTTPOnly cookies
- **Password Hashing**: Bcrypt for secure password storage
- **CORS Protection**: Configured CORS middleware
- **OTP Verification**: Email-based OTP for critical operations
- **Payment Signature Verification**: Razorpay signature validation
- **Token-based Event Access**: Secure event token generation and validation
- **Admin Authentication**: Cookie-based admin session management

## 💳 Payment Flow

1. User receives payment link with encrypted amount and event token
2. User enters payment details and completes OTP verification
3. Razorpay order is created
4. Payment is processed through Razorpay
5. Payment signature is verified
6. Ticket is generated and stored in MongoDB
7. Ticket is emailed to the user
8. User can view/download ticket using ticket ID

## 🎫 Ticket Verification Flow

1. Admin logs in and accesses the scanner page
2. Admin scans QR code on attendee's ticket
3. System validates ticket against event token
4. Ticket status is updated (attended/not attended)
5. Real-time verification result is displayed


## 🌐 Deployment

The application is deployed at: `https://trendyticketservices.onrender.com`

## 📄 License

This project is proprietary software. All rights reserved.

## 🎨 Frontend Technologies

- HTML5
- CSS3
- JavaScript (Vanilla)
- Jinja2 Templates
- Responsive Design

---

**Built with ❤️ using FastAPI**
